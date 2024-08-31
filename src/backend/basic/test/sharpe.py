import cv2
import numpy as np

import cv2
import sys
import numpy as np
import matplotlib.pyplot as plt

import os
print(os.getcwd())

# 读取图像
img = cv2.imread('src\\backend\\basic\\test\\1.jpg')

import cv2
import numpy as np

def adjust_saturation(image, alpha):

    hls_image = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
    h, l, s = cv2.split(hls_image)
    s = np.clip(s * alpha, 0, 255).astype(np.uint8)
    
    # 将调整后的S通道与原始的H和L通道合并
    adjusted_hls_image = cv2.merge([h, l, s])
    
    # 将图像从HLS转换回BGR色彩空间
    adjusted_image = cv2.cvtColor(adjusted_hls_image, cv2.COLOR_HLS2BGR)
    
    return adjusted_image

def update_saturation(val):
    # 将滑动条的值映射到合适的alpha范围，例如[0.5, 2.0]
    alpha = val / 50.0
    adjusted_image = adjust_saturation(img, alpha)
    cv2.imshow('Image', img)
    cv2.imshow('Saturation Adjusted Image', adjusted_image)


# 创建一个窗口来显示图像
cv2.namedWindow('Saturation Adjusted Image')

# 创建一个滑动条，初始值为100（表示alpha=1.0），最大值为200
cv2.createTrackbar('Saturation', 'Saturation Adjusted Image', 50, 300, update_saturation)

# 初始化显示图像
update_saturation(50)

# 等待按下ESC键关闭窗口
while True:
    if cv2.waitKey(1) & 0xFF == 27:
        break

cv2.destroyAllWindows()

