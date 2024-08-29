from flask import Flask, request, jsonify, send_file
import cv2

import numpy as np
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 设置后端为 Agg
from scipy.ndimage import gaussian_filter1d
from io import BytesIO
import base64
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 启用 CORS，允许来自所有来源的请求


def drawHist(image):
    colors = ('b', 'g', 'r')
    plt.figure(figsize=(10, 6))

    for i, color in enumerate(colors):
        hist = cv2.calcHist([image], [i], None, [256], [0, 256])
        hist = gaussian_filter1d(hist, sigma=2)  # 平滑处理
        plt.plot(hist, color=color, linewidth=2, alpha=0.8)  # 增加线条宽度和透明度

    plt.title('Color Histogram', fontsize=16, fontweight='bold')
    plt.xlabel('Pixel Intensity', fontsize=14)
    plt.ylabel('Frequency', fontsize=14)
    plt.xlim([0, 256])
    plt.grid(True, linestyle='--', alpha=0.7)  # 添加网格
    plt.gca().set_facecolor('#1c1c1c')  # 设置背景颜色

    # 将绘制的直方图保存到一个内存文件
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return buf

def base64_to_image(base64_string):
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]

    img_data = base64.b64decode(base64_string)
    nparr = np.frombuffer(img_data, np.uint8)
    
    if nparr.size == 0:
        print("Failed to convert base64 to image array")
        return None

    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        print("Failed to decode image")

    return img

@app.route('/upload_image', methods=['POST'])
def upload_image():
    print("999999999999999999999999999999")
    # 获取前端发送的图像数据
    data = request.get_json()
    image_data = data['image']
    
    if not image_data:
        print("not base64_image")
        return jsonify({'error': 'No image data provided'}), 400

    # 解码 Base64 编码的图像数据
    image = base64_to_image(image_data)

    if image is None:
        print("image is None")
        return jsonify({'error': 'Failed to decode image'}), 400

    # 绘制直方图
    hist_buf = drawHist(image)

    # 将图像编码为 JPEG 格式
    _, buffer = cv2.imencode('.jpg', hist_buf)
    if not _:
        return jsonify({'error': 'Failed to encode image'}), 500

    # 将编码后的图像转换为 Base64 编码
    encoded_image = base64.b64encode(buffer).decode('utf-8')

    print(encoded_image[:100])  # 仅打印前100个字符以检查格式

    return jsonify({'image': encoded_image})

if __name__ == '__main__':
    app.run(debug=True, port=5003)
