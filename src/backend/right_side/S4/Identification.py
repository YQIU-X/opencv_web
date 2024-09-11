import numpy as np
import cv2

def calculate_background_color(image):
    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    mean_brightness = np.mean(gray_image)
    threshold = 127 
    
    if mean_brightness > threshold:
        blue_color = (230, 216, 173)  # 浅蓝色
    else:
        blue_color = (140, 70, 0)  # 深蓝色

    return blue_color

def create_id_photo(input_image):

    mask = np.zeros(input_image.shape[:2], np.uint8)

    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    height, width = input_image.shape[:2]
    rect = (10, 10, width - 10, height - 10)
    cv2.grabCut(input_image, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)

    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    foreground = input_image * mask2[:, :, np.newaxis]

    blue_color = calculate_background_color(input_image)

    background_img = np.full(input_image.shape, blue_color, dtype=np.uint8)

    combined_image = np.where(mask2[:, :, np.newaxis] == 1, foreground, background_img)
    return combined_image