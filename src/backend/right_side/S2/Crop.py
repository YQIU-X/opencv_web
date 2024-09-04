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


import cv2

def draw_rectangle(img, points):
    # 确保 points 是一个包含四个点的列表
    if len(points) != 4:
        raise ValueError("Points must contain exactly 4 corner points")
    
    # 定义颜色和厚度
    color = (0, 255, 0)  # 绿色
    thickness = 2
    corner_thickness = 10
    corner_length = 20

    # 绘制矩形框的四条边
    cv2.rectangle(img, points[0], points[2], color, thickness)

    # 计算矩形中心
    center_x = (points[0][0] + points[2][0]) // 2
    center_y = (points[0][1] + points[2][1]) // 2

    # 绘制四个角的加粗线
    # 左上角
    cv2.line(img, points[0], (points[0][0] + corner_length, points[0][1]), color, corner_thickness)
    cv2.line(img, points[0], (points[0][0], points[0][1] + corner_length), color, corner_thickness)
    
    # 右上角
    cv2.line(img, points[1], (points[1][0] - corner_length, points[1][1]), color, corner_thickness)
    cv2.line(img, points[1], (points[1][0], points[1][1] + corner_length), color, corner_thickness)
    
    # 右下角
    cv2.line(img, points[2], (points[2][0] - corner_length, points[2][1]), color, corner_thickness)
    cv2.line(img, points[2], (points[2][0], points[2][1] - corner_length), color, corner_thickness)
    
    # 左下角
    cv2.line(img, points[3], (points[3][0] + corner_length, points[3][1]), color, corner_thickness)
    cv2.line(img, points[3], (points[3][0], points[3][1] - corner_length), color, corner_thickness)

    # 绘制垂直虚线
    draw_dashed_line(img, (center_x, 0), (center_x, img.shape[0]), (80, 180, 100), 2, 10)

    # 绘制水平虚线
    draw_dashed_line(img, (0, center_y), (img.shape[1], center_y), (80, 180, 100), 2, 10)

    return img


def draw_dashed_line(img, pt1, pt2, color, thickness, gap):
    dist = np.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)
    dashes = int(dist / gap)
    for i in range(dashes):
        start_x = int(pt1[0] + (pt2[0] - pt1[0]) * (i / dashes))
        start_y = int(pt1[1] + (pt2[1] - pt1[1]) * (i / dashes))
        end_x = int(pt1[0] + (pt2[0] - pt1[0]) * ((i + 0.5) / dashes))
        end_y = int(pt1[1] + (pt2[1] - pt1[1]) * ((i + 0.5) / dashes))
        cv2.line(img, (start_x, start_y), (end_x, end_y), color, thickness)
    
    return img

def update_rectangle_and_lines(img, points, new_point):
    rect_top_left = points[0]
    rect_bottom_right = points[2]

    # 计算矩形中心
    center_x = (rect_top_left[0] + rect_bottom_right[0]) // 2
    center_y = (rect_top_left[1] + rect_bottom_right[1]) // 2

    # 确定新点在哪个区域，并更新相应的矩形角点，同时调整对角点确保是矩形
    x = new_point[0]
    y = new_point[1]
    """
      0 | 1
    ----|-----
      3 | 2
    """
    if new_point[0] < center_x and new_point[1] < center_y:
        points[0] = new_point
        points[1] = (points[1][0], new_point[1])
        points[3] = (x, points[3][1])
    elif new_point[0] > center_x and new_point[1] < center_y:
        points[0] = (points[0][0], y)
        points[1] = new_point
        points[2] = (x, points[2][1])
    elif new_point[0] > center_x and new_point[1] > center_y:
        points[1] = (x, points[1][1])
        points[2] = new_point
        points[3] = (points[3][0], y)
    elif new_point[0] < center_x and new_point[1] > center_y:
        points[0] = (x, points[0][1])
        points[2] = (points[2][0], y)
        points[3] = new_point

    # 使用自定义绘制矩形框函数
    img = draw_rectangle(img, points)
    
    return img, points

@app.route('/crop', methods=['POST'])
def point_callback():
    data = request.json
    new_point = data.get('point')  # 接收新点
    new_point = (int(new_point['x']), int(new_point['y']))
    
    # 接收并解析缩放比例
    scale = data.get('scale', {'scaleX': 1, 'scaleY': 1})
    scaleX = scale.get('scaleX', 1)
    scaleY = scale.get('scaleY', 1)
    
    currentOperation = data.get('currentOperation')
    type = data.get('type')
    scaled_point = (int(new_point[0] * scaleX), int(new_point[1] * scaleY))
    
    image_id = data.get('imageId')
    
    manager = ImageManager()
    current_image = manager.get_current_image(image_id)
    _, config = manager.get_last_image(image_id)

    if currentOperation == 'freeCrop':
        # 按比例调整坐标
        points = read_points()
        points.append(scaled_point)
        save_points(points)
        img = draw_lines(current_image, points)
    elif currentOperation == 'rectCrop':
        points = read_points()
        if not points:
            # 第一次点击，初始化裁剪矩形
            height, width = current_image.shape[:2]
            points = [
                (0, 0),  # 左上角
                (width, 0),  # 右上角
                (width, height),  # 右下角
                (0, height)  # 左下角
            ]
            save_points(points)
            save_points(points)
        
            # 绘制初始矩形
            img = draw_rectangle(current_image, points)
        else:
            # 更新矩形角点和虚线，并确保裁剪框始终为矩形
            img, points = update_rectangle_and_lines(current_image, points, scaled_point)
            save_points(points)

    img_base64 = image_2_base64(img)

    return jsonify({"id": image_id, "src": img_base64, "config": config})


if __name__ == '__main__':
    app.run(debug=False, port=5001, threaded=True)
