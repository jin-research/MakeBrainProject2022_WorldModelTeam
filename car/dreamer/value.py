# Based on Dreamer_PyTorch by Kaito Suzuki (MIT License).
#   https://github.com/cross32768/Dreamer_PyTorch
# Copyright (c) 2020 Kaito Suzuki
# Modified for Donkey Car / Jetson Nano by Make Brain Project 2022, Group 22-A.

import torch
from torch import nn
from torch.nn import functional as F

class ValueModel(nn.Module):
    def __init__(self, state_dim, rnn_hidden_dim, hidden_dim=400, act=F.elu):
        super(ValueModel, self).__init__()
        self.fc1 = nn.Linear(state_dim + rnn_hidden_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, hidden_dim)
        self.fc4 = nn.Linear(hidden_dim, 1)
        self.act = act

    def forward(self, state, rnn_hidden):
        hidden = self.act(self.fc1(torch.cat([state, rnn_hidden], dim=1)))
        hidden = self.act(self.fc2(hidden))
        hidden = self.act(self.fc3(hidden))
        state_value = self.fc4(hidden)
        return state_value
