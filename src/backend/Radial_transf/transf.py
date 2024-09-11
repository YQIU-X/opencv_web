import cv2
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
sys.path.append(".")
from src.backend.data.ImageManager import ImageManager
from src.backend.Utils import image_2_base64

app = Flask(__name__)
CORS(app)

def make_background_transparent(image, bg_color=(0, 0, 0)):
    # 将图像从 BGR 转换为 RGBA
    image_rgba = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

    # 找到与背景颜色匹配的区域
    mask = cv2.inRange(image[:, :, :3], np.array(bg_color), np.array(bg_color))

    # 将匹配的区域的 Alpha 通道设置为 0
    image_rgba[mask == 255, 3] = 0

    return image_rgba

@app.route('/Radial_transf', methods=['POST'])
def Radial_transf():
    data = request.get_json()

    print("Received data:", data)
    image_id = data.get('id')
    top_left = data.get('topLeft', {})
    top_right = data.get('topRight', {})
    bottom_left = data.get('bottomLeft', {})
    bottom_right = data.get('bottomRight', {})
    orign_top_left = data.get('orignTopLeft', {})
    orign_top_right = data.get('orignTopRight', {})
    orign_bottom_left = data.get('orignBottomLeft', {})
    orign_bottom_right = data.get('orignBottomRight', {})

    # 验证所有点是否具有 'x' 和 'y'
    for point in [orign_top_left, orign_top_right, orign_bottom_left, orign_bottom_right]:
        if 'x' not in point or 'y' not in point:
            return jsonify({"error": "Invalid vertex data: missing 'x' or 'y' in origin points"}), 400

    for point in [top_left, top_right, bottom_left, bottom_right]:
        if 'x' not in point or 'y' not in point:
            return jsonify({"error": "Invalid vertex data: missing 'x' or 'y' in destination points"}), 400

    manager = ImageManager()
    current_image = manager.get_current_image(image_id)

    pts1 = np.float32([
        [orign_top_left['x'], orign_top_left['y']],
        [orign_top_right['x'], orign_top_right['y']],
        [orign_bottom_left['x'], orign_bottom_left['y']],
        [orign_bottom_right['x'], orign_bottom_right['y']]
    ])

    pts2 = np.float32([
        [top_left['x'], top_left['y']],
        [top_right['x'], top_right['y']],
        [bottom_left['x'], bottom_left['y']],
        [bottom_right['x'], bottom_right['y']]
    ])


    matrix = cv2.getPerspectiveTransform(pts1, pts2)

    new_corners = cv2.perspectiveTransform(np.array([pts1]), matrix)[0]

    x, y, new_width, new_height = cv2.boundingRect(new_corners)

    translation_matrix = np.array([[1, 0, -x], [0, 1, -y], [0, 0, 1]])
    adjusted_matrix = np.dot(translation_matrix, matrix)

    transformed_image = cv2.warpPerspective(current_image, adjusted_matrix, (new_width, new_height))

    # 将背景部分转换为透明
    transformed_image_with_transparency = make_background_transparent(transformed_image)
    cv2.imwrite('transformed_image_with_transparency.png',transformed_image_with_transparency)
    encoded_image = image_2_base64(transformed_image_with_transparency)

    new_top_left = [new_corners[0][0] - x, new_corners[0][1] - y]
    new_top_right = [new_corners[1][0] - x, new_corners[1][1] - y]
    new_bottom_left = [new_corners[2][0] - x, new_corners[2][1] - y]
    new_bottom_right = [new_corners[3][0] - x, new_corners[3][1] - y]

    response = {
        'img': encoded_image,
        'width': new_width,
        'height': new_height,
        'newTopLeft': new_top_left,
        'newTopRight': new_top_right,
        'newBottomLeft': new_bottom_left,
        'newBottomRight': new_bottom_right
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=False, port=5016, threaded=True)
