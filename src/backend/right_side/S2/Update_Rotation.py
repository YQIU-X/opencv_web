import cv2
import numpy as np
import os
import json
from flask import Flask, request, jsonify
import sys
sys.path.append(".")
from src.backend.Utils import image_2_base64
from src.backend.data.ImageManager import ImageManager
from src.backend.right_side.S1.Apply_Config import Apply_Config
from flask_cors import CORS

POINTS_NAME = 'points.json'
DATA_ROOT = ".\\src\\backend\\data"
POINTS_FILE = os.path.join(DATA_ROOT, POINTS_NAME)

app = Flask(__name__)
CORS(app)

def read_points():
    """
    从文件中读取矩形的四个角点。
    """
    if os.path.exists(POINTS_FILE):
        with open(POINTS_FILE, 'r') as file:
            points_list = json.load(file)
            return [tuple(point) for point in points_list]
    return []

def save_points(points):
    """
    将矩形的四个角点保存到文件中。
    """
    with open(POINTS_FILE, 'w') as file:
        # 将 points 转换为 Python 的 int 类型
        json.dump([list(map(int, point)) for point in points], file)

def draw_dashed_line(img, pt1, pt2, color, thickness, gap=10):
    """
    在图像上绘制一条虚线
    """
    dist = np.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)
    dashes = int(dist // gap)
    for i in range(dashes):
        start_x = int(pt1[0] + (pt2[0] - pt1[0]) * (i / dashes))
        start_y = int(pt1[1] + (pt2[1] - pt1[1]) * (i / dashes))
        end_x = int(pt1[0] + (pt2[0] - pt1[0]) * ((i + 0.5) / dashes))
        end_y = int(pt1[1] + (pt2[1] - pt1[1]) * ((i + 0.5) / dashes))
        cv2.line(img, (start_x, start_y), (end_x, end_y), color, thickness)

def get_rotated_boundaries(image, angle):
    """
    获取旋转后的图像尺寸边界。
    """
    h, w = image.shape[:2]
    center = (w // 2, h // 2)

    # 获取旋转矩阵
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    # 计算旋转后的边界框
    cos_val = np.abs(rotation_matrix[0, 0])
    sin_val = np.abs(rotation_matrix[0, 1])

    # 计算新图像的尺寸
    new_w = int((h * sin_val) + (w * cos_val))
    new_h = int((h * cos_val) + (w * sin_val))

    # 调整旋转矩阵中的平移部分
    rotation_matrix[0, 2] += (new_w / 2) - center[0]
    rotation_matrix[1, 2] += (new_h / 2) - center[1]

    return new_w, new_h, rotation_matrix

def line_intersection(p1, p2, p3, p4):
    """
    计算两条线段 (p1, p2) 和 (p3, p4) 的交点
    """
    A1 = p2[1] - p1[1]
    B1 = p1[0] - p2[0]
    C1 = A1 * p1[0] + B1 * p1[1]

    A2 = p4[1] - p3[1]
    B2 = p3[0] - p4[0]
    C2 = A2 * p3[0] + B2 * p3[1]

    det = A1 * B2 - A2 * B1

    if det == 0:
        return None  # 两线平行，无交点
    else:
        x = (B2 * C1 - B1 * C2) / det
        y = (A1 * C2 - A2 * C1) / det
        return np.array([x, y])

def is_point_on_segment(p, p1, p2):
    """
    判断点 p 是否在线段 (p1, p2) 上
    """
    crossproduct = (p[1] - p1[1]) * (p2[0] - p1[0]) - (p[0] - p1[0]) * (p2[1] - p1[1])
    if abs(crossproduct) > 1e-6:
        return False

    dotproduct = (p[0] - p1[0]) * (p2[0] - p1[0]) + (p[1] - p1[1]) * (p2[1] - p1[1])
    if dotproduct < 0:
        return False

    squaredlength = (p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2
    if dotproduct > squaredlength:
        return False

    return True

def calculate_line_points(center, slope, rotated_corners, precision=5):
    """
    计算给定中心点和斜率的直线与旋转矩形的交点
    precision: 控制结果精度，避免浮点数误差导致重复
    """
    # 定义直线方向的两个延伸方向
    direction_positive = np.array([1, slope])  # 正方向
    direction_negative = np.array([-1, -slope])  # 负方向
    
    # 定义起点
    p3 = center
    p4_positive = center + 1000 * direction_positive  # 正向延伸点
    p4_negative = center + 1000 * direction_negative  # 负向延伸点

    intersection_points = []
    # 计算旋转矩形四条边
    for i in range(len(rotated_corners)):
        p1 = rotated_corners[i]
        p2 = rotated_corners[(i + 1) % len(rotated_corners)]  # 每条边

        # 计算直线在正方向和负方向与边的交点
        intersection_positive = line_intersection(p1, p2, p3, p4_positive)
        intersection_negative = line_intersection(p1, p2, p3, p4_negative)

        # 判断交点是否在线段上，并且去重
        if intersection_positive is not None and is_point_on_segment(intersection_positive, p1, p2):
            rounded_intersection_positive = np.round(intersection_positive, precision)
            if not any(np.allclose(rounded_intersection_positive, point, atol=10**-precision) for point in intersection_points):
                intersection_points.append(rounded_intersection_positive)
        
        if intersection_negative is not None and is_point_on_segment(intersection_negative, p1, p2):
            rounded_intersection_negative = np.round(intersection_negative, precision)
            if not any(np.allclose(rounded_intersection_negative, point, atol=10**-precision) for point in intersection_points):
                intersection_points.append(rounded_intersection_negative)

    return intersection_points

def draw_max_inner_rectangle(image, rotation_matrix, new_w, new_h, w, h):
    """
    计算旋转后图像的最大内接矩形，并返回矩形的四个角点。
    """

    # 图像四个角的坐标
    corners = np.array([
        [0, 0], 
        [w, 0], 
        [w, h], 
        [0, h]
    ])

    # 旋转图像的四个角
    rotated_corners = cv2.transform(np.array([corners]), rotation_matrix)[0]

    center_x = new_w//2
    center_y = new_h//2
    center = np.array([center_x, center_y])

    slope1 = h / w
    slope2 = -h / w

    # 计算两条直线与旋转矩形的交点
    intersection_points_slope1 = calculate_line_points(center, slope1, rotated_corners)
    intersection_points_slope2 = calculate_line_points(center, slope2, rotated_corners)
    points = []
    p1 = intersection_points_slope1[0]
    p2 = intersection_points_slope2[0]
    if np.sum((p2 - center)**2) < np.sum((p1 - center)**2):
        p2_int = (int(p2[0]), int(p2[1]))
        points.append(p2_int)
        points.append((int(2 * center_x - p2[0]), int(p2[1])))
        points.append((int(2 * center_x - p2[0]), int(2 * center_y - p2[1])))
        points.append((int(p2[0]), int(2 * center_y - p2[1])))
    else:
        p1_int = (int(p1[0]), int(p1[1]))
        points.append(p1_int)
        points.append((int(2 * center_x - p1[0]), int(p1[1])))
        points.append((int(2 * center_x - p1[0]), int(2 * center_y - p1[1])))
        points.append((int(p1[0]), int(2 * center_y - p1[1])))

    points_sorted = sorted(points, key=lambda point: (point[1], point[0]))

    # Assign sorted points to the respective corners
    top_left = points_sorted[0]
    top_right = points_sorted[1]
    bottom_right = points_sorted[3]
    bottom_left = points_sorted[2]

    # Reorder to match the order: top-left, top-right, bottom-right, bottom-left
    sorted_points = [top_left, top_right, bottom_right, bottom_left]

    # Return the sorted points
    return sorted_points

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

    return img

def rotate_image(image, angle):
    """
    Rotate the given image by the specified angle and return the rotated image.
    """
    # 获取旋转后的图像尺寸和旋转矩阵
    new_w, new_h, rotation_matrix = get_rotated_boundaries(image, angle)
    
    h, w = image.shape[:2]
    # 旋转图像
    rotated_image = cv2.warpAffine(image, rotation_matrix, (new_w, new_h))

    # 绘制水平和垂直虚线
    draw_dashed_line(rotated_image, (new_w // 2, 0), (new_w // 2, new_h), (0, 255, 0), 2)  # 竖线
    draw_dashed_line(rotated_image, (0, new_h // 2), (new_w, new_h // 2), (0, 255, 0), 2)  # 横线

    # 计算最大内接矩形
    max_rect_corners = draw_max_inner_rectangle(rotated_image, rotation_matrix, new_w, new_h, w, h)

    # 保存矩形的四个角点
    save_points(max_rect_corners)

    # 绘制最大内接矩形
    rotated_image = draw_rectangle(rotated_image, max_rect_corners)

    return rotated_image

@app.route('/update_rotation', methods=['POST'])
def update_rotation():
    data = request.json
    image_id = data.get('id')
    angle = data.get('angle')

    try:
        # 将 angle 转换为浮点数
        angle = float(angle)
    except ValueError:
        return jsonify({"error": "Invalid angle value"}), 400

    manager = ImageManager()
    current_image = manager.get_current_image(image_id)

    if current_image is None:
        return jsonify({"error": "Image not found"}), 404

    rotated_image = rotate_image(current_image, angle)
    img_base64 = image_2_base64(rotated_image)
    _, config = manager.get_last_image(image_id)

    return jsonify({"id": image_id, "src": img_base64, "config": config})


if __name__ == '__main__':
    app.run(debug=False, port=5012, threaded=True)
