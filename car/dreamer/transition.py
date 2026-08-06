# Based on Dreamer_PyTorch by Kaito Suzuki (MIT License).
#   https://github.com/cross32768/Dreamer_PyTorch
# Copyright (c) 2020 Kaito Suzuki
# Modified for Donkey Car / Jetson Nano by Make Brain Project 2022, Group 22-A.

import torch
from torch import nn
from torch.nn import functional as F
from torch.distributions import Normal

class TransitionModel(nn.Module):
    def __init__(self, state_dim, action_dim, rnn_hidden_dim,
                 hidden_dim=200, min_stddev=0.1, act=F.elu):
        """
        action_dim: env.action_space.shape[0], 行動環境の次元?
        min_stddev: バイアス? ノイズ?
        """
        super(TransitionModel, self).__init__()
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.rnn_hidden_dim = rnn_hidden_dim
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        print("self.device",self.device)

        

        self.fc_state_action = nn.Linear(state_dim + action_dim, hidden_dim).to(self.device)

        self.fc_rnn_hidden = nn.Linear(rnn_hidden_dim, hidden_dim).to(self.device)

        self.fc_state_mean_prior = nn.Linear(hidden_dim, state_dim).to(self.device)
        self.fc_state_stddev_prior = nn.Linear(hidden_dim, state_dim).to(self.device)

        self.fc_rnn_hidden_embedded_obs = nn.Linear(rnn_hidden_dim + 1024, hidden_dim).to(self.device)

        self.fc_state_mean_posterior = nn.Linear(hidden_dim, state_dim).to(self.device)
        self.fc_state_stddev_posterior = nn.Linear(hidden_dim, state_dim).to(self.device)



        self.rnn = nn.GRUCell(hidden_dim, rnn_hidden_dim).to(self.device)
        self._min_stddev = min_stddev
        self.act = act
  

    def forward(self, state, action, rnn_hidden, embedded_next_obs):
        """
        h_t+1 = f(h_t, s_t, a_t)
        """



        next_state_prior, rnn_hidden = self.prior(self.reccurent(state, action, rnn_hidden))


        # 疑問: なぜposteriorはreccurentを呼び出さないのか?→上のpriorからh_t+1(rnn_hidden)が求まっているから
        next_state_posterior = self.posterior(rnn_hidden, embedded_next_obs)

        return next_state_prior, next_state_posterior, rnn_hidden
      
    def reccurent(self, state, action, rnn_hidden):
        if state is None:
            state = torch.zeros(self.state_dim).to(self.device)
            state = state.unsqueeze(0)
        if action is None:
            action = torch.zeros(self.action_dim).to(self.device)
            print("action",action)
            action = action.unsqueeze(0)
            print("action",action)
            print("TransitionModel.reccurent > action is None")





        hidden = self.act(self.fc_state_action(torch.cat([state, action], dim=1)))


        # h_t+1 = f(hidden, h_t)
        rnn_hidden = self.rnn(hidden, rnn_hidden) 

        return rnn_hidden

    def prior(self, rnn_hidden):



        hidden = self.act(self.fc_rnn_hidden(rnn_hidden))

        # 全結合層に入力し, 平均を求める(?) 
        mean = self.fc_state_mean_prior(hidden)

        # 決定的状態を全結合層に通し, その結果を活性化関数(ソフトプラス)に通した値を標準偏差とする?
        stddev = F.softplus(self.fc_state_stddev_prior(hidden)) + self._min_stddev


        return Normal(mean, stddev), rnn_hidden

    def posterior(self, rnn_hidden, embedded_obs):


        # q(s_t+1 | h_t+1, e_t+1)の h_t, o_tがhiddenに対応?
        hidden = self.act(self.fc_rnn_hidden_embedded_obs(torch.cat([rnn_hidden, embedded_obs], dim=1)))
        

        mean = self.fc_state_mean_posterior(hidden)
        

        stddev = F.softplus(self.fc_state_stddev_posterior(hidden)) + self._min_stddev


        return Normal(mean, stddev)
