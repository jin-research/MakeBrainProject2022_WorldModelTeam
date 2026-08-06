# coding: utf-8
# Based on Dreamer_PyTorch by Kaito Suzuki (MIT License).
#   https://github.com/cross32768/Dreamer_PyTorch
# Copyright (c) 2020 Kaito Suzuki
# Modified for Donkey Car / Jetson Nano by Make Brain Project 2022, Group 22-A.
import time
import os
import random
import matplotlib.pyplot as plt
import numpy as np

import makeEnv

def random():
    make_env = make_env()
    start_time = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    print("開始時刻：", start_time)
    now_time = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    dir = 'data' + '/'
    os.makedirs(dir, exist_ok = True)

    for episode in range(seed_episodes):
        action0_data = pd.Series(0)
        obs = env.reset()
        obs = cv2.resize(obs,dsize = (64,64))
    
        dir = 'data/sim_img_data'+str(now_time) + "/"
        os.makedirs(dir, exist_ok = True)
        dir = dir + 'episode'+ str(episode) + "/"
        os.makedirs(dir, exist_ok = True)
    
        done = False
        c=0
        while not done:
            plt.imshow(obs)
            plt.show()
            obs = cv2.resize(obs,dsize = (64,64))
        
            pil_img = Image.fromarray(obs)
    
            if  c%15 == 0:
                filename=dir + str(c) + '.png'
                pil_img.save(filename)
            
            action = env.action_space.sample()
            action0_data, num_for_action0_assignment, action = take_action_moving_average(action0_data, num_for_action0_assignment, action)
        
            action[1]=(action[1]+0.75)/2
            next_obs, reward, done, _ = env.step(action)
            replay_buffer.push(obs, action, reward, done)
            obs = next_obs
            print(c)
            c+=1
        
        

