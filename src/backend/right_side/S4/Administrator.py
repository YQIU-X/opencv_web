from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
sys.path.append(".")
from src.backend.right_side.S4.PP_HumanSeg.src.seghuman import seg_image, get_bg_img
from src.backend.data.ImageManager import ImageManager
from src.backend.Utils import image_2_base64
from src.backend.right_side.S4.Image_Stitch import stitch_images
from src.backend.right_side.S4.Histogram_Equalization import equalize_rgb_histogram
from src.backend.right_side.S4.PP_HumanSeg.src.seghuman import seg_image, get_bg_img
from src.backend.right_side.S4.Identification import create_id_photo, calculate_background_color
import numpy as np

app = Flask(__name__)
CORS(app)



@app.route('/administrator', methods=['POST'])
def administrator():
    data = request.get_json()

    imageId_1 = data.get('Image1')
    imageId_2 = data.get('Image2')

    manager = ImageManager()
    current_image_1 = None

    if imageId_1 is not None:
        imageId_1 = int(data['Image1'])
        current_image_1 = manager.get_current_image(imageId_1)
    if imageId_2 is not None:
        imageId_2 = int(data['Image2'])
        current_image_2 = manager.get_current_image(imageId_2)

    operation = data['operation']
    
    config = {"temperature": 0, "hue": 0, "exposure": 0, "contrast": 0, "sharpen": 0, "saturation": 0}


    if operation == 'image-stitch':
        image_src = stitch_images(current_image_2, current_image_1)
    elif operation == 'histogram-equalization':
        print(operation)
        image_src = equalize_rgb_histogram(current_image_1)
    elif operation == 'Identification-photo-production':
        height, width, channels = current_image_1.shape
        blue_color = calculate_background_color(current_image_1)
        background_img = np.full((height, width, channels), blue_color, dtype=np.uint8)
        
        image_src = seg_image(current_image_1, background_img)
        image_src = create_id_photo(image_src)

    

    img_base64 = image_2_base64(image_src)
    new_img_id = manager.get_next_image_id()
    manager.add_image(new_img_id, image_src, config)
    manager.save_images()

    return jsonify({"id": new_img_id, "src": img_base64, "config": config})

if __name__ == '__main__':
    app.run(debug=False, port=5013, threaded=True)