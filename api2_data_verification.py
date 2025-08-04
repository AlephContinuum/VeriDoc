from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)


app = Flask(__name__)
CORS(app)


@app.route('/verify_data', methods=['POST'])
def verify_data():
    # The API receives submitted form data and the extracted data from the first API.
    request_data = request.json
    if not request_data:
        return jsonify({'error': 'No JSON data received'}), 400

    submitted_data = request_data.get('submitted_data')
    original_data = request_data.get('original_data')

    if not submitted_data or not original_data:
        return jsonify({'error': 'Missing submitted_data or original_data'}), 400

    verification_results = {}

    # Iterate through each field in the submitted data
    for key, submitted_value in submitted_data.items():
        original_value = original_data.get(key)

        # Simple comparison logic (case-insensitive and whitespace-stripped)
        is_match = str(submitted_value).strip().lower() == str(original_value).strip().lower()

        verification_results[key] = {
            'submitted_value': submitted_value,
            'original_value': original_value,
            'match_status': 'Match' if is_match else 'Mismatch',
            'confidence_score': 1.0 if is_match else 0.0
        }

    return jsonify(verification_results), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001) # Run on a different port to avoid conflict