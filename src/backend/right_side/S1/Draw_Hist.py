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
    # 自动识别图像的类型
    if len(image.shape) == 2 or image.shape[2] == 1:  # 如果是灰度图
        # Create a figure with a grey background
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('#2c2c2c')  # Set the figure background to grey
        ax.set_facecolor('#2c2c2c')  # Set the axis background to grey

        # Compute the histogram for grayscale image
        hist = cv2.calcHist([image], [0], None, [256], [0, 256])
        hist = gaussian_filter1d(hist, sigma=2)  # Apply smoothing

        # Plot the histogram with a white border effect
        ax.fill_between(range(256), hist.ravel(), color='gray', alpha=0.3)
        ax.plot(hist, color='gray', linewidth=2, alpha=0.8,
                path_effects=[patheffects.Stroke(linewidth=4, foreground='white'),
                              patheffects.Normal()])

        ax.set_xlim([0, 256])
        ax.grid(False)
        ax.axis('off')

    else:  # 如果是彩色图像 (BGR)
        colors = ('b', 'g', 'r')
        # Create a figure with a grey background
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('#2c2c2c')  # Set the figure background to grey
        ax.set_facecolor('#2c2c2c')  # Set the axis background to grey

        for i, color in enumerate(colors):
            hist = cv2.calcHist([image], [i], None, [256], [0, 256])
            hist = gaussian_filter1d(hist, sigma=2)  # Apply smoothing

            # Fill the area under the curve with color
            ax.fill_between(range(256), hist.ravel(), color=color, alpha=0.3)
            # Plot the curve with a white border effect
            ax.plot(hist, color=color, linewidth=2, alpha=0.8,
                    path_effects=[patheffects.Stroke(linewidth=4, foreground='white'),
                                  patheffects.Normal()])

        ax.set_xlim([0, 256])
        ax.grid(False)
        ax.axis('off')

    # Save the histogram image to a memory file
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    plt.close(fig)

    # Convert the image from BytesIO to a NumPy array
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

    if img is None:
        return jsonify({'error': 'Image not found'}), 404

    hist_img = drawHist(img)

    encoded_image = image_2_base64(hist_img)

    return jsonify({'image': encoded_image})

if __name__ == '__main__':
    app.run(debug=False, port=5003, threaded=True)
