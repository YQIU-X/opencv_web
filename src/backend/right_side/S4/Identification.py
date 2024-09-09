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

    # 步骤1：为grabCut准备掩模
    mask = np.zeros(input_image.shape[:2], np.uint8)

    # 为grabCut创建模型
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    # 步骤2：定义包含人像区域的矩形
    height, width = input_image.shape[:2]
    rect = (10, 10, width - 10, height - 10)  # 根据需要调整这个矩形

    # 步骤3：应用grabCut算法
    cv2.grabCut(input_image, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)

    # 步骤4：修改掩模以提取前景
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    foreground = input_image * mask2[:, :, np.newaxis]

    # 获取合适的背景颜色
    blue_color = calculate_background_color(input_image)

    # 步骤6：创建与输入图像大小相同的蓝色背景
    background_img = np.full(input_image.shape, blue_color, dtype=np.uint8)

    # 步骤7：将分割的前景与新背景合成
    combined_image = np.where(mask2[:, :, np.newaxis] == 1, foreground, background_img)
    return combined_image