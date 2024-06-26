import os
import cv2
import torch
import numpy as np
import datetime
import matplotlib.pyplot as plt

# Additional Scripts
from train_transunet import TransUNetSeg

from utils.utils import thresh_func
from config import cfg


class SegInference:
    def __init__(self, model_path, device):
        self.device = device
        self.transunet = TransUNetSeg(device)
        self.transunet.load_model(model_path)

        if not os.path.exists('/content/results'):
            os.mkdir('/content/results')

    def read_and_preprocess(self, p):
        img = cv2.imread(p)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        img_torch = cv2.resize(img, (cfg.transunet.img_dim, cfg.transunet.img_dim))
        img_torch = img_torch / 255.
        img_torch = img_torch.transpose((2, 0, 1))
        img_torch = np.expand_dims(img_torch, axis=0)
        img_torch = torch.from_numpy(img_torch.astype('float32')).to(self.device)

        return img, img_torch

    def save_preds(self, preds):
        folder_path = '/content/results' + str(datetime.datetime.utcnow()).replace(' ', '_')

        os.mkdir(folder_path)
        for name, pred_mask in preds.items():
            cv2.imwrite(f'{folder_path}/{name}', pred_mask)

    def infer(self, path, grad_path,merged=True, save=True):
        path = [path] if isinstance(path, str) else path
        grad_path = [grad_path] if isinstance(grad_path, str) else grad_path

        # filename_for_saving = os.path.basename(path)
        preds = {}

        for p_grad in grad_path:
            file_name_grad = p_grad.split('/')[-1]
            print(file_name_grad)
            img_grad, img_torch_grad = self.read_and_preprocess(p_grad)

        for p in path:
            file_name = p.split('/')[-1]
            img, img_torch = self.read_and_preprocess(p)
            with torch.no_grad():
                pred_mask = self.transunet.model(img_torch, img_torch_grad)
                pred_mask = torch.sigmoid(pred_mask)
                pred_mask = pred_mask.detach().cpu().numpy().transpose((0, 2, 3, 1))

            orig_h, orig_w = img.shape[:2]
            pred_mask = cv2.resize(pred_mask[0, ...], (orig_w, orig_h))
            # print(pred_mask.shape)
            pred_mask_before_th = pred_mask * 255
            cv2.imwrite(f'/content/drive/MyDrive/kvasir/train/treshold_img/{file_name}', pred_mask_before_th)
            print("Image Successfully saved! ")
            # pred_mask = thresh_func(pred_mask, thresh=cfg.inference_threshold)
            # pred_mask *= 255
            # cv2.imwrite('/content/results/plot2.png', pred_mask)                

            # print(pred_mask.shape)
            if merged:
                pred_mask = cv2.bitwise_and(img, img, mask=pred_mask.astype('uint8'))

            preds[file_name] = pred_mask

        # if save:
        #     self.save_preds(preds)

        return preds
