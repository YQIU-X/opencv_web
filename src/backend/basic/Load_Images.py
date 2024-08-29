
# PORT: http://localhost:5006/upload_images


from flask import Flask, jsonify
from flask_cors import CORS
import os
import pickle
import sys
sys.path.append(".")
from src.backend.Utils import image_2_base64, IMG_Get
from collections import deque


app = Flask(__name__)
CORS(app)

DATA_ROOT = ".\\src\\backend\\data"
PICKLE_FILE = os.path.join(DATA_ROOT, 'IMGs.pkl')

@app.route('/upload_images', methods=['POST'])
def upload_images():
    if os.path.exists(PICKLE_FILE):
        with open(PICKLE_FILE, 'rb') as f:
            IMGS = pickle.load(f)
    else:
        return jsonify({'error': 'No images found'}), 404

    images = []
    for image_id, IMG in IMGS.items():
        img = IMG_Get(IMG)
        img_base64 = image_2_base64(img)
        images.append({
            'id': image_id,
            'src': img_base64
        })
        

    return jsonify({'images': images})

if __name__ == '__main__':
    app.run(port=5006)
