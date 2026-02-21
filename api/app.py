from flask import Flask, jsonify

app = Flask(__name__)


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
        'api_version': '1.0.0'
    })


@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint - returns sample data."""
    return jsonify({
        'message': 'GET request successful',
        'data': {
            'id': 1,
            'name': 'Sample Item',
            'description': 'This is a test response'
        }
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
