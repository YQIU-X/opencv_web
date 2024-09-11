import cv2
import numpy as np
import matplotlib.pyplot as plt

def equalize_rgb_histogram(image):
    r, g, b = cv2.split(image)

    r_eq = cv2.equalizeHist(r)
    g_eq = cv2.equalizeHist(g)
    b_eq = cv2.equalizeHist(b)

    img_eq = cv2.merge([r_eq, g_eq, b_eq])

    return img_eq
