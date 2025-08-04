from flask import Flask, request, jsonify
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import io


app = Flask(__name__)

# Load the TrOCR model and processor from Hugging Face
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-large-printed")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-large-printed")




@app.route('/extract_text', methods=['POST'])
def extract_text():
    # Check if a file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        try:
            # Read the image file and convert to PIL Image format
            image = Image.open(io.BytesIO(file.read())).convert("RGB")

            # Use TrOCR to get the text
            pixel_values = processor(images=image, return_tensors="pt").pixel_values
            generated_ids = model.generate(pixel_values)
            extracted_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

            return jsonify({'extracted_text': extracted_text}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        



if __name__ == '__main__':
    app.run(debug=True)

