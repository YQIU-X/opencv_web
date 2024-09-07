import cv2
import numpy as np
import matplotlib.pyplot as plt

def equalize_rgb_histogram(image):
    # 分离RGB通道
    r, g, b = cv2.split(image)

    # 对每个通道进行直方图均衡化
    r_eq = cv2.equalizeHist(r)
    g_eq = cv2.equalizeHist(g)
    b_eq = cv2.equalizeHist(b)

    # 合并均衡化后的通道
    img_eq = cv2.merge([r_eq, g_eq, b_eq])

    return img_eq
