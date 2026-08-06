# Based on Dreamer_PyTorch by Kaito Suzuki (MIT License).
#   https://github.com/cross32768/Dreamer_PyTorch
# Copyright (c) 2020 Kaito Suzuki
# Modified for Donkey Car / Jetson Nano by Make Brain Project 2022, Group 22-A.

from dreamer.transition import TransitionModel
from dreamer.observation import ObservationModel
from dreamer.reward import RewardModel
import torch
class RSSM:
    def __init__(self, state_dim, action_dim, rnn_hidden_dim, ):
        device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.transition = TransitionModel(state_dim, action_dim, rnn_hidden_dim).to(device)
        self.observation = ObservationModel(state_dim, rnn_hidden_dim,).to(device)
        self.reward = RewardModel(state_dim, rnn_hidden_dim,).to(device)
