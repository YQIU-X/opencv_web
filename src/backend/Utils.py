import cv2
import numpy as np
import base64

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


def IMG_Back(IMG):
    if len(IMG["deque"]) == 1:
        return IMG["raw"]
    else:
        return IMG["deque"].pop()

def IMG_Forward(IMG, img):
    IMG["deque"].append(img)

def IMG_Get(IMG):
    return IMG["deque"][-1]
