
# PORT: http://localhost:5009/seg_human

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
sys.path.append(".")
from src.backend.right_side.S4.PP_HumanSeg.src.seghuman import seg_image, get_bg_img
from src.backend.data.ImageManager import ImageManager
from src.backend.Utils import image_2_base64

app = Flask(__name__)
CORS(app)

@app.route('/seg_human', methods=['POST'])
def seg_human():
    data = request.json
    seg_img_id = int(data['seg_img_id'])
    background_img_id = data['background_img_id']
    background_img = None
    if background_img_id is not None:
        background_img_id = int(background_img_id)
        background_img = manager.get_current_image(background_img_id)

    manager = ImageManager()

    seg_img = manager.get_current_image(seg_img_id)
    background_img = None
    if(background_img_id):
        background_img = manager.get_current_image(background_img_id)

    if background_img is not None and background_img.size > 0:
        adjusted_image = seg_image(seg_img, background_img)
    else:
        background_img = get_bg_img(None, seg_img.shape)
        adjusted_image = seg_image(seg_img, background_img)
    
    new_img_id = manager.get_next_image_id()
    manager.add_image(new_img_id, adjusted_image)
    manager.save_images()

    config = {"temperature": 0, "hue": 0, "exposure": 0, "contrast": 0, "sharpen": 0, "saturation": 0}
    img_base64 = image_2_base64(adjusted_image)

    return jsonify({"id": new_img_id, "src": img_base64, "config": config})

if __name__ == '__main__':
    app.run(debug=True, port=5009)
