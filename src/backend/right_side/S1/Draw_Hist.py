
# PORT: http://localhost:5003/fetch_histogram

from flask import Flask, request, jsonify
import cv2
import numpy as np
from matplotlib import pyplot as plt
import matplotlib
from matplotlib import patheffects
matplotlib.use('Agg')  # 设置后端为 Agg
from scipy.ndimage import gaussian_filter1d
from io import BytesIO
from flask_cors import CORS
import sys
sys.path.append(".")
from src.backend.Utils import image_2_base64
from src.backend.data.ImageManager import ImageManager

app = Flask(__name__)
CORS(app)

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


@app.route('/fetch_histogram', methods=['POST'])
def upload_image():
    data = request.get_json()
    image_id_value = int(data.get('id'))


    if isinstance(image_id_value, str):
        image_id = int(image_id_value, 0)
    else:
        image_id = int(image_id_value)
    print("image_id_value", image_id)
    manager = ImageManager()
    img = manager.get_current_image(image_id)
    hist_img = drawHist(img)

    encoded_image = image_2_base64(hist_img)

    return jsonify({'image': encoded_image})

if __name__ == '__main__':
    app.run(debug=False, port=5003, threaded=True)
