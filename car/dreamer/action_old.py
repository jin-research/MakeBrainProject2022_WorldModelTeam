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
