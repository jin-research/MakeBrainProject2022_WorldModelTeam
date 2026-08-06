# coding: utf-8
# Your code here!

#!/usr/bin/env python3


import os
import time

from docopt import docopt

import donkeycar as dk
from donkeycar.parts.datastore import TubHandler
from donkeycar.parts.actuator import PWMSteering, PWMThrottle
from donkeycar.parts.datastore import TubGroup, TubWriter
from donkeycar.parts.camera import CSICamera
import numpy as np
#import pandas as pd
import pickle
from donkeycar.parts.datastore_for_record import steerings_record
from donkeycar.parts.datastore_for_record import throttles_record
from donkeycar.parts.datastore_for_record import images_record
import torch
from dreamer.agent import Agent
from dreamer.encoder import Encoder
from dreamer.transition import TransitionModel
from dreamer.action import ActionModel
from dreamer.rssm import RSSM
from dreamer.value import ValueModel
import cv2

def drive(cfg):
    '''
    Construct a working robotic vehicle from many parts.
    Each part runs as a job in the Vehicle loop, calling either
    it's run or run_threaded method depending on the constructor flag `threaded`.
    All parts are updated one after another at the framerate given in
    cfg.DRIVE_LOOP_HZ assuming each part finishes processing in a timely manner.
    Parts may have named outputs and inputs. The framework handles passing named outputs
    to parts requesting the same named input.
    '''

    #Initialize car
    V = dk.vehicle.Vehicle()
    
    class MyController:
        '''
        a simple controller class that outputs a constant steering and throttle.
        '''
        def __init__(self):
            print("MyController.__init__")
            self.count_loop = 0
            self.state_dim = 30
            self.action_dim = 2
            self.rnn_hidden_dim = 200
            self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
            self.encoder = Encoder().to(self.device)
            self.rssm = RSSM(self.state_dim, self.action_dim, self.rnn_hidden_dim, )
            #self.transition = TransitionModel(self.state_dim, self.action_dim, self.rnn_hidden_dim).to(self.device)
            self.action_model = ActionModel(self.state_dim, self.rnn_hidden_dim, self.action_dim).to(self.device)
            self.value_model = ValueModel(self.state_dim, self.rnn_hidden_dim).to(self.device)
            self.policy = Agent(self.encoder, self.rssm.transition, self.action_model)
            #print("images_record.shape",images_record)
            #self.PATH = "2022-11-25 18_17_42.109092+09_00599.pth"
            self.encoder.load_state_dict(torch.load('./presentemp/encoder.pth'))
            self.rssm.transition.load_state_dict(torch.load('./presentemp/rssm.pth'))
            self.rssm.observation.load_state_dict(torch.load('./presentemp/obs_model.pth'))
            self.rssm.reward.load_state_dict(torch.load('./presentemp/reward_model.pth'))
            self.value_model.load_state_dict(torch.load('./presentemp/value_model.pth'))
            self.action_model.load_state_dict(torch.load('./presentemp/action_model.pth'))

        def run(self):
            #print("images_record.shape",images_record)
            obs = cv2.resize(images_record[-1], dsize = (64, 64))
            obs = obs.astype(np.float32)
            #print("obsssssssssssssssssssssssssssss\n", obs.shape)
            #print("obs.shape",obs.shape)
            #print("obs\n",obs)
            print("action = self.policy(obs):",self.policy(obs))
            action = self.policy(obs)
            #action=[0,0]      
            steering = action[0]
            throttle = (action[1] + 0.75)/8
            self.count_loop += 1
            steerings_record.append(steering)
            throttles_record.append(throttle)
            print("type(steering)",type(steering))
            
            return steering, throttle

    V.add(MyController(), outputs=['angle', 'throttle'])

    print("to stop process, CTRL + S ")
    cam = CSICamera()
    V.add(cam, outputs=['image'], threaded=True)

    #warmup camera
    while cam.run() is None:
        time.sleep(1)
        #print("cam.run() is None")

    #add tub part to record images
    tub = TubWriter(path='./dat', inputs=['image'], types=['image_array'])
    V.add(tub, inputs=['image'], outputs=['num_records'])


    #Drive train setup
    #steering_controller = PCA9685(cfg.STEERING_CHANNEL, cfg.PCA9685_I2C_ADDR, busnum=cfg.PCA9685_I2C_BUSNUM)
    steering = PWMSteering(left_pulse=cfg.STEERING_LEFT_PWM, 
                                    right_pulse=cfg.STEERING_RIGHT_PWM)
    
    #throttle_controller = PCA9685(cfg.THROTTLE_CHANNEL, cfg.PCA9685_I2C_ADDR, busnum=cfg.PCA9685_I2C_BUSNUM)
    throttle = PWMThrottle(max_pulse=cfg.THROTTLE_FORWARD_PWM,
                                    zero_pulse=cfg.THROTTLE_STOPPED_PWM, 
                                    min_pulse=cfg.THROTTLE_REVERSE_PWM)

    V.add(steering, inputs=['angle'])
    V.add(throttle, inputs=['throttle'])
    #print('steering, throttle', MyController().run())

    inputs = ['image_array', 'angle', 'throttle']
    types = ['image_array', 'float', 'float']
    
    #multiple tubs
    #th = TubHandler(path=cfg.DATA_PATH)
    #tub = th.new_tub_writer(inputs=inputs, types=types)

    # single tub
    tub = TubWriter(path=cfg.TUB_PATH, inputs=inputs, types=types)
    V.add(tub, inputs=inputs, run_condition='recording')
    
    #run the vehicle for 20 seconds
    V.start(rate_hz=cfg.DRIVE_LOOP_HZ, max_loop_count=cfg.MAX_LOOPS)

if __name__ == '__main__':
    cfg = dk.load_config()
    print("to stop process, CTRL + S ")
    drive(cfg)
