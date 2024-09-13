import torch
import torchvision
from torch import nn
import cv2
from PIL import Image
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
sys.path.append(".")
from src.backend.data.ImageManager import ImageManager
from src.backend.Utils import image_2_base64

app = Flask(__name__)
CORS(app)

class StyleTransfer:
    def __init__(self, content_img_cv, style_img_cv, image_shape=(300, 450), device=None):
        self.device = device if device else torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.image_shape = image_shape

        self.rgb_mean = torch.tensor([0.485, 0.456, 0.406]).to(self.device)
        self.rgb_std = torch.tensor([0.229, 0.224, 0.225]).to(self.device)

        self.content_img = self.cv2_to_pil(content_img_cv)
        self.style_img = self.cv2_to_pil(style_img_cv)

        self.pretrained_net = torchvision.models.vgg19(pretrained=True).features.to(self.device).eval()

        self.style_layers, self.content_layers = [0, 5, 10, 19, 28], [25]
        self.net = nn.Sequential(*[self.pretrained_net[i] for i in range(max(self.style_layers + self.content_layers) + 1)]).to(self.device)
        
        self.content_weight, self.style_weight, self.tv_weight = 1, 1e3, 10

    def cv2_to_pil(self, img_cv):
        """Convert a cv2 image (BGR format) to PIL image (RGB format)."""
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        return Image.fromarray(img_rgb)

    def pil_to_cv2(self, img_pil):
        """Convert a PIL image (RGB format) to cv2 image (BGR format)."""
        img_rgb = np.array(img_pil)
        return cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

    def preprocess(self, img):
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        transforms = torchvision.transforms.Compose([
            torchvision.transforms.Resize(self.image_shape),
            torchvision.transforms.ToTensor(),
            torchvision.transforms.Normalize(mean=self.rgb_mean, std=self.rgb_std)])
        return transforms(img).unsqueeze(0).to(self.device)

    def postprocess(self, img_tensor):
        inv_normalize = torchvision.transforms.Normalize(
            mean=-self.rgb_mean / self.rgb_std,
            std=1 / self.rgb_std)
        to_PIL_image = torchvision.transforms.ToPILImage()
        img_pil = to_PIL_image(inv_normalize(img_tensor[0].cpu()).clamp(0, 1))
        return self.pil_to_cv2(img_pil)

    def extract_features(self, X):
        contents = []
        styles = []
        for i in range(len(self.net)):
            X = self.net[i](X)
            if i in self.style_layers:
                styles.append(X)
            if i in self.content_layers:
                contents.append(X)
        return contents, styles

    def gram(self, X):
        num_channels, n = X.shape[1], X.numel() // X.shape[1]
        X = X.reshape((num_channels, n))
        return torch.matmul(X, X.T) / (num_channels * n)

    def content_loss(self, Y_hat, Y):
        return torch.square(Y_hat - Y.detach()).mean()

    def style_loss(self, Y_hat, gram_Y):
        return torch.square(self.gram(Y_hat) - gram_Y.detach()).mean()

    def tv_loss(self, Y_hat):
        return 0.5 * (torch.abs(Y_hat[:, :, 1:, :] - Y_hat[:, :, :-1, :]).mean() +
                      torch.abs(Y_hat[:, :, :, 1:] - Y_hat[:, :, :, :-1]).mean())

    def compute_loss(self, X, contents_Y_hat, styles_Y_hat, contents_Y, styles_Y_gram):
        contents_l = [self.content_loss(Y_hat, Y) * self.content_weight for Y_hat, Y in zip(contents_Y_hat, contents_Y)]
        styles_l = [self.style_loss(Y_hat, Y) * self.style_weight for Y_hat, Y in zip(styles_Y_hat, styles_Y_gram)]
        tv_l = self.tv_loss(X) * self.tv_weight
        l = sum(10 * styles_l + contents_l + [tv_l])
        return contents_l, styles_l, tv_l, l

    def get_contents(self):
        content_X = self.preprocess(self.content_img)
        contents_Y, _ = self.extract_features(content_X)
        return content_X, contents_Y

    def get_styles(self):
        style_X = self.preprocess(self.style_img)
        _, styles_Y = self.extract_features(style_X)
        return style_X, styles_Y

    def train(self, lr=0.3, num_epochs=700, lr_decay_epoch=50):
        print(self.device)
        content_X, contents_Y = self.get_contents()
        _, styles_Y = self.get_styles()

        gen_img = nn.Parameter(content_X.clone())
        trainer = torch.optim.Adam([gen_img], lr=lr)
        styles_Y_gram = [self.gram(Y) for Y in styles_Y]

        scheduler = torch.optim.lr_scheduler.StepLR(trainer, lr_decay_epoch, 0.8)

        for epoch in range(num_epochs):
            trainer.zero_grad()
            contents_Y_hat, styles_Y_hat = self.extract_features(gen_img)
            _, _, _, l = self.compute_loss(
                gen_img, contents_Y_hat, styles_Y_hat, contents_Y, styles_Y_gram)
            l.backward()
            trainer.step()
            scheduler.step()
            print(epoch)
        return self.postprocess(gen_img)

@app.route('/style_migration', methods=['POST'])
def style_migration():
    data = request.get_json()
    
    # 清理未使用的显存
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    content_img_id = int(data['content_id'])
    style_img_id = int(data['style_id'])
    manager = ImageManager()
    content_img = manager.get_current_image(content_img_id)
    style_img = manager.get_current_image(style_img_id)
    style_transfer = StyleTransfer(content_img, style_img, image_shape=content_img.shape[:2])
    
    # 执行风格迁移
    output_image = style_transfer.train()
    
    # 清理训练过程中未使用的显存
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    new_img_id = manager.get_next_image_id()
    manager.add_image(new_img_id, output_image)
    manager.save_images()

    config = {"temperature": 0, "hue": 0, "exposure": 0, "contrast": 0, "sharpen": 0, "saturation": 0}

    img_base64 = image_2_base64(output_image)
    return jsonify({"id": new_img_id, "src": img_base64, "config": config})

if __name__ == '__main__':
    app.run(debug=False, port=5008, threaded=True)
