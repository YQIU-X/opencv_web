from flask import Flask, request, jsonify
import cv2
import os
import numpy as np
import json
import base64
from flask_cors import CORS
import sys
sys.path.append(".")
from src.backend.Utils import image_2_base64, base64_2_image
from src.backend.data.ImageManager import ImageManager
from src.backend.right_side.S1.Apply_Config import Apply_Config


app = Flask(__name__)
CORS(app)


DATA_ROOT = "./src/backend/data"
POINTS_NAME = 'points.json'
POINTS_FILE = os.path.join(DATA_ROOT, POINTS_NAME)

def extract_region(img, points):
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    points = np.array(points, dtype=np.int32)
    cv2.fillPoly(mask, [points], 255)
    extracted = cv2.bitwise_and(img, img, mask=mask)
    x, y, w, h = cv2.boundingRect(points)
    roi = extracted[y:y+h, x:x+w]
    return roi

def read_points():
    if os.path.exists(POINTS_FILE):
        with open(POINTS_FILE, 'r') as file:
            points_list = json.load(file)
            return [tuple(point) for point in points_list]
    return []

TEMP_NAME = 'temp.pkl'
DATA_ROOT = ".\\src\\backend\\data"

TEMP_FILE = os.path.join(DATA_ROOT, TEMP_NAME)

import pickle


def load_image():
    if os.path.exists(TEMP_FILE):
        with open(TEMP_FILE, 'rb') as f:
            img = pickle.load(f)
            return img


@app.route('/apply_Crop', methods=['POST'])
def apply_crop():
    data = request.json
    image_id = data.get('id')

    image = load_image()
    points = read_points()

    manager = ImageManager()
    _, config = manager.get_last_image(image_id)
    result_img = extract_region(image, points)
    current_img = Apply_Config(result_img, config)

    manager.set_current_image(image_id, current_img)
    manager.forward_image(image_id, current_img, config)
    manager.save_images()
    encoded_image = image_2_base64(current_img)

    if os.path.exists(POINTS_FILE):
        os.remove(POINTS_FILE)
        print(f"{POINTS_FILE} has been deleted.")
    else:
        print(f"{POINTS_FILE} does not exist.")

    return jsonify({"id": image_id, "src": encoded_image, "config": config})


if __name__ == '__main__':
    app.run(debug=False, port=5011, threaded=True)
