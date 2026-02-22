# AutoMetric - Car Price Prediction ML Application

A complete machine learning project demonstrating the full ML lifecycle from data to deployment. This project predicts car prices using a CatBoost regression model with an interactive web interface.

## 📋 Project Overview

This is a simple demonstration project showcasing how a machine learning model is built from raw data and deployed as a functional product. It includes:

- **Original dataset** for car price prediction
- **Trained CatBoost model** with metadata
- **Complete training pipeline** documented in Jupyter notebook
- **Flask REST API backend** for model serving
- **Interactive web frontend** for predictions
- **Ready to clone and run** from GitHub

## 🏗️ Project Structure

```
AutoMetric/
├── api/                          # Flask backend API
│   └── app.py                    # Main Flask application
├── app/                          # Frontend interface
│   ├── index.html                # Web UI
│   ├── index.css                 # Styling
│   └── index.js                  # Client-side logic
├── data/                         # Original datasets
│   └── car_price.csv             # Raw car pricing data
├── model/                        # Trained model artifacts
│   ├── car_price_catboost_model.cbm   # CatBoost model file
│   └── model_metadata.json       # Model configuration & metrics
├── scripts/                      # Training & development scripts
│   └── notebook.ipynb            # Step-by-step model development
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🎯 Features

- **Car Price Prediction**: Predicts car prices based on brand, model, engine size, mileage, and other features
- **CatBoost Model**: Uses state-of-the-art gradient boosting with categorical feature support
- **Feature Engineering**: Includes car age calculation and mileage binning
- **Web Interface**: User-friendly interface for making predictions
- **REST API**: Flask backend with CORS support for easy integration

## 📊 Model Performance

The trained CatBoost model achieves:
- **Test R² Score**: 0.915
- **Test RMSE**: 13.13
- **Training Strategy**: Stratified 70-15-15 split (Train-Val-Test)
- **Best Iteration**: 2176

### Model Features
- Brand (Categorical)
- Model (Categorical)
- Engine (cc) (Numerical)
- Gear (Categorical)
- Fuel Type (Categorical)
- Car_Age (Engineered: 2026 - YOM)
- Millage (Engineered: ceil(Millage_KM / 100))

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git (for cloning the repository)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Dhammika-Mahendra/AutoMetric.git
   cd AutoMetric
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**
   - **Windows (PowerShell)**:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - **Windows (Command Prompt)**:
     ```cmd
     .venv\Scripts\activate.bat
     ```
   - **macOS/Linux**:
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Running the Application

### 1. Start the Backend (Flask API)

Open a terminal in the project directory and run:

```bash
python api/app.py
```

The Flask server will start on `http://localhost:5000` (or the port specified in the console output).

### 2. Start the Frontend

Simply open the `app/index.html` file in your web browser:
- **Option 1**: Double-click the file
- **Option 2**: Right-click and select "Open with" → your preferred browser
- **Option 3**: Drag and drop into an open browser window

The web interface will connect to the backend API automatically.

## 🔧 API Endpoints

### Predict Car Price

GET /price

```

http://localhost:5000/price?brand=AUDI&model=A1&yom=2016&engineCC=990&gear=Automatic&fuelType=Petrol&mileage=99000


```

**Response:**
```json
{
  "currency": "LKR",
  "explainability": {
    "all_factors": [ ],
    "base_price": 5329350,
    "reasons": [],
    "top_factors": []
  },
  "predicted_price": 20.85,
  "price": 2085341,
  "status": "success"
}
```

## 📓 Exploring the Model Development

To understand how the model was built and trained:

1. **Open the Jupyter Notebook**: `scripts/notebook.ipynb`
2. This notebook contains:
   - Data exploration and preprocessing
   - Feature engineering steps
   - Model training and hyperparameter tuning
   - Performance evaluation
   - Model export

### Running the Notebook

Ensure you have Jupyter installed:
```bash
pip install jupyter ipykernel
```

Launch Jupyter:
```bash
jupyter notebook scripts/notebook.ipynb
```

## 🔄 Retraining the Model

To modify or retrain the model:

1. Open `scripts/notebook.ipynb`
2. Modify the data preprocessing, feature engineering, or model parameters
3. Re-run the training cells
4. Export the new model to the `model/` directory
5. Update `model_metadata.json` with new metrics
6. Restart the Flask API to use the updated model

## 📦 Dependencies

Key libraries used:
- **Flask**: Web framework for API
- **Flask-CORS**: Cross-origin resource sharing
- **CatBoost**: Gradient boosting model
- **Pandas**: Data manipulation
- **NumPy**: Numerical computing
- **Scikit-learn**: ML utilities
- **Matplotlib/Seaborn**: Visualization
- **SHAP**: Model interpretability

See `requirements.txt` for the complete list.

## 🤝 Contributing

This is a demonstration project. Feel free to:
- Clone and experiment with the model
- Improve the frontend interface
- Add new features or endpoints
- Optimize model performance
- Report issues or suggestions


