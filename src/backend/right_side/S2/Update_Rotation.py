import cv2
import numpy as np
from flask import Flask, request, jsonify
import sys
sys.path.append(".")
from src.backend.Utils import image_2_base64
from src.backend.data.ImageManager import ImageManager
from src.backend.right_side.S1.Apply_Config import Apply_Config
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def rotate_image(image, angle):
    """
    Rotate the given image by the specified angle and return the rotated image.
    """
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)

    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    rotated_image = cv2.warpAffine(image, rotation_matrix, (w, h))

    return rotated_image

@app.route('/update_rotation', methods=['POST'])
def update_rotation():
    data = request.json
    image_id = data.get('id')
    angle = data.get('angle')

    manager = ImageManager()
    print(666666666666666666666)
    current_image = manager.get_current_image(image_id)

    rotated_image = rotate_image(current_image, angle)
    img_base64 = image_2_base64(rotated_image)
    _, config = manager.get_last_image(image_id)

    return jsonify({"id": image_id, "src": img_base64, "config": config})


if __name__ == '__main__':
    app.run(debug=False, port=5012, threaded=True)
