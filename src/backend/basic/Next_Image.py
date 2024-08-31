
# PORT: http://localhost:5007/next_image

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
sys.path.append(".")
from src.backend.data.ImageManager import ImageManager
from src.backend.Utils import image_2_base64

app = Flask(__name__)
CORS(app)

@app.route('/next_image', methods=['POST'])
def next_image():
    data = request.get_json()
    image_id = int(data['id'])
    manager = ImageManager()
    img, next_id = manager.get_next_image(image_id)
    img_base64 = image_2_base64(img)
    _, config = manager.get_last_image(next_id)
    return jsonify({"id": next_id, "src": img_base64, "config": config})


if __name__ == '__main__':
    app.run(debug=False, port=5007, threaded=True)

