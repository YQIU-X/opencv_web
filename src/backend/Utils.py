import cv2
import numpy as np
import base64

# 统一变量命名
# img   为图片
# image 为{img, config}

def base64_2_image(base64_string):
    
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

def image_2_base64(image):
    _, buffer = cv2.imencode('.jpg', image)
    encoded_image = base64.b64encode(buffer).decode('utf-8')
    return encoded_image


