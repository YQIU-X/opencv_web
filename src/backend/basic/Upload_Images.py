
# PORT: http://localhost:5005/upload_images


from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pickle
import cv2
import sys
import numpy as np
sys.path.append(".")
from src.backend.Utils import image_2_base64
from collections import deque


app = Flask(__name__)
CORS(app)

PICKLE_FILE = 'IMGs.pkl'
DATA_ROOT = ".\\src\\backend\\data"
PICKLE_FILE = os.path.join(DATA_ROOT, PICKLE_FILE)



@app.route('/upload_images', methods=['POST'])
def upload_images():
    if os.path.exists(PICKLE_FILE):
        with open(PICKLE_FILE, 'rb') as f:
            IMGS = pickle.load(f)
    else:
        IMGS = {}
        
    files = request.files.getlist('images')
    valid_extensions = {'jpg', 'jpeg', 'png', 'gif'}

    ids = []
    first_image_base64 = None
    for i, file in enumerate(files):
        file_extension = file.filename.split('.').pop().lower()
        if file_extension not in valid_extensions:
            return jsonify({'error': 'Invalid file format'}), 400

        img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_UNCHANGED)
        image_id = len(IMGS) + 1
        if i == 0 and len(IMGS) == 0:
            first_image_base64 = image_2_base64(img)

        dq = deque()
        dq.append(img)
        IMGS[image_id] = {
            "raw": img,
            "deque": dq,
            "config": {}
        }
        
        ids.append(image_id)

    with open(PICKLE_FILE, 'wb') as f:
        pickle.dump(IMGS, f)
    response = jsonify({'first_image': first_image_base64, 'image_ids': ids})
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5005)
