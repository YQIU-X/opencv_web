from flask import Flask, request, jsonify
import cv2
import numpy as np
from matplotlib import pyplot as plt
import matplotlib
from matplotlib import patheffects  # 导入 path_effects 模块
matplotlib.use('Agg')  # 设置后端为 Agg
from scipy.ndimage import gaussian_filter1d
from io import BytesIO
import base64
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 启用 CORS，允许来自所有来源的请求

def drawHist(image):
    colors = ('b', 'g', 'r')
    
    # 创建一个带灰色背景的图形
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#2c2c2c')  # 整个图形背景设置为灰色
    ax.set_facecolor('#2c2c2c')  # 坐标轴背景设置为灰色

    for i, color in enumerate(colors):
        hist = cv2.calcHist([image], [i], None, [256], [0, 256])
        hist = gaussian_filter1d(hist, sigma=2)  # 平滑处理
        
        # 绘制曲线，并添加白色边缘效果
        ax.plot(hist, color=color, linewidth=2, alpha=0.8,
                path_effects=[patheffects.Stroke(linewidth=4, foreground='white'),
                              patheffects.Normal()])

    ax.set_xlim([0, 256])
    
    # 去除网格、坐标轴及其标签
    ax.grid(False)
    ax.axis('off')

    # 将绘制的直方图保存到一个内存文件
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    plt.close(fig)

    # 从 BytesIO 读取图像并将其转换为 NumPy 数组
    img_array = np.frombuffer(buf.getvalue(), dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    return img

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
    # 获取前端发送的图像数据
    data = request.get_json()
    image_data = data['image']
    
    if not image_data:
        return jsonify({'error': 'No image data provided'}), 400

    # 解码 Base64 编码的图像数据
    image = base64_to_image(image_data)

    if image is None:
        return jsonify({'error': 'Failed to decode image'}), 400

    # 绘制直方图
    hist_img = drawHist(image)

    # 将图像编码为 JPEG 格式
    _, buffer = cv2.imencode('.jpg', hist_img)
    if not _:
        return jsonify({'error': 'Failed to encode image'}), 500

    # 将编码后的图像转换为 Base64 编码
    encoded_image = base64.b64encode(buffer).decode('utf-8')

    return jsonify({'image': encoded_image})

if __name__ == '__main__':
    app.run(debug=True, port=5003)
