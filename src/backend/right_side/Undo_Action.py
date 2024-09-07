
# http://localhost:5004/undo_action

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
sys.path.append(".")
from src.backend.data.ImageManager import ImageManager
from src.backend.Utils import image_2_base64
from src.backend.right_side.S1.Apply_Config import Apply_Config

app = Flask(__name__)
CORS(app)

@app.route('/undo_action', methods=['POST'])
def undo_action():
    data = request.get_json()
    image_id = int(data['id'])
    print("undo_action")
    manager = ImageManager()

    img, config = manager.back_image(image_id)
    print(len(manager.data[1]['deque']))

    current_image = Apply_Config(img, config)
    manager.set_current_image(image_id, current_image)
    img_base64 = image_2_base64(current_image)
    
    manager.save_images()

    return jsonify({"id": image_id, "src": img_base64, "config": config})


if __name__ == '__main__':
    app.run(debug=False, port=5004, threaded=True)