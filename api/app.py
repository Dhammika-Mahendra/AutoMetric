import os
import json
import pandas as pd
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from catboost import CatBoostRegressor

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
    and returns a single-row DataFrame with the 19 features the model expects.
    """
    # Parse the listing date  →  year / month / day
    date_str = params.get('date', datetime.today().strftime('%Y-%m-%d'))
    listing_date = pd.to_datetime(date_str)
    listing_year = listing_date.year
    listing_month = listing_date.month
    listing_day = listing_date.day

    yom = int(params['yom'])
    mileage = float(params['mileage'])
    engine_cc = float(params['engineCC'])

    car_age = listing_year - yom
    mileage_per_year = mileage / (car_age + 1)  # +1 to avoid division by zero

    # Map boolean / checkbox values to the labels the model was trained on
    def bool_to_label(val):
        """Convert 'true'/'false'/bool → 'Available'/'Not Available'"""
        if isinstance(val, bool):
            return 'Available' if val else 'Not Available'
        return 'Available' if str(val).lower() == 'true' else 'Not Available'

    leasing_val = params.get('leasing', False)
    leasing_label = 'Leasing' if str(leasing_val).lower() == 'true' else 'No Leasing'

    row = {
        'Brand':            params['brand'],
        'Model':            params['model'],
        'YOM':              yom,
        'Engine (cc)':      engine_cc,
        'Gear':             params['gear'],
        'Fuel Type':        params['fuelType'],
        'Millage(KM)':      mileage,
        'Town':             params['town'],
        'Leasing':          leasing_label,
        'Condition':        params.get('condition', 'USED'),
        'AIR CONDITION':    bool_to_label(params.get('airCondition', False)),
        'POWER STEERING':   bool_to_label(params.get('powerSteering', False)),
        'POWER MIRROR':     bool_to_label(params.get('powerMirror', False)),
        'POWER WINDOW':     bool_to_label(params.get('powerWindow', False)),
        'Listing_Year':     listing_year,
        'Listing_Month':    listing_month,
        'Listing_Day':      listing_day,
        'Car_Age':          car_age,
        'Mileage_Per_Year': mileage_per_year,
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
    Predict car price.

    Query parameters (all required unless noted):
        brand, model, yom, engineCC, gear, fuelType,
        mileage, town, date (YYYY-MM-DD), condition,
        leasing (true/false), airCondition (true/false),
        powerSteering (true/false), powerMirror (true/false),
        powerWindow (true/false)

    Returns:
        JSON  { predicted_price: <float>, price: <int> }
        predicted_price → raw model output (in ×10,000 LKR units)
        price           → human-readable price in LKR
    """
    try:
        params = request.args.to_dict()

        # Validate required fields
        required = ['brand', 'model', 'yom', 'engineCC', 'gear',
                     'fuelType', 'mileage', 'town']
        missing = [f for f in required if f not in params or not params[f]]
        if missing:
            return jsonify({
                'status': 'error',
                'message': f'Missing required parameters: {", ".join(missing)}'
            }), 400

        # Build feature row & predict
        features_df = build_features(params)
        prediction = model.predict(features_df)[0]

        # The model predicts in ×10,000 LKR units
        price_lkr = round(prediction * 10000)

        return jsonify({
            'status': 'success',
            'predicted_price': round(float(prediction), 2),
            'price': price_lkr,
            'currency': 'LKR'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
