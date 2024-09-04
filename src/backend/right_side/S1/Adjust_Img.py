
# PORT: http://localhost:5000/adjust_image

from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import sys
sys.path.append(".")
from src.backend.Utils import image_2_base64
from src.backend.data.ImageManager import ImageManager
from src.backend.right_side.S1.Apply_Config import Apply_Config

app = Flask(__name__)
CORS(app)


@app.route('/adjust_image', methods=['POST'])
def adjust_image():
    data = request.json

    temperature = int(data.get('temperature', 0))
    hue = int(data.get('hue', 0))
    exposure = int(data.get('exposure', 0))
    contrast = int(data.get('contrast', 0))
    sharpen = int(data.get('sharpen', 0))
    saturation = int(data.get('saturation', 0))
    image_id = data.get('image_id')
    manager = ImageManager()

    img, _ = manager.get_last_image(image_id)
    config = {"temperature": temperature, "hue": hue, "exposure": exposure, "contrast": contrast, "sharpen": sharpen, "saturation": saturation}
    manager.forward_image(image_id, img, config)  # 存图

    if img is None:
        print("image is None")
        return jsonify({'error': 'Failed to decode image'}), 400

    img = Apply_Config(img, config)
    
    manager.set_current_image(image_id, img)  # 设当前图

    encoded_image = image_2_base64(img)

    manager.save_images()  # 存文件
    return jsonify({"id": image_id, "src": encoded_image, "config": config})

if __name__ == '__main__':
    app.run(debug=False, port=5000, threaded=True)
