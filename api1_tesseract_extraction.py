from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import pytesseract
import io
import re
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import torch
import numpy as np
import cv2

# Load the TrOCR handwritten model and processor once at startup.
# This model is specifically trained for handwritten text.
# The model will be downloaded automatically the first time this code runs.
try:
    processor_handwritten = TrOCRProcessor.from_pretrained("microsoft/trocr-large-handwritten")
    model_handwritten = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-large-handwritten")
except Exception as e:
    print(f"Error loading TrOCR model: {e}")
    processor_handwritten = None
    model_handwritten = None

app = Flask(__name__)
CORS(app)

def parse_extracted_data(text):
    """
    Parses a raw text string to extract structured data using regular expressions.
    This function is now more robust to handle output from both Tesseract and TrOCR.
    """
    data = {}
    
    # --- General fields ---
    # The regex patterns are designed to be flexible for various document types.
    
    # Name: Finds "Name" and captures the text that follows.
    name_match = re.search(r'(?:Name|Full Name)[:\s]*(.*?)(?:\n|$)', text, re.IGNORECASE)
    if name_match:
        data['name'] = name_match.group(1).strip()
        
    # Age: Finds "Age" and captures the numbers that follow.
    age_match = re.search(r'Age[:\s]*(\d{1,3})', text, re.IGNORECASE)
    if age_match:
        data['age'] = age_match.group(1).strip()

    # Gender: Finds "Gender" and captures a word like "Male" or "Female".
    gender_match = re.search(r'Gender[:\s]*(Male|Female)', text, re.IGNORECASE)
    if gender_match:
        data['gender'] = gender_match.group(1).strip()

    # Date of Birth: Finds "Date of Birth" and captures a date format.
    dob_match = re.search(r'(?:Date of Birth|DOB)[:\s]*([\d\/-]+)', text, re.IGNORECASE)
    if dob_match:
        data['date_of_birth'] = dob_match.group(1).strip()
        
    # Phone number: Finds "Phone" and captures a common phone number pattern.
    phone_match = re.search(r'(?:Phone|Phone number)[:\s]*([\d\s\-\+\(\)]+)', text, re.IGNORECASE)
    if phone_match:
        data['phone_number'] = phone_match.group(1).strip()
        
    # Email: Finds "Email" and captures a standard email address.
    email_match = re.search(r'(?:Email|Email Id)[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text, re.IGNORECASE)
    if email_match:
        data['email'] = email_match.group(1).strip()
        
    # Address: Finds "Address" and captures the rest of the line or paragraph.
    address_match = re.search(r'Address[:\s]*(.*?)(?:\n\n|$)', text, re.IGNORECASE | re.DOTALL)
    if address_match:
        data['address'] = re.sub(r'\s+', ' ', address_match.group(1)).strip()

    # --- Specific fields from the British Council form ---
    first_name_match = re.search(r'First name\s+([A-Z]+)', text, re.IGNORECASE)
    if first_name_match:
        data['first_name'] = first_name_match.group(1).strip()
    last_name_match = re.search(r'Last name\s+([A-Z-]+)', text, re.IGNORECASE)
    if last_name_match:
        data['last_name'] = last_name_match.group(1).strip()
        
    return data

@app.route('/extract_text', methods=['POST'])
def extract_text():
    """
    API endpoint for extracting text from printed documents using Tesseract.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        try:
            image = Image.open(io.BytesIO(file.read()))
            # Use pytesseract for printed text
            raw_text = pytesseract.image_to_string(image)
            parsed_data = parse_extracted_data(raw_text)
            return jsonify(parsed_data), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/extract_handwritten_text', methods=['POST'])
def extract_handwritten_text():
    """
    API endpoint for extracting text from handwritten documents using TrOCR.
    Includes image pre-processing for better accuracy.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        try:
            image_stream = io.BytesIO(file.read())
            image_pil = Image.open(image_stream).convert("RGB")

            # Convert PIL image to an OpenCV format for pre-processing
            image_cv = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
            
            # Use adaptive thresholding to create a clean black and white image.
            # This is more effective than simple thresholding for uneven backgrounds.
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
            
            # Convert the pre-processed image back to PIL format
            processed_image_pil = Image.fromarray(cv2.cvtColor(thresh, cv2.COLOR_BGR2RGB))
            
            # Use TrOCR for handwritten text on the cleaned image
            pixel_values = processor_handwritten(images=processed_image_pil, return_tensors="pt").pixel_values
            generated_ids = model_handwritten.generate(pixel_values)
            raw_text = processor_handwritten.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            # For debugging purposes
            print(f"TrOCR Raw Text Output: {raw_text}")
            
            parsed_data = parse_extracted_data(raw_text)
            
            return jsonify(parsed_data), 200
        except Exception as e:
            print(f"Error in handwritten extraction: {e}")
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
    
