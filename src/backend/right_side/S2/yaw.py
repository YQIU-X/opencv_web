import cv2
import numpy as np


def adjust_vertical_perspective(image, correction=0):
    (h, w) = image.shape[:2]

    # 定义输入图像的四个角点
    src_pts = np.float32([[0, 0], [w, 0], [0, h], [w, h]])

    # 根据 correction 值决定是顶部还是底部矫正
    if correction >= 0:
        # 顶部矫正
        dst_pts = np.float32([[0 - correction, 0], [w + correction, 0], 
                              [0, h], [w, h]])
    else:
        # 底部矫正
        correction = abs(correction)
        dst_pts = np.float32([[0, 0], [w, 0], 
                              [0 - correction, h], [w + correction, h]])
    
    # 计算透视变换矩阵
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)

    # 计算新尺寸以适应更大的图像
    new_w = w + abs(correction) * 2
    new_h = h

    # 应用透视变换
    corrected_image = cv2.warpPerspective(image, M, (new_w, new_h))
    return corrected_image

def adjust_horizon_perspective(image, correction=0):
    (h, w) = image.shape[:2]

    # 定义输入图像的四个角点
    src_pts = np.float32([[0, 0], [w, 0], [0, h], [w, h]])

    # 根据 correction 值决定是顶部还是底部矫正
    if correction >= 0:
        # 顶部矫正
        dst_pts = np.float32([[0, 0 - correction], [w, 0 + correction], 
                              [0, h], [w, h]])
    else:
        # 底部矫正
        correction = abs(correction)
        dst_pts = np.float32([[0, 0], [w, 0], 
                              [0, h - correction], [w, h + correction]])
    
    # 计算透视变换矩阵
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)

    # 计算新尺寸以适应更大的图像
    new_w = w + abs(correction) * 2
    new_h = h

    # 应用透视变换
    corrected_image = cv2.warpPerspective(image, M, (new_w, new_h))
    return corrected_image

# 回调函数，用于滑动条更新
def update_image(val):
    # 获取当前滑动条的值
    correction = cv2.getTrackbarPos('Correction', 'Adjustments') - w // 2

    # 应用透视变换
    perspective_corrected_image = adjust_horizon_perspective(image, correction=correction)

    # 显示调整后的图像
    cv2.imshow('Adjustments', perspective_corrected_image)


image = cv2.imread("src\\backend\\right_side\\S4\\PP_HumanSeg\\data\\images\\bg_1.jpg")
(h, w) = image.shape[:2]

# 创建窗口
cv2.namedWindow('Adjustments')

# 创建滑动条
cv2.createTrackbar('Correction', 'Adjustments', w // 2, w, update_image)  # 矫正范围从 -w/2 到 w/2

# 初始化显示
update_image(0)

# 等待用户操作
cv2.waitKey(0)
cv2.destroyAllWindows()
