from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import os
import sys
sys.path.append(".")
from src.backend.Utils import image_2_base64
from src.backend.data.ImageManager import ImageManager


app = Flask(__name__)
CORS(app)

def apply_emboss_effect(img):
    base_kernel = np.array([[0,-1,-1],[1,0,-1],[1,1,0]])

    def generate_kernel(base_kernel, size):
        base_size = base_kernel.shape[0]
        if size <= base_size:
            return base_kernel

        kernel = np.copy(base_kernel)
        while kernel.shape[0] < size:
            kernel = np.pad(kernel, ((1, 1), (1, 1)), 'edge')
        
        return kernel

    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    filter_size = 3
    current_kernel = generate_kernel(base_kernel, filter_size)

    output = cv2.filter2D(gray_img, -1, current_kernel) + 128
    return output

def shadow(input_image, light):
    # 将输入图像转换为浮点类型并归一化，便于后续处理
    f = input_image.astype(np.float32) / 255.0
    # 使用OpenCV将归一化的图像转换为灰度图
    gray = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)

    # 计算灰度图的平方，用以确定阴影区域
    thresh = (1.0 - gray) ** 2
    # 计算阴影区域的平均值，用作后续的阈值
    t = np.mean(thresh)
    # 创建一个掩码，标记阴影区域（高于平均值的区域）
    mask = np.where(thresh >= t, 255, 0).astype(np.uint8)
    # 设置校正参数
    max_val = 4  # 最大校正范围
    bright = light / 100.0 / max_val  # 计算校正强度
    mid = 1.0 + max_val * bright  # 计算中间值
    # 创建两个过渡矩阵，用于调整图像的亮度和对比度
    midrate = np.where(mask == 255, mid, ((mid - 1.0) / t * thresh) + 1.0)
    brightrate = np.where(mask == 255, bright, (1.0 / t * thresh) * bright)
    # 使用指数函数调整图像亮度，并通过掩码实现平滑过渡
    result = np.clip(pow(f, 1.0 / midrate[:, :, np.newaxis]), 0.0, 1.0)
    # 根据计算出的亮度率调整图像，限制值在0到1之间
    result = np.clip(result * (1.0 / (1 - brightrate[:, :, np.newaxis])), 0.0, 1.0) * 255
    # 将结果转换为8位无符号整型，以便显示和保存
    result = result.astype(np.uint8)
    return result

def Saturation(rgb_img, increment):
    # 将输入图像转换为浮点数，并归一化到0-1范围
    img = rgb_img.astype(np.float64) / 255.0
    # 计算每个像素的最小值，即HSL颜色空间中的亮度最低的部分
    img_min = img.min(axis=2)
    # 计算每个像素的最大值，即HSL颜色空间中的亮度最高的部分
    img_max = img.max(axis=2)

    # 计算饱和度（delta）和亮度（value）的中间值
    delta = (img_max - img_min)
    value = (img_max + img_min)
    # 计算HSL颜色空间中的亮度L
    L = value / 2.0

    # 根据亮度L计算饱和度s的两个可能值
    s1 = delta / (value + 1e-8)  # 防止除以0的情况，添加一个很小的数
    s2 = delta / (2 - value + 1e-8)
    # 根据亮度L选择饱和度s的正确值
    s = np.where(L < 0.5, s1, s2)

    # 计算增量调整后的饱和度，如果饱和度加上增量大于1，则保持原饱和度，否则用1减去增量
    temp = increment + s
    alpha = np.where(temp > 1, s, 1 - increment)
    # 计算调整后的alpha值
    alpha = 1 / alpha - 1

    # 对RGB图像的每个通道进行调整，以改变饱和度
    for i in range(3):
        img[:, :, i] += (img[:, :, i] - L) * alpha
    # 确保调整后的RGB值在0到1之间，如果超出这个范围，则将其限制在这个范围内
    img = np.clip(img, 0, 1)

    # 返回调整后的图像
    return img


def laplacian_sharpening(image, kernel_size=3, scale=0.03, delta=0):
    """
    Apply Laplacian sharpening to an image.

    Parameters:
    image: The input image in BGR format.
    kernel_size: The size of the Laplacian kernel (must be 1, 3, 5, or 7).
    scale: The optional scale factor for the computed Laplacian values.
    delta: The optional delta value added to the results prior to storing them.

    Returns:
    The sharpened image.
    """
    # Check if kernel size is valid
    if kernel_size not in [1, 3, 5, 7]:
        raise ValueError("Kernel size must be 1, 3, 5, or 7.")

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Compute the Laplacian of the image
    laplacian = cv2.Laplacian(gray_image, cv2.CV_64F, ksize=kernel_size, scale=scale, delta=delta)

    # Convert Laplacian image to 8-bit
    laplacian_8u = cv2.convertScaleAbs(laplacian)

    # Convert the 8-bit Laplacian image to BGR
    laplacian_8u_bgr = cv2.cvtColor(laplacian_8u, cv2.COLOR_GRAY2BGR)

    # Add the Laplacian image to the original image
    sharpened_image = cv2.addWeighted(image, 1, laplacian_8u_bgr, 1.5, 0)

    return sharpened_image

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
    result[:, :, 2] = apply_lut(result[:, :, 2], lut_r)  # R通道
    result[:, :, 1] = apply_lut(result[:, :, 1], lut_g)  # G通道
    result[:, :, 0] = apply_lut(result[:, :, 0], lut_b)  # B通道
    return result


def shadow(input_image, light):
    # 将输入图像转换为浮点类型并归一化，便于后续处理
    f = input_image.astype(np.float32) / 255.0
    # 使用OpenCV将归一化的图像转换为灰度图
    gray = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)

    # 计算灰度图的平方，用以确定阴影区域
    thresh = (1.0 - gray) ** 2
    # 计算阴影区域的平均值，用作后续的阈值
    t = np.mean(thresh)
    # 创建一个掩码，标记阴影区域（高于平均值的区域）
    mask = np.where(thresh >= t, 255, 0).astype(np.uint8)
    # 设置校正参数
    max_val = 4  # 最大校正范围
    bright = light / 100.0 / max_val  # 计算校正强度
    mid = 1.0 + max_val * bright  # 计算中间值
    # 创建两个过渡矩阵，用于调整图像的亮度和对比度
    midrate = np.where(mask == 255, mid, ((mid - 1.0) / t * thresh) + 1.0)
    brightrate = np.where(mask == 255, bright, (1.0 / t * thresh) * bright)
    # 使用指数函数调整图像亮度，并通过掩码实现平滑过渡
    result = np.clip(pow(f, 1.0 / midrate[:, :, np.newaxis]), 0.0, 1.0)
    # 根据计算出的亮度率调整图像，限制值在0到1之间
    result = np.clip(result * (1.0 / (1 - brightrate[:, :, np.newaxis])), 0.0, 1.0) * 255
    # 将结果转换为8位无符号整型，以便显示和保存
    result = result.astype(np.uint8)
    return result

def Saturation(rgb_img, increment):
    # 将输入图像转换为浮点数，并归一化到0-1范围
    img = rgb_img.astype(np.float64) / 255.0
    # 计算每个像素的最小值，即HSL颜色空间中的亮度最低的部分
    img_min = img.min(axis=2)
    # 计算每个像素的最大值，即HSL颜色空间中的亮度最高的部分
    img_max = img.max(axis=2)

    # 计算饱和度（delta）和亮度（value）的中间值
    delta = (img_max - img_min)
    value = (img_max + img_min)
    # 计算HSL颜色空间中的亮度L
    L = value / 2.0

    # 根据亮度L计算饱和度s的两个可能值
    s1 = delta / (value + 1e-8)  # 防止除以0的情况，添加一个很小的数
    s2 = delta / (2 - value + 1e-8)
    # 根据亮度L选择饱和度s的正确值
    s = np.where(L < 0.5, s1, s2)

    # 计算增量调整后的饱和度，如果饱和度加上增量大于1，则保持原饱和度，否则用1减去增量
    temp = increment + s
    alpha = np.where(temp > 1, s, 1 - increment)
    # 计算调整后的alpha值
    alpha = 1 / alpha - 1

    # 对RGB图像的每个通道进行调整，以改变饱和度
    for i in range(3):
        img[:, :, i] += (img[:, :, i] - L) * alpha
    # 确保调整后的RGB值在0到1之间，如果超出这个范围，则将其限制在这个范围内
    img = np.clip(img, 0, 1)

    # 返回调整后的图像
    return img


def laplacian_sharpening(image, kernel_size=3, scale=0.05, delta=0):
    """
    Apply Laplacian sharpening to an image.

    Parameters:
    image: The input image in BGR format.
    kernel_size: The size of the Laplacian kernel (must be 1, 3, 5, or 7).
    scale: The optional scale factor for the computed Laplacian values.
    delta: The optional delta value added to the results prior to storing them.

    Returns:
    The sharpened image.
    """
    # Check if kernel size is valid
    if kernel_size not in [1, 3, 5, 7]:
        raise ValueError("Kernel size must be 1, 3, 5, or 7.")

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Compute the Laplacian of the image
    laplacian = cv2.Laplacian(gray_image, cv2.CV_64F, ksize=kernel_size, scale=scale, delta=delta)

    # Convert Laplacian image to 8-bit
    laplacian_8u = cv2.convertScaleAbs(laplacian)

    # Convert the 8-bit Laplacian image to BGR
    laplacian_8u_bgr = cv2.cvtColor(laplacian_8u, cv2.COLOR_GRAY2BGR)

    # Add the Laplacian image to the original image
    sharpened_image = cv2.addWeighted(image, 1, laplacian_8u_bgr, 1.5, 0)

    return sharpened_image


def sketch_pencil(image):
    _, sketch = cv2.pencilSketch(image, sigma_s=60, sigma_r=0.07, shade_factor=0.05)
    return sketch

def stylization(image):
    result = cv2.stylization(image, sigma_s=50, sigma_r=0.6)
    return result


def Nostalgia(img):#参数为原图像
    #获取图像属性
    h,w=img.shape[0:2]
    #定义空白图像，存放图像怀旧处理之后的图片
    img1=np.zeros((h, w, 3), dtype=img.dtype)
    #通过对原始图像进行遍历，通过怀旧公式修改像素值，然后进行怀旧处理
    for i in range(h):
        for j in range(w):
            B=0.131*img[i,j,0]+0.534*img[i,j,1]+0.272*img[i,j,2]
            G=0.168*img[i,j,0]+0.686*img[i,j,1]+0.349*img[i,j,2]
            R=0.189*img[i,j,0]+0.769*img[i,j,1]+0.393*img[i,j,2]
            #防止图像溢出
            if B> 255:
                B = 255
            if G>255:
                G = 255
            if R>255:
                R = 255
            img1[i, j] = [int(B), int(G), int(R)]#B\G\R三通道都设置为怀旧值
    return img1

def filter(img, filter):
    if filter == 'relief':
        return apply_emboss_effect(img)
    elif filter == 'grayscale':
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    elif filter == 'pencil':
        return sketch_pencil(img)
    elif filter == 'stylization':
        return stylization(img)
    elif filter == 'fresh':
        lap=laplacian_sharpening(img)
        shd=shadow(lap,-10)
        sat=Saturation(shd,0.3)
        return shd
    elif filter == 'obscure':
        return cv2.blur(img, (15, 15))
    elif filter == 'Glamorous':
        col=color_temperature(img,-20)
        abs = cv2.convertScaleAbs(col, alpha=1.1, beta=-10)
        lap=laplacian_sharpening(abs)
        shd=shadow(lap,-20)
        sat=Saturation(shd,0.1)
        return shd
    elif filter == 'nostalgia':
        return Nostalgia(img)
    else: 
        return img
    

@app.route('/apply_filter', methods=['POST'])
def apply_filter():
    data = request.json
    image_id = data.get('image_id')
    filter_name = data.get('filter')

    manager = ImageManager()
    currentImg = manager.get_current_image(image_id)
    config = {"temperature": 0, "hue": 0, "exposure": 0, "contrast": 0, "sharpen": 0, "saturation": 0}

    img = filter(currentImg, filter_name)
    
    manager.forward_image(image_id, img, config)
    manager.set_current_image(image_id, img)
    manager.save_images()
    encoded_image = image_2_base64(img)

    return jsonify({"id": image_id, "src": encoded_image, "config": config})

if __name__ == '__main__':
    app.run(debug=False, port=5015, threaded=True)
