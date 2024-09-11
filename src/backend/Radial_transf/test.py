import cv2
import numpy as np
import matplotlib.pyplot as plt

# 加载图像
image = cv2.imread('src/backend/Radial_transf/11.png')

# 获取图像的尺寸
height, width = image.shape[:2]

# 原始矩形的四个角点
pts1 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])

# 目标四边形的四个角点，可以任意调整
pts2 = np.float32([[10, 30], [470, 50], [70, 670], [500, 450]])

# 计算透视变换矩阵
matrix = cv2.getPerspectiveTransform(pts1, pts2)

# 计算变换后的四个角点的新位置
new_corners = cv2.perspectiveTransform(np.array([pts1]), matrix)[0]

# 计算包裹变换后四个角点的最小矩形
x, y, new_width, new_height = cv2.boundingRect(new_corners)

# 创建平移矩阵，修正图像位置
translation_matrix = np.array([[1, 0, -x], [0, 1, -y], [0, 0, 1]])

# 将平移矩阵与透视变换矩阵相乘
adjusted_matrix = np.dot(translation_matrix, matrix)

# 执行透视变换，创建新的画布大小来包含变换后的图片
transformed_image = cv2.warpPerspective(image, adjusted_matrix, (new_width, new_height))

# 使用matplotlib显示原图和变换后的图像
plt.subplot(1, 2, 1)
plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
plt.title('Original Image')

plt.subplot(1, 2, 2)
plt.imshow(cv2.cvtColor(transformed_image, cv2.COLOR_BGR2RGB))
plt.title('Transformed Image (Corrected Alignment)')

plt.show()
