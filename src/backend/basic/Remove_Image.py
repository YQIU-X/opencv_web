
# PORT: http://localhost:5002/remove_images

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
sys.path.append(".")
from src.backend.data.ImageManager import ImageManager

app = Flask(__name__)
CORS(app)

@app.route('/remove_image', methods=['POST'])
def remove_image():
    data = request.get_json()
    image_id = int(data['id'])
    print(image_id)
    manager = ImageManager()
    manager.delete_image(image_id)
    manager.save_images()

    return jsonify({"message": "Image removed successfully", "image_id": image_id})

if __name__ == '__main__':
    app.run(debug=False, port=5002, threaded=True)

