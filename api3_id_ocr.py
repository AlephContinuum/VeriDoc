from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import pytesseract
import io
import re

app = Flask(__name__)
CORS(app)

def parse_id_data(text):
    """
    Parses raw text to extract structured data specific to ID documents.
    """
    data = {}
    
    # --- Passport and ID card fields ---
    
    # Name: Flexible regex to capture full name, often in all caps.
    name_match = re.search(r'Name[\s:]*([A-Z\s]+)', text, re.IGNORECASE)
    if name_match:
        data['full_name'] = name_match.group(1).strip()
    
    # Document Type: Identifies common document types.
    doc_type_match = re.search(r'(Passport|Aadhaar|PAN Card|College ID)', text, re.IGNORECASE)
    if doc_type_match:
        data['document_type'] = doc_type_match.group(1).strip()
    
    # Document Number: Looks for a common document number pattern (alphanumeric).
    doc_number_match = re.search(r'(Document No|ID No|No)[\s:]*([A-Z0-9]+)', text, re.IGNORECASE)
    if doc_number_match:
        data['document_number'] = doc_number_match.group(2).strip()

    # Date of Birth: Captures various date formats.
    dob_match = re.search(r'(?:Date of Birth|DOB)[\s:]*([\d\/-]+)', text, re.IGNORECASE)
    if dob_match:
        data['date_of_birth'] = dob_match.group(1).strip()
        
    # Gender: Looks for Male/Female.
    gender_match = re.search(r'Gender[\s:]*(Male|Female)', text, re.IGNORECASE)
    if gender_match:
        data['gender'] = gender_match.group(1).strip()
        
    # Expiry Date: Looks for an expiry date.
    expiry_match = re.search(r'(?:Expiry|Expires)[\s:]*([\d\/-]+)', text, re.IGNORECASE)
    if expiry_match:
        data['expiry_date'] = expiry_match.group(1).strip()

    return data

@app.route('/extract_id_data', methods=['POST'])
def extract_id_data():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        try:
            image = Image.open(io.BytesIO(file.read()))
            raw_text = pytesseract.image_to_string(image)
            parsed_data = parse_id_data(raw_text)
            return jsonify(parsed_data), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002) # Run on a new port