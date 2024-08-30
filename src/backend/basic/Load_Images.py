
# PORT: http://localhost:5006/load_images


from flask import Flask, jsonify
from flask_cors import CORS
import os
import pickle
import sys
sys.path.append(".")
from src.backend.Utils import image_2_base64
from src.backend.data.ImageManager import ImageManager

app = Flask(__name__)
CORS(app)

@app.route('/load_images', methods=['POST'])
def load_images():
    manager = ImageManager()

    images = []

    for image_id, _ in manager:
        img = manager.get_current_image(image_id)
        _, config = manager.get_last_image(image_id)
        img_base64 = image_2_base64(img)
        images.append({
            'id': image_id,
            'img64': img_base64,
            'config': config
        })

    return jsonify({'images': images})

if __name__ == '__main__':
    app.run(debug=False, port=5006, threaded=True)
