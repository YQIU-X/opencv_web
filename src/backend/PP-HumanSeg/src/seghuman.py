import os
import cv2
import numpy as np
from paddleseg.utils import get_sys_env, logger
from infer import Predictor

class Args:
    def __init__(self):
        self.vertical_screen = False
        self.use_post_process = False  # 固定设置为False
        self.use_optic_flow = False
        self.test_speed = False
        self.bg_img_path = None
        self.img_path = None
        self.save_dir = None
        self.config = '.\inference_models\portrait_pp_humansegv2_lite_256x144_inference_model_with_softmax\deploy.yaml'

def get_bg_img(bg_img_path, img_shape):
    if bg_img_path is None:
        bg = 255 * np.ones(img_shape)
    elif not os.path.exists(bg_img_path):
        raise Exception('The --bg_img_path is not existed: {}'.format(
            bg_img_path))
    else:
        bg = cv2.imread(bg_img_path)
    return bg

def seg_image(img, bg_img):
    args = Args()
    env_info = get_sys_env()
    args.use_gpu = True if env_info['Paddle compiled with cuda'] \
        and env_info['GPUs used'] else False
    logger.info("Input: image")
    logger.info("Create predictor...")
    predictor = Predictor(args)
    logger.info("Start predicting...")
    out_img = predictor.run(img, bg_img)
    return out_img

if __name__ == "__main__":
    img = cv2.imread(".\data\images\portrait_heng.jpg")
    bg_img = get_bg_img(None, img.shape)
    segimage = seg_image(img, bg_img)
    cv2.imshow('aa', segimage)
    cv2.waitKey(0)
