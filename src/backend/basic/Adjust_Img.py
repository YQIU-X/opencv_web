
# PORT: http://localhost:5000/adjust_image

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

# 色温
def color_temperature(input, n):
    def create_lut(level):
        # 创建一个查找表（LUT），范围从0到255
        lut = np.arange(256, dtype=np.uint8)
        # 更复杂的颜色映射，这里使用简单的线性映射作为示例
        # 实际上，可以在这里使用更复杂的非线性映射
        for i in range(256):
            if i + level > 255:
                lut[i] = 255
            elif i + level < 0:
                lut[i] = 0
            else:
                lut[i] = i + level
        return lut

    def apply_lut(image, lut):
        # 使用OpenCV的LUT函数应用查找表
        return cv2.LUT(image, lut)
    
    result = input.copy()
    level = n // 2
    # 创建查找表并应用它到RGB通道
    lut_r = create_lut(level)
    lut_g = create_lut(level)
    lut_b = create_lut(-level)
    result[:, :, 2] = apply_lut(result[:, :, 2], lut_r)
    result[:, :, 1] = apply_lut(result[:, :, 1], lut_g)
    result[:, :, 0] = apply_lut(result[:, :, 0], lut_b)
    return result

# 色调
def adjust_hue(image, hue_shift):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    h = np.mod(h.astype(np.int16) + hue_shift, 180).astype(np.uint8)
    hsv_adjusted = cv2.merge((h, s, v))
    return cv2.cvtColor(hsv_adjusted, cv2.COLOR_HSV2BGR)

# 映射函数
def map_value(contrast):
    if -100 <= contrast <= 0:
        return (contrast + 100) / 100
    elif 0 < contrast <= 100:
        return contrast / 10 + 1
    else:
        raise ValueError("输入值超出预期范围")

# 曝光
def adjust_exposure(image, alpha):
    return cv2.convertScaleAbs(image, alpha=map_value(alpha))

# 对比度
def adjust_contrast(img, contrast):
    fI = img / 255.0

    fI = np.where(fI - 0.01 > 0, fI - 0.01, 0)
    max_val_org = np.max(fI)
    min_val_org = np.min(fI)
    gamma = map_value(contrast)
    O = np.power(fI, gamma)
    
    max_val = np.max(O)
    min_val = np.min(O)

    O = (max_val_org - min_val_org) / (max_val - min_val) * (O - min_val) + min_val_org

    # 将图像数据恢复到 [0, 255] 范围并转换为 uint8 类型
    return np.clip((O * 255), 0, 255).astype(np.uint8)


@app.route('/adjust_image', methods=['POST'])
def adjust_image():
    data = request.json

    temprature = int(data.get('temprature', 0))
    hue = int(data.get('hue', 0))
    exposure = int(data.get('exposure', 0))
    contrast = int(data.get('contrast', 0))
    image_id = data.get('image_id')
    manager = ImageManager()

    img, _ = manager.get_last_image(image_id)
    config = {"temperature": temprature, "hue": hue, "exposure": exposure, "contrast": contrast}
    manager.forward_image(image_id, img, config)  # 存图

    if img is None:
        print("image is None")
        return jsonify({'error': 'Failed to decode image'}), 400

    img = color_temperature(img, temprature)
    img = adjust_hue(img, hue)
    img = adjust_exposure(img, exposure)
    img = adjust_contrast(img, contrast)
    print(config)
    manager.set_current_image(image_id, img)  # 设当前图

    encoded_image = image_2_base64(img)

    manager.save_images()  # 存文件
    return jsonify({'image': encoded_image, 'config' : config})

if __name__ == '__main__':
    app.run(debug=False, port=5000, threaded=True)
