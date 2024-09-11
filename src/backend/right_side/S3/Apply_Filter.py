from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import os
import sys
sys.path.append(".")
from src.backend.Utils import image_2_base64
from src.backend.data.ImageManager import ImageManager


app = Flask(__name__)
CORS(app)

def apply_emboss_effect(img):
    base_kernel = np.array([[0,-1,-1],[1,0,-1],[1,1,0]])

    def generate_kernel(base_kernel, size):
        base_size = base_kernel.shape[0]
        if size <= base_size:
            return base_kernel

        kernel = np.copy(base_kernel)
        while kernel.shape[0] < size:
            kernel = np.pad(kernel, ((1, 1), (1, 1)), 'edge')
        
        return kernel

    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    filter_size = 3
    current_kernel = generate_kernel(base_kernel, filter_size)

    output = cv2.filter2D(gray_img, -1, current_kernel) + 128
    return output



def sketch_pencil(image):
    _, sketch = cv2.pencilSketch(image, sigma_s=60, sigma_r=0.07, shade_factor=0.05)
    return sketch

def stylization(image):
    result = cv2.stylization(image, sigma_s=50, sigma_r=0.6)
    return result


def filter(img, filter):
    if filter == 'relief':
        return apply_emboss_effect(img)
    elif filter == 'grayscale':
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    elif filter == 'pencil':
        return sketch_pencil(img)
    elif filter == 'stylization':
        return stylization(img)
    else:
        return img
    

@app.route('/apply_filter', methods=['POST'])
def apply_filter():
    data = request.json
    image_id = data.get('image_id')
    filter_name = data.get('filter')

    manager = ImageManager()
    currentImg = manager.get_current_image(image_id)
    config = {"temperature": 0, "hue": 0, "exposure": 0, "contrast": 0, "sharpen": 0, "saturation": 0}

    img = filter(currentImg, filter_name)
    
    manager.forward_image(image_id, img, config)
    manager.set_current_image(image_id, img)
    manager.save_images()
    encoded_image = image_2_base64(img)

    return jsonify({"id": image_id, "src": encoded_image, "config": config})

if __name__ == '__main__':
    app.run(debug=False, port=5015, threaded=True)
