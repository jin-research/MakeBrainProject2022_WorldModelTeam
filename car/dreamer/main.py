# coding: utf-8
# Based on Dreamer_PyTorch by Kaito Suzuki (MIT License).
#   https://github.com/cross32768/Dreamer_PyTorch
# Copyright (c) 2020 Kaito Suzuki
# Modified for Donkey Car / Jetson Nano by Make Brain Project 2022, Group 22-A.
import time
import os
import shutil
import csv
import gym

import numpy as np
import matplotlib.pyplot as plt

import torch
import cv2

from torch.distributions import Normal
from torch.distributions.kl import kl_divergence
from torch import nn
from torch.nn import functional as F
from torch.nn.utils import clip_grad_norm_

import random
from gym import spaces
from gym.utils import seeding


#画像保存
from PIL import Image
import datetime
import pytz


# actionの調和平均を取るため
import pandas as pd

import action
import agent
import encoder
import lambda_target
import makeEnv
import obsercation
import param
import preprocessObs
import randomAction
import replaybuffer
from rssm import RSSM
import reward
import takeAction
import transition
import value

''' クラスのインスタンス化(ハイパーパラメータの箇所がまだ直せていない) '''
make_env = makeEnv() 
param() # ハイパーパラメータ
encoder = encoder.to(device)
rssm = RSSM(param.state_dim, env.action_space.shape[0], param.rnn_hidden_dim)
''' 保存先 '''
log_dir = 'logs_test_from1031'
#log_dir = 'logs'
writer = SummaryWriter(log_dir)

''' メイン学習 '''
start_time = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
print("開始時刻：", start_time)



# for episode in range(epoch, all_episodes):

for episode in range(param.seed_episodes, param.all_episodes):
    action0_data = pd.Series(0)
    # -----------------------------
    
    # -----------------------------
    start = time.time()
    
    policy = Agent(encoder, rssm.transition, action_model)
    obs = env.reset()
    
    dir = 'data/sim_img_data'+str(now_time) + "/"
    os.makedirs(dir, exist_ok = True)
    dir = dir + 'episode'+ str(episode) + "/"
    os.makedirs(dir, exist_ok = True)
    c=0
    
    done = False
    total_reward = 0


