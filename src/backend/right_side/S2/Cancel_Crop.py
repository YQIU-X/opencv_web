from flask import Flask, request, jsonify
import os
from flask_cors import CORS
import sys
sys.path.append(".")
from src.backend.Utils import image_2_base64
from src.backend.data.ImageManager import ImageManager

app = Flask(__name__)
CORS(app)

# 配置常量
DATA_ROOT = ".\\src\\backend\\data"
POINTS_NAME = 'points.json'
POINTS_FILE = os.path.join(DATA_ROOT, POINTS_NAME)


@app.route('/cancel_crop', methods=['POST'])
def cancel_crop():
    data = request.json
    image_id = data.get('id')
    current_operation = data.get('currentOperation')

    if os.path.exists(POINTS_FILE):
        os.remove(POINTS_FILE)
        print(f"{POINTS_FILE} has been deleted.")
    else:
        print(f"{POINTS_FILE} does not exist.")

    manager = ImageManager()
    current_image = manager.get_current_image(image_id)
    _, config = manager.get_last_image(image_id)
    manager.set_current_image(image_id, current_image)

    encoded_image = image_2_base64(current_image)
    return jsonify({"id": image_id, "src": encoded_image, "config": config})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True)
