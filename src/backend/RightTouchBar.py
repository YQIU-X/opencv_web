from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64

app = Flask(__name__)
CORS(app)  # 允许所有源的请求，你可以根据需要配置更具体的规则

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

def color_temperature(input, n):
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

def adjust_hue(image, hue_shift):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    h = np.mod(h.astype(np.int16) + hue_shift, 180).astype(np.uint8)
    hsv_adjusted = cv2.merge((h, s, v))
    return cv2.cvtColor(hsv_adjusted, cv2.COLOR_HSV2BGR)

def map_value(contrast):
    if -100 <= contrast <= 0:
        return (contrast + 100) / 100
    elif 0 < contrast <= 100:
        return contrast / 10 + 1
    else:
        raise ValueError("输入值超出预期范围")
    
def adjust_exposure(image, alpha):
    return cv2.convertScaleAbs(image, alpha=map_value(alpha))


    
def adjust_contrast(img, contrast):
    # 将图像数据归一化到 [0, 1] 范围
    fI = img / 255.0
    
    # 计算原始图像的最大值
    max_val_org = np.max(fI)
    
    # 使用伽马变换调整对比度
    gamma = map_value(contrast)
    O = np.power(fI, gamma)
    
    # 计算伽马变换后的最大值
    max_val = np.max(O)
    
    # 归一化图像数据以保持原始的最大值
    O *= (max_val_org / max_val)
    
    # 将图像数据恢复到 [0, 255] 范围并转换为 uint8 类型
    return (O * 255).astype(np.uint8)


@app.route('/adjust_image', methods=['POST'])
def adjust_image():
    data = request.json
    temprature = int(data.get('temprature', 0))
    hue = int(data.get('hue', 0))
    exposure = int(data.get('exposure', 0))
    contrast = int(data.get('contrast', 0))
    base64_image = data.get('image')
    
    # print(base64_image)

    if not base64_image:
        print("not base64_image")
        return jsonify({'error': 'No image data provided'}), 400

    # 解码 Base64 编码的图像数据
    image = base64_to_image(base64_image)

    if image is None:
        print("image is None")
        return jsonify({'error': 'Failed to decode image'}), 400

    image = color_temperature(image, temprature)
    image = adjust_hue(image, hue)
    image = adjust_exposure(image, exposure)
    image = adjust_contrast(image, contrast)

    # 将图像编码为 JPEG 格式
    _, buffer = cv2.imencode('.jpg', image)
    if not _:
        return jsonify({'error': 'Failed to encode image'}), 500

    # 将编码后的图像转换为 Base64 编码
    encoded_image = base64.b64encode(buffer).decode('utf-8')
    return jsonify({'image': encoded_image})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
