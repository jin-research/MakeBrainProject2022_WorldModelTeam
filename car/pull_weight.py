# translate_weights.py

from collections import OrderedDict
import numpy as np
import shutil
import torch
import sys
import os

# PyTorchの異なるバージョン間での重みの変換
# 例 PyTorch 1.8 で学習 -> PyTorch 1.1 で推論
# 変換後のPyTorchで実行 (例 PyTorch 1.1)



name = "action_model.pth"
ckpt = OrderedDict()


for k in os.listdir("tmp_action/"):
    v = np.load(f"tmp_action/{k}")
    k = k[:-4].replace("+", ".")
    ckpt[k] = torch.from_numpy(v)
torch.save(ckpt, name)
#shutil.rmtree("tmp_action")


name = "encoder.pth"
ckpt = OrderedDict()

for k in os.listdir("tmp_encoder/"):
    v = np.load(f"tmp_encoder/{k}")
    k = k[:-4].replace("+", ".")
    ckpt[k] = torch.from_numpy(v)
torch.save(ckpt, name)
#shutil.rmtree("tmp_encoder")


name = "obs_model.pth"
ckpt = OrderedDict()

for k in os.listdir("tmp_obs/"):
    v = np.load(f"tmp_obs/{k}")
    k = k[:-4].replace("+", ".")
    ckpt[k] = torch.from_numpy(v)
torch.save(ckpt, name)
#shutil.rmtree("tmp_obs")

name = "reward_model.pth"
ckpt = OrderedDict()

for k in os.listdir("tmp_reward/"):
    v = np.load(f"tmp_reward/{k}")
    k = k[:-4].replace("+", ".")
    ckpt[k] = torch.from_numpy(v)
torch.save(ckpt, name)
#shutil.rmtree("tmp_reward")

name = "rssm.pth"
ckpt = OrderedDict()

for k in os.listdir("tmp_rssm/"):
    v = np.load(f"tmp_rssm/{k}")
    k = k[:-4].replace("+", ".")
    ckpt[k] = torch.from_numpy(v)
torch.save(ckpt, name)
#shutil.rmtree("tmp_reward")

name = "value_model.pth"
ckpt = OrderedDict()

for k in os.listdir("tmp_value/"):
    v = np.load(f"tmp_value/{k}")
    k = k[:-4].replace("+", ".")
    ckpt[k] = torch.from_numpy(v)
torch.save(ckpt, name)
#shutil.rmtree("tmp_value")


print("done")
