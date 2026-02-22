import os
import json
import pandas as pd
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from catboost import CatBoostRegressor, Pool
import numpy as np

app = Flask(__name__)
CORS(app)

# ── Load model and metadata at startup ──────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'car_price_catboost_model.cbm')
METADATA_PATH = os.path.join(BASE_DIR, 'model', 'model_metadata.json')

# Load CatBoost model
model = CatBoostRegressor()
model.load_model(MODEL_PATH)

# Load metadata (feature names, categorical indices, etc.)
with open(METADATA_PATH, 'r') as f:
    metadata = json.load(f)

FEATURE_NAMES = metadata['feature_names']
CAT_FEATURE_INDICES = metadata['categorical_feature_indices']

print(f"✅ Model loaded from {MODEL_PATH}")
print(f"✅ Features expected: {FEATURE_NAMES}")


# ── Helper: build a feature DataFrame from request params ───────────────
def build_features(params: dict) -> pd.DataFrame:
    """
    Accepts the raw request parameters (from query-string or JSON body)
    and returns a single-row DataFrame with the features the model expects.
    Only uses: Brand, Model, YOM, Engine (cc), Gear, Fuel Type, Millage(KM)
    """
    yom = int(params['yom'])
    mileage = float(params['mileage'])
    engine_cc = float(params['engineCC'])

    row = {
        'Brand':            params['brand'],
        'Model':            params['model'],
        'YOM':              yom,
        'Engine (cc)':      engine_cc,
        'Gear':             params['gear'],
        'Fuel Type':        params['fuelType'],
        'Millage(KM)':      mileage,
    }

    # Return a DataFrame with columns in exactly the order the model expects
    return pd.DataFrame([row], columns=FEATURE_NAMES)


# ── Routes ──────────────────────────────────────────────────────────────
@app.route('/', methods=['GET'])
def home():
    """Home endpoint - returns a welcome message."""
    return jsonify({
        'message': 'Welcome to AutoMetric API',
        'status': 'success'
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint - returns API status."""
    return jsonify({
        'status': 'healthy',
        'api_version': '1.0.0',
        'model_loaded': True,
        'features': FEATURE_NAMES
    })


@app.route('/price', methods=['GET'])
def predict_price():
    """
    Predict car price with explainability.

    Query parameters (all required):
        brand, model, yom, engineCC, gear, fuelType, mileage

    Returns:
        JSON with:
        - predicted_price  → raw model output (in ×100,000 LKR units)
        - price            → human-readable price in LKR
        - explainability   → SHAP-based breakdown with:
            • base_price   → average model prediction (LKR)
            • top_factors  → top 5 features by impact
            • all_factors  → all features sorted by impact
            • reasons      → human-readable explanation strings
    """
    try:
        params = request.args.to_dict()

        # Validate required fields
        required = ['brand', 'model', 'yom', 'engineCC', 'gear',
                     'fuelType', 'mileage']
        missing = [f for f in required if f not in params or not params[f]]
        if missing:
            return jsonify({
                'status': 'error',
                'message': f'Missing required parameters: {", ".join(missing)}'
            }), 400

        # Build feature row & predict
        features_df = build_features(params)
        prediction = model.predict(features_df)[0]

        # The model predicts in ×100,000 LKR units
        price_lkr = round(prediction * 100000)

        # ── Explainability: per-prediction SHAP values ──────────────
        pool = Pool(features_df, cat_features=CAT_FEATURE_INDICES)
        shap_raw = model.get_feature_importance(
            type='ShapValues', data=pool
        )[0]
        shap_vals = shap_raw[:-1]          # per-feature SHAP values
        base_value = float(shap_raw[-1])   # expected (average) prediction

        # Convert raw SHAP into user-friendly impact scores
        abs_shap = np.abs(shap_vals)
        total_abs = abs_shap.sum() if abs_shap.sum() > 0 else 1.0

        factors = []
        for name, val, a in zip(FEATURE_NAMES, shap_vals, abs_shap):
            direction = 'increases' if val > 0 else 'decreases' if val < 0 else 'neutral'
            factors.append({
                'feature': name,
                'value': str(features_df[name].iloc[0]),
                'direction': direction,
                'impact_pct': round(float(a / total_abs) * 100, 1),
                'price_effect': round(float(val) * 100000),
            })
        # Most influential first
        factors.sort(key=lambda f: abs(f['price_effect']), reverse=True)

        # Top-5 human-readable reasons
        reasons = []
        for f in factors[:5]:
            verb = f['direction']
            reasons.append(
                f"{f['feature']} ({f['value']}) {verb} the price "
                f"by ~Rs. {abs(f['price_effect']):,} "
                f"({f['impact_pct']}% importance)"
            )

        return jsonify({
            'status': 'success',
            'predicted_price': round(float(prediction), 2),
            'price': price_lkr,
            'currency': 'LKR',
            'explainability': {
                'base_price': round(base_value * 100000),
                'top_factors': factors[:5],
                'all_factors': factors,
                'reasons': reasons
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
