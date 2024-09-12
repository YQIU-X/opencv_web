from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import sys
import numpy as np
sys.path.append(".")
from src.backend.Utils import image_2_base64
from src.backend.data.ImageManager import ImageManager

app = Flask(__name__)
CORS(app)

@app.route('/upload_images', methods=['POST'])
def upload_images():
    manager = ImageManager()
        
    files = request.files.getlist('images')
    valid_extensions = {'jpg', 'jpeg', 'png', 'gif'}

    index = 0
    config = {"temperature": 0, "hue": 0, "exposure": 0, "contrast": 0, "sharpen": 0, "saturation": 0}
    first_image_base64 = None
    
    for file in files:
        file_extension = file.filename.split('.').pop().lower()
        if file_extension not in valid_extensions:
            continue
        
        # 读取图片
        img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_UNCHANGED)
        
        # 检查图片是否有4个通道（包括Alpha通道）
        if img.shape[2] == 4:
            print(file)
            # 如果有Alpha通道，去掉透明度（转换为3通道BGR）
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # 分配图片ID
        image_id = manager.get_next_image_id()

        # 如果是第一张图片且manager为空，生成其base64编码
        if index == 0 and len(manager) == 0:
            first_image_base64 = image_2_base64(img)

        # 添加图片到管理器
        manager.add_image(image_id, img, config)
        index += 1
        print(image_id)
        
    # 保存图片
    manager.save_images()

    # 返回第一个图片的Base64编码
    response = jsonify({'first_image': first_image_base64, "config": config})
    return response

if __name__ == '__main__':
    app.run(debug=False, port=5005, threaded=True)
