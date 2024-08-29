from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64

app = Flask(__name__)
CORS(app)  # 启用 CORS，允许来自所有来源的请求


@app.route('/click_coordinates', methods=['POST'])
def click_coordinates():
    data = request.json
    x = data.get('x')
    y = data.get('y')
    print(x)
    print(y)
    return jsonify({"status": "success", "x": x, "y": y})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
