# coding: utf-8
# Your code here!
# Based on Dreamer_PyTorch by Kaito Suzuki (MIT License).
#   https://github.com/cross32768/Dreamer_PyTorch
# Copyright (c) 2020 Kaito Suzuki
# Modified for Donkey Car / Jetson Nano by Make Brain Project 2022, Group 22-A.

import torch
import numpy as np

class Agent:
    def __init__(self, encoder, rssm, action_model):
        self.encoder = encoder
        self.rssm = rssm
        self.action_model = action_model
        self.action_dim = 2
        #self.device = next(self.action_model.parameters()).device
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.rnn_hidden = torch.zeros(1, rssm.rnn_hidden_dim, device=self.device)

    def preprocess_obs(self, obs):
        obs = obs.astype(np.float32)
        normalized_obs = obs / 255.0 - 0.5
        return normalized_obs


    def __call__(self, obs, training=True):

        obs = self.preprocess_obs(obs)
        print("obs.shape",obs.shape)
        obs = torch.as_tensor(obs, device=self.device)
        print("obs.dim()",obs.dim())
        dim = obs.dim()
        obs = obs.transpose(1, dim-1).transpose(0, 1).unsqueeze(0)
        #obs = obs.transpose(1, 2).transpose(0, 1).unsqueeze(0)

        with torch.no_grad():

            embedded_obs = self.encoder(obs)
            state_posterior = self.rssm.posterior(self.rnn_hidden, embedded_obs)
            state = state_posterior.sample()
            action = self.action_model(state, self.rnn_hidden, training=training)


            _, self.rnn_hidden = self.rssm.prior(self.rssm.reccurent(state, action, self.rnn_hidden))
        if action is None:
            action = torch.zeros(self.action_dim).to(self.device)
            print("Agent.__call__ > action is None")
        return action.squeeze().cpu().numpy()


    def reset(self):
        self.rnn_hidden = torch.zeros(1, self.rssm.rnn_hidden_dim, device=self.device)

