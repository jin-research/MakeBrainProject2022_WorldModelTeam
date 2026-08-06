# Based on Dreamer_PyTorch by Kaito Suzuki (MIT License).
#   https://github.com/cross32768/Dreamer_PyTorch
# Copyright (c) 2020 Kaito Suzuki
# Modified for Donkey Car / Jetson Nano by Make Brain Project 2022, Group 22-A.

import torch
from torch import nn
from torch.nn import functional as F
import numpy as np
import torch.distributions as dist

class ActionModel(nn.Module):
    def __init__(self, state_dim, rnn_hidden_dim, action_dim,
                 hidden_dim=400, act=F.elu, min_stddev=1e-4, init_stddev=5.0):
        super(ActionModel, self).__init__()
        self.fc1 = nn.Linear(state_dim + rnn_hidden_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, hidden_dim)
        self.fc4 = nn.Linear(hidden_dim, hidden_dim)
        self.fc_mean = nn.Linear(hidden_dim, action_dim)
        self.fc_stddev = nn.Linear(hidden_dim, action_dim)
        self.act = act
        self.min_stddev = min_stddev
        self.init_stddev = np.log(np.exp(init_stddev) - 1)

    def calc_reward(self, done: bool) -> float:
            # Normalization factor, real max speed is around 30
            # but only attained on a long straight line
            max_speed = 10
            
            #print("self.image_array[:,:,0]",self.image_array[:,:,0])
            r_range_1 = (210 <(self.image_array[:,:,0]))
            r_range_2 =  ( (self.image_array[:,:,0]) < 240 )
            g_range_1 =  ( 170 < (self.image_array[:,:,1]) )
            g_range_2 =  ( (self.image_array[:,:,1]) < 200 )
            b_range_1 =  ( 110 < (self.image_array[:,:,2]) )
            b_range_2 =  ( (self.image_array[:,:,2]) < 140 )
            pixel_range = r_range_1 * r_range_2 * g_range_1 * g_range_2 * b_range_1 * b_range_2
            pixel_range_num = pixel_range.sum()
            all_square_pixel = sum((self.image_array).shape) / 3
            all_square_pixel_percentage = (pixel_range_num/all_square_pixel)*100
            #print("all_square_pixel_percentage [%]",all_square_pixel_percentage)
    
            # print("image_array",self.image_array)
    
            if done:
                return -1.0
    
            #if self.cte > self.max_cte:
            #    return -1.0
    
            # Collision
            #if self.hit != "none":
            #    return -2.0
    
            # going fast close to the center of lane yields best reward
            base_all_square_pixel_percentage = 5 #[%]
            #print("old_reward", (1.0 - (self.cte / self.max_cte) ** 2) * (self.speed / max_speed))
            #print("new_reward",( ( all_square_pixel_percentage / base_all_square_pixel_percentage )**2) * (self.speed / max_speed))
            
            
            # steering
    
            
            
            return_reward = ( ( all_square_pixel_percentage / base_all_square_pixel_percentage )) * ( self.speed / max_speed)
            #return_reward = all_square_pixel_percentage * (self.speed*3)
            #print("return_reward", return_reward)
            return return_reward
            
    
            #return (1.0 - (self.cte / self.max_cte) ** 2) * (self.speed / max_speed)

    def forward(self, state, rnn_hidden, training=True):
        if state is None:
            state = torch.zeros(self.state_dim).to(self.device)
            state = state.unsqueeze(0)
        if rnn_hidden is None:
            rnn_hidden = torch.zeros(self.rnn_hidden_dim).to(self.device)
            rnn_hidden = rnn_hidden.unsqueeze(0)    
        hidden = self.act(self.fc1(torch.cat([state, rnn_hidden], dim=1)))
        hidden = self.act(self.fc2(hidden))
        hidden = self.act(self.fc3(hidden))
        hidden = self.act(self.fc4(hidden))


        mean = self.fc_mean(hidden)
        mean = 5.0 * torch.tanh(mean / 5.0)
        stddev = self.fc_stddev(hidden)
        stddev = F.softplus(stddev + self.init_stddev) + self.min_stddev
        if training:
            #action = torch.tanh(Normal(mean, stddev).rsample())
            action = torch.tanh(dist.Normal(mean, stddev).rsample())
        else:
            action = torch.tanh(mean)
        return action
