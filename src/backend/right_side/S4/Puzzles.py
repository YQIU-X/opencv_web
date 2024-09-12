import cv2
import numpy as np

def get_puzzle(img1, img2, img3, img4):
    final_height = 800
    final_width = final_height // 4 * 3 # 宽度是高度的两倍

    # 设置拼图中图片之间的距离和图片与边缘之间的距离
    spacing = 20  # 图片之间的距离
    margin = 30   # 图片和背景边缘的距离

    # 计算左边两张图片的高度（总高度减去间距和边缘留白平分给两张图）
    left_image_height = (final_height - spacing - 2 * margin) // 2
    left_image_width = (final_width // 2) - margin  # 左侧图片的宽度

    # 计算右边图片的高度和宽度
    right_image_height = final_height - 2 * margin  # 高度需要考虑上下边距
    right_image_width = final_width // 2 - margin - spacing  # 右边图片宽度

    # 调整图片大小
    img1_resized = cv2.resize(img1, (left_image_width, left_image_height))  # 左上图片
    img2_resized = cv2.resize(img2, (left_image_width, left_image_height))  # 左下图片
    img3_resized = cv2.resize(img3, (right_image_width, right_image_height))  # 右边图片

    # 创建黑色背景，高度为 final_height，宽度为 final_width
    background = cv2.resize(img4, (final_width, final_height))

    # 将图片放置到背景上，考虑到边缘留白
    # 左上角图片（留白在左和上）
    background[margin:margin + left_image_height, margin:margin + left_image_width] = img1_resized

    # 左下角图片（留白在左和下）
    background[margin + left_image_height + spacing:final_height - margin, margin:margin + left_image_width] = img2_resized

    # 右边图片（留白在右）
    background[margin:margin + right_image_height, left_image_width + spacing + margin:final_width - margin] = img3_resized

    return background
