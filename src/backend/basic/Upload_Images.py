
# PORT: http://localhost:5005/upload_images


from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import sys
import numpy as np
from collections import deque
sys.path.append(".")
from src.backend.Utils import image_2_base64
from src.backend.data.ImageManager import ImageManager


app = Flask(__name__)
CORS(app)

@app.route('/upload_images', methods=['POST'])
def upload_images():
    manager = ImageManager()
        
    files = request.files.getlist('images')
    valid_extensions = {'jpg', 'jpeg', 'png', 'gif'}

    index = 0
    config = {"temperature": 0, "hue": 0, "exposure": 0, "contrast": 0}
    first_image_base64 = None
    for file in files:
        file_extension = file.filename.split('.').pop().lower()
        if file_extension not in valid_extensions:
            continue
        
        img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_UNCHANGED)

        image_id = manager.get_next_image_id()

        if index == 0 and len(manager) == 0:
            first_image_base64 = image_2_base64(img)
        
        manager.add_image(image_id, img, config)
        index += 1

    manager.save_images()
    response = jsonify({'first_image': first_image_base64, "config": config})
    return response


if __name__ == '__main__':
    app.run(debug=False, port=5005, threaded=True)
