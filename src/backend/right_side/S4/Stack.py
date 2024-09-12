import cv2
import numpy as np

def resize_images_to_max(images):
    max_height = max(image.shape[0] for image in images)
    max_width = max(image.shape[1] for image in images)

    resized_images = []
    for image in images:
        resized_image = cv2.resize(image, (max_width, max_height), interpolation=cv2.INTER_AREA)
        resized_images.append(resized_image)

    return resized_images

def stack_images_mean_cv(images):
    resized_images = resize_images_to_max(images)
    stacked_mean = np.mean(np.stack(resized_images, axis=0), axis=0)
    return stacked_mean.astype(np.uint8)

def stack_images_max_cv(images):
    resized_images = resize_images_to_max(images)
    stacked_max = np.max(np.stack(resized_images, axis=0), axis=0)
    return stacked_max.astype(np.uint8)
