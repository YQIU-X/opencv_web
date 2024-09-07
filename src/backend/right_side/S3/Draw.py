from flask import Flask, request, jsonify
import cv2
import os
import numpy as np
import json
import base64
from flask_cors import CORS
import sys
import pickle

sys.path.append(".")
from src.backend.Utils import image_2_base64, base64_2_image
from src.backend.data.ImageManager import ImageManager
from src.backend.right_side.S1.Apply_Config import Apply_Config

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}})

import cv2
import numpy as np

# 颜色映射，匹配前端传入的颜色名称
color_map = {
    'red': (0, 0, 255),      # BGR格式
    'green': (0, 255, 0),
    'blue': (255, 0, 0),
    'yellow': (0, 255, 255),
    'purple': (255, 0, 255),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'mosaic': None  # 'mosaic' 的处理可以自定义
}

def apply_mosaic_to_line(image, points, mosaic_size, thickness):
    """在给定的点组成的不规则区域上应用马赛克效果"""
    # 创建拷贝以避免修改原始图像
    temp_image = image.copy()

    # 创建一个掩码图像，初始为全零
    mask = np.zeros_like(image)

    # 遍历所有点，在每个点位置绘制一个半径为 thickness 的圆
    for pt in points:
        cv2.circle(mask, tuple(pt), radius=thickness, color=(255, 255, 255), thickness=-1)  # 填充的圆

    # 获取掩码区域（即圆形所覆盖的所有点）
    mask_area = np.where(mask[:, :, 0] == 255)

    if len(mask_area[0]) == 0:
        return image  # 如果没有找到有效区域，直接返回原图

    # 提取掩码区域的像素点，并将其缩小到马赛克尺寸
    mosaic_image = temp_image.copy()

    # 获取这些点对应的像素值
    mosaic_image[mask_area[0], mask_area[1]] = temp_image[mask_area[0], mask_area[1]]

    # 提取掩码区域并应用马赛克效果
    small = cv2.resize(mosaic_image, (mosaic_image.shape[1] // 20, mosaic_image.shape[0] // 20), interpolation=cv2.INTER_LINEAR)

    # 再放大回原来的尺寸
    mosaic = cv2.resize(small, (mosaic_image.shape[1], mosaic_image.shape[0]), interpolation=cv2.INTER_NEAREST)

    # 将马赛克效果应用到原图的掩码区域
    temp_image[mask_area[0], mask_area[1]] = mosaic[mask_area[0], mask_area[1]]

    return temp_image

def draw_lines_on_image(image, points, paint_color, paint_size):
    # 创建图像副本
    temp_image = image.copy()

    # 检查颜色是否在映射表中
    if paint_color not in color_map:
        print(f"Color '{paint_color}' is not valid.")
        return temp_image

    # 获取对应的颜色BGR值
    color = color_map[paint_color]

    if paint_color == 'mosaic':
            # 如果选择了马赛克模式，应用马赛克处理
            temp_image = apply_mosaic_to_line(temp_image, points, mosaic_size=paint_size, thickness=paint_size)
    else:
        # 否则直接画线
        # 遍历points，将相邻点连接成线
        for i in range(len(points) - 1):
            pt1 = tuple(points[i])
            pt2 = tuple(points[i + 1])

            cv2.line(temp_image, pt1, pt2, color, thickness=paint_size)
    
    return temp_image


@app.route('/draw', methods=['OPTIONS', 'POST'])
def draw():
    if request.method == 'OPTIONS':
        return '', 200  # 处理OPTIONS预检请求，返回状态200
    data = request.json
    
    image_id = data.get('id')
    
    paint_color = data.get('paint_color')
    paint_size = int(data.get('paint_size', 10))
    scaleX = float(data.get('scaleX', 1.0))
    scaleY = float(data.get('scaleY', 1.0))
    points = data.get('points')

    # 确保points是一个列表，进行坐标缩放
    scaled_points = [(int(point['x'] * scaleX), int(point['y'] * scaleY)) for point in points]

    manager = ImageManager()
    current_image = manager.get_current_image(image_id)
    config = {"temperature": 0, "hue": 0, "exposure": 0, "contrast": 0, "sharpen": 0, "saturation": 0}
        
    img = draw_lines_on_image(current_image, scaled_points, paint_color, paint_size)

    manager.set_current_image(image_id, img)
    manager.forward_image(image_id, img, config)
    manager.save_images()
        
    encoded_image = image_2_base64(img)

    # 返回响应
    return jsonify({"id": image_id, "src": encoded_image, "config": config})

if __name__ == '__main__':
        app.run(debug=False, port=5014, threaded=True)
