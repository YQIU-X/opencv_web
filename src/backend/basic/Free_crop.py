from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np

app = Flask(__name__)
CORS(app)

def draw_line(img, point1, point2):
    cv2.line(img, point1, point2, (80, 180, 100), 2)
    return img

def extract_region(img, points):
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    points = np.array(points, dtype=np.int32)
    cv2.fillPoly(mask, [points], 255)
    extracted = cv2.bitwise_and(img, img, mask=mask)
    x, y, w, h = cv2.boundingRect(points)
    roi = extracted[y:y+h, x:x+w]
    return roi

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

POINTS_FILE = 'points.json'

# 从文件中读取点列表
def read_points():
    if os.path.exists(POINTS_FILE):
        with open(POINTS_FILE, 'r') as file:
            return json.load(file)
    return []

# 将点列表写入文件
def save_points(points):
    with open(POINTS_FILE, 'w') as file:
        json.dump(points, file)

@app.route('/point_callback', methods=['POST'])
def point_callback():
    data = request.json
    new_point = data.get('point')  # 接收新点
    mosaic_size = data.get('mosaic_size', 10)  # 可选的马赛克大小

    # 读取现有的点列表
    points = read_points()

    # 将新点添加到列表中
    points.append(new_point)

    # 将更新后的点列表写入文件
    save_points(points)

    # 读取图像 (这里假设图像路径是固定的，也可以根据需要传入)
    img = cv2.imread("src\\backend\\PP_HumanSeg\\data\\images\\bg_1.jpg")

    # 处理图像
    roi = extract_region(img, points)
    img_with_mosaic = apply_mosaic(img, points, mosaic_size)

    # 保存处理后的图像（或进行其他处理，如直接返回图像数据）
    cv2.imwrite("output_roi.jpg", roi)
    cv2.imwrite("output_mosaic.jpg", img_with_mosaic)

    return jsonify({"status": "success", "message": "Image processed successfully."})

if __name__ == '__main__':
    app.run(debug=False, port=5001, threaded=True)
