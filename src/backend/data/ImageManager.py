from collections import deque
import pickle
import os

PICKLE_NAME = 'IMAGEs.pkl'
DATA_ROOT = ".\\src\\backend\\data"
PICKLE_FILE = os.path.join(DATA_ROOT, PICKLE_NAME)

"""
[id = 1]
{current: (raw + config)
deque: ({
(raw1:     (raw2:     ...
 config: )  config: )
})}

[id = 2]
{current: (raw + config)
deque: ({
(raw1:     (raw2:     ...
 config: )  config: )
})}
.
.
.
"""
class ImageManager:
    def __init__(self):
        self.pickle_file = PICKLE_FILE
        self.data = {}
        self.max_image_id = 0
        self.load_images()

    def load_images(self):
        if os.path.exists(self.pickle_file):
            with open(self.pickle_file, 'rb') as f:
                self.data = pickle.load(f)
                if self.data:
                    self.max_image_id = max(self.data.keys())
        else:
            print(f"Pickle file {self.pickle_file} not found")


    def save_images(self):
        with open(self.pickle_file, 'wb') as f:
            pickle.dump(self.data, f)

    def add_image(self, id, img, config={"temperature": 0, "hue": 0, "exposure": 0, "contrast": 0}):
        """添加一张新图像"""
        dq = deque()
        dq.append({"img": img, "config": config})
        self.data[id] = {"current": img, "deque": dq}
        
    def get_last_image(self, id):
        image_dic = self.data[id]
        """获取 deque 中最后一张图像"""
        if not image_dic["deque"]:
            raise IndexError("Deque is empty")
        item = image_dic["deque"][-1]
        return item["img"], item["config"]

    def get_current_image(self, id):
        """获取现在图像"""
        image_dic = self.data[id]
        return image_dic["current"]

    def get_next_image_id(self):
        """获取下一个可用的 image_id"""
        self.max_image_id += 1
        return self.max_image_id
    
    def set_current_image(self, id, img):
        """获取现在图像"""
        image_dic = self.data[id]
        image_dic["current"] = img

    def delete_image(self, id):
        del self.data[id]

    def back_image(self, id):
        """回退一张图像"""
        image_dic = self.data[id]
        if len(image_dic["deque"]) == 1:
            item = image_dic["deque"][-1]
            return item["img"], item["config"]
        else:
            item = image_dic["deque"].pop()
            return item["img"], item["config"]
        

    def forward_image(self, id, img, config):
        """前进一张图像"""
        image_dic = self.data[id]
        image_dic["deque"].append({"img": img, "config": config})

    def __len__(self):
        """返回 data 的长度"""
        return len(self.data)
    
    def __iter__(self):
        """实现迭代器方法以便在实例上进行迭代"""
        return iter(self.data.items())