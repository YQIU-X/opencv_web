from flask import Flask, request, jsonify
import cv2
import numpy as np
import base64
from io import BytesIO
from flask_cors import CORS
import sys
sys.path.append(".\\src\\backend\\PP-HumanSeg\\src")
from seghuman import seg_image

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

def base64_to_image(base64_string):
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]

    img_data = base64.b64decode(base64_string)
    nparr = np.frombuffer(img_data, np.uint8)

    if nparr.size == 0:
        print("Failed to convert base64 to image array")
        return None

    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        print("Failed to decode image")

    return img

@app.route('/adjust_image', methods=['POST'])
def adjust_image():
    # Get the image and settings from the request
    data = request.json
    base64_image = data.get('image')

    if not base64_image:
        return jsonify({'error': 'No image data provided'}), 400

    # Decode the base64 encoded image
    image = base64_to_image(base64_image)

    if image is None:
        return jsonify({'error': 'Failed to decode image'}), 400

    # Adjust the image properties
    adjusted_image = seg_image(image, None)

    # Encode the adjusted image to base64
    _, buffer = cv2.imencode('.jpg', adjusted_image)
    if not _:
        return jsonify({'error': 'Failed to encode image'}), 500

    encoded_image = base64.b64encode(buffer).decode('utf-8')
    return jsonify({'image': encoded_image})

if __name__ == '__main__':
    app.run(debug=True, port=5003)
