import cv2
import numpy as np

def inpaint_image(temp_image, points, paint_size):
    
    # 复制原始图像和掩模
    img_mask = temp_image.copy()
    inpaintMask = np.zeros(temp_image.shape[:2], np.uint8)

    # 根据提供的点列表绘制掩模
    for point in points:
        cv2.circle(inpaintMask, point, paint_size, 255, -1)

    # 选择算法：根据点的数量决定使用哪种修复算法
    if len(points) > 100:
        # 使用Navier-Stokes方法
        res = cv2.inpaint(src=img_mask, inpaintMask=inpaintMask, inpaintRadius=paint_size, flags=cv2.INPAINT_NS)
        method_used = 'NS Technique'
    else:
        # 使用Fast Marching Method
        res = cv2.inpaint(src=img_mask, inpaintMask=inpaintMask, inpaintRadius=paint_size, flags=cv2.INPAINT_TELEA)
        method_used = 'FMM'
    
    return res

# 示例使用
if __name__ == '__main__':
    # 读取图像
    temp_image = cv2.imread('src/backend/right_side/S4/11.png')  # 替换为你的图像文件路径

    # 示例点列表和画笔大小
    points = [(100, 100), (110, 110), (120, 120)]  # 示例的点列表
    paint_size = 5  # 示例画笔大小

    # 调用函数修复图像
    result_image = inpaint_image(temp_image, points, paint_size)

    # 显示修复后的图像
    cv2.imshow('Repaired Image', result_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
