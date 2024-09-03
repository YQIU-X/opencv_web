from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import sys
sys.path.append(".")
from src.backend.Utils import image_2_base64
from src.backend.data.ImageManager import ImageManager

app = Flask(__name__)
CORS(app)

def draw_dashed_line(img, pt1, pt2, color, thickness, dash_length):
    # 计算向量
    line_vector = np.array(pt2) - np.array(pt1)
    line_length = np.linalg.norm(line_vector)
    line_direction = line_vector / line_length

    # 绘制虚线
    for i in np.arange(0, line_length, dash_length*2):
        start_point = pt1 + line_direction * i
        end_point = pt1 + line_direction * min(i + dash_length, line_length)
        cv2.line(img, tuple(start_point.astype(int)), tuple(end_point.astype(int)), color, thickness)

def draw_lines(img, points):
    if len(points) == 1:
        # 如果只有一个点，在图像上标记这个点
        point = points[0]
        cv2.circle(img, point, radius=5, color=(80, 180, 100), thickness=-1)  # 绘制一个小圆圈
    elif len(points) > 1:
        for i in range(len(points)):

            # 标记每个点
            cv2.circle(img, points[i], radius=5, color=(80, 180, 100), thickness=-1)
            
            if i < len(points) - 1:
                # 在相邻的点之间绘制线条
                point1 = points[i]
                point2 = points[i + 1]
                cv2.line(img, point1, point2, (80, 180, 100), 2)

        # 绘制首尾两个点之间的虚线
        if len(points) > 2:
            point1 = points[0]
            point2 = points[-1]
            draw_dashed_line(img, point1, point2, (80, 180, 100), 2, 10)
    
    return img



def make_mosaic(image, x, y, width, height, size=10):
    """在给定的矩形区域应用马赛克效果。"""
    roi = image[y:y+height, x:x+width]
    roi_small = cv2.resize(roi, (width // size, height // size), interpolation=cv2.INTER_LINEAR)
    mosaic = cv2.resize(roi_small, (width, height), interpolation=cv2.INTER_NEAREST)
    image[y:y+height, x:x+width] = mosaic
    return image

def apply_mosaic(img, points, mosaic_size):
    img_current = img.copy()
    mask = np.zeros(img_current.shape[:2], dtype=np.uint8)
    points = np.array(points, dtype=np.int32)
    cv2.fillPoly(mask, [points], 255)
    x, y, w, h = cv2.boundingRect(points)
    image_with_mosaic = make_mosaic(img_current.copy(), x, y, w, h, mosaic_size)
    img_current[mask == 255] = image_with_mosaic[mask == 255]
    return img_current

import json
import os

POINTS_NAME = 'points.json'
DATA_ROOT = ".\\src\\backend\\data"
POINTS_FILE = os.path.join(DATA_ROOT, POINTS_NAME)

def read_points():
    if os.path.exists(POINTS_FILE):
        with open(POINTS_FILE, 'r') as file:
            points_list = json.load(file)
            return [tuple(point) for point in points_list]
    return []

def save_points(points):
    with open(POINTS_FILE, 'w') as file:
        json.dump(points, file)

@app.route('/free_crop', methods=['POST'])
def point_callback():
    data = request.json
    new_point = data.get('point')  # 接收新点
    new_point = (int(new_point['x']), int(new_point['y']))
    
    # 接收并解析缩放比例
    scale = data.get('scale', {'scaleX': 1, 'scaleY': 1})
    scaleX = scale.get('scaleX', 1)
    scaleY = scale.get('scaleY', 1)
    
    # 按比例调整坐标
    scaled_point = (int(new_point[0] * scaleX), int(new_point[1] * scaleY))
    
    image_id = data.get('imageId')
    points = read_points()
    points.append(scaled_point)

    save_points(points)
    
    manager = ImageManager()
    current_image = manager.get_current_image(image_id)
    _, config = manager.get_last_image(image_id)
    print(points)
    img = draw_lines(current_image, points)
    img_base64 = image_2_base64(img)

    return jsonify({"id": image_id, "src": img_base64, "config": config})

if __name__ == '__main__':
    app.run(debug=False, port=5001, threaded=True)
