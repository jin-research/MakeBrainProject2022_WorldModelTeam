# Based on Dreamer_PyTorch by Kaito Suzuki (MIT License).
#   https://github.com/cross32768/Dreamer_PyTorch
# Copyright (c) 2020 Kaito Suzuki
# Modified for Donkey Car / Jetson Nano by Make Brain Project 2022, Group 22-A.

import pickle
import os
import time
import shutil
import numpy as np
import torch
import cv2
from torch.distributions.kl import kl_divergence
from torch import nn
from torch.nn import functional as F
from torch.nn.utils import clip_grad_norm_
import random

from dreamer.agent import Agent
from dreamer.encoder import Encoder
from dreamer.transition import TransitionModel
from dreamer.action import ActionModel
from dreamer.rssm import RSSM
from dreamer.value import ValueModel
from dreamer.replaybuffer import ReplayBuffer
#画像保存
from PIL import Image
import datetime
import pytz



count_loop = 0
action_dim = 2
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')


buffer_capacity = 300000  
replay_buffer = ReplayBuffer(capacity=buffer_capacity,
                      observation_shape= (64,64,3),
                      action_dim=action_dim)
#print("observation_shape",env.observation_space.shape)

state_dim = 30  
rnn_hidden_dim = 200  

encoder = Encoder().to(device)
rssm = RSSM(state_dim,action_dim,rnn_hidden_dim, )
print("rssm done")
value_model = ValueModel(state_dim, rnn_hidden_dim).to(device)
action_model = ActionModel(state_dim, rnn_hidden_dim,
                     action_dim).to(device)


model_lr = 6e-4  
value_lr = 8e-5
action_lr = 8e-5
eps = 1e-4
model_params = (list(encoder.parameters()) +
          list(rssm.transition.parameters()) +
          list(rssm.observation.parameters()) +
          list(rssm.reward.parameters()))

model_optimizer = torch.optim.Adam(model_params, lr=model_lr, eps=eps)
value_optimizer = torch.optim.Adam(value_model.parameters(), lr=value_lr, eps=eps)
action_optimizer = torch.optim.Adam(action_model.parameters(), lr=action_lr, eps=eps)



test_interval = 10  
seed_episodes = 5#5 # 最初にランダム行動で探索するエピソード数
all_episodes = 600  # 学習全体のエピソード数（300ほどで, ある程度収束します）
model_save_interval =100  # NNの重みを何エピソードごとに保存するか
collect_interval = 100  # 何回のNNの更新ごとに経験を集めるか（＝1エピソード経験を集めるごとに何回更新するか）

action_noise_var = 0.3  
batch_size = 50
chunk_length = 50  
imagination_horizon = 15  


gamma = 0.9  
lambda_ = 0.95  
clip_grad_norm = 100  
free_nats = 1e-7 #3  # KL誤差（RSSMのTransitionModelにおけるpriorとposteriorの間の誤差）がこの値以下の場合, 無視する




encoder = Encoder().to(device)
rssm = RSSM(state_dim, action_dim, rnn_hidden_dim, )
            #transition = TransitionModel(state_dim, action_dim, rnn_hidden_dim).to(device)
action_model = ActionModel(state_dim, rnn_hidden_dim, action_dim).to(device)
value_model = ValueModel(state_dim, rnn_hidden_dim).to(device)
policy = Agent(encoder, rssm.transition, action_model)
            #print("images_record.shape",images_record)
            #PATH = "2022-11-25 18_17_42.109092+09_00599.pth"
encoder.load_state_dict(torch.load('./data/tmp12_5/encoder.pth'))
rssm.transition.load_state_dict(torch.load('./data/tmp12_5/rssm.pth'))
rssm.observation.load_state_dict(torch.load('./data/tmp12_5/obs_model.pth'))
rssm.reward.load_state_dict(torch.load('./data/tmp12_5/reward_model.pth'))
value_model.load_state_dict(torch.load('./data/tmp12_5/value_model.pth'))
action_model.load_state_dict(torch.load('./data/tmp12_5/action_model.pth'))


# ファイルを開く


f = open("real_data_names_store.txt","r")
real_data_names_store = f.read()
f.close()

print("type(real_data_names_store)",type(real_data_names_store))
#print(real_data_names_store)
#print(len(real_data_names_store))
#real_data_names_store_neo=[]
#for i in range(len(real_data_names_store)/49):
#    real_data_names_store_neo.append(real_data_names_store[0:49*i]

import pandas as pd
real_data_names_store=pd.read_csv("real_data_names_store.txt").values.tolist()
#for real_data_name in real_data_names_store:
#    print(real_data_name[0])



for real_data_name in real_data_names_store:
    real_data_name = real_data_name[0]
    print(real_data_name)
    try:

        with open("./data/2022-12-07 03:58:31.408934+09:00_data.bin", mode="rb") as f:
            steerings = pickle.load(f)
            throttles = pickle.load(f)
            images = pickle.load(f)
            rewards = pickle.load(f)
            dones = pickle.load(f)
            '''
            print("steerings_record\n",len(steerings_record))
            print("throttles_record\n",len(throttles_record))
            print("images_record\n",len(images_record))
            print("rewards\n",len(rewards))
            print("dones\n",len(dones))
            '''

#        with open(real_data_name, 'rb') as f:
#            # ファイルからデータを読み込む
#            steerings = pickle.load(f)
#            throttles = pickle.load(f)
#            images = pickle.load(f)
#            rewards = pickle.load(f)
#            dones = pickle.load(f)

    # EOFError が発生した場合
    except EOFError:
        # ファイルを削除する
        os.remove(real_data_name)

        # 新しいファイルを作成する
        with open(real_data_name, 'wb') as f:
            # データを書き込む
            pickle.dump(steerings,f)
            pickle.dump(throttles,f)
            pickle.dump(images,f)
            pickle.dump(rewards,f)
            pickle.dump(dones,f)
            steerings = pickle.load(f)
            throttles = pickle.load(f)
            images = pickle.load(f)
            rewards = pickle.load(f)
            dones = pickle.load(f)
        print("done")


 
    for i in range(min(len(steerings), len(throttles), len(images), len(rewards), len(dones))):
        action = np.array([steerings[i], (throttles[i] + 0.75)/16])
        images[i] = cv2.resize(images[i], dsize = (64, 64))
        replay_buffer.push(images[i], action, rewards[i], dones[i])
start = time.time()

def preprocess_obs(obs):
    obs = obs.astype(np.float32)
    normalized_obs = obs / 255.0 - 0.5
    return normalized_obs

for update_step in range(collect_interval):
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    observations, actions, rewards, _ = \
        replay_buffer.sample(batch_size, chunk_length)


    observations = preprocess_obs(observations)
    observations = torch.as_tensor(observations, device=device)
    observations = observations.transpose(3, 4).transpose(2, 3)
    observations = observations.transpose(0, 1)
    actions = torch.as_tensor(actions, device=device).transpose(0, 1)
    rewards = torch.as_tensor(rewards, device=device).transpose(0, 1)


    print("update_step",update_step)
    embedded_observations = encoder(
        observations.reshape(-1, 3, 64, 64)).view(chunk_length, batch_size, -1)


    states = torch.zeros(chunk_length, batch_size, state_dim, device=device)
    rnn_hiddens = torch.zeros(chunk_length, batch_size, rnn_hidden_dim, device=device)


    state = torch.zeros(batch_size, state_dim, device=device)
    rnn_hidden = torch.zeros(batch_size, rnn_hidden_dim, device=device)


    kl_loss = 0
    for l in range(chunk_length-1):
        next_state_prior, next_state_posterior, rnn_hidden = \
            rssm.transition(state, actions[l], rnn_hidden, embedded_observations[l+1])
        state = next_state_posterior.rsample()
        states[l+1] = state
        rnn_hiddens[l+1] = rnn_hidden
        kl = kl_divergence(next_state_prior, next_state_posterior).sum(dim=1)
        kl_loss += kl.clamp(min=free_nats).mean()  


    kl_loss /= (chunk_length - 1)



    states = states[1:]
    rnn_hiddens = rnn_hiddens[1:]


    flatten_states = states.view(-1, state_dim)
    flatten_rnn_hiddens = rnn_hiddens.view(-1, rnn_hidden_dim)
    recon_observations = rssm.observation(flatten_states, flatten_rnn_hiddens).view(chunk_length-1, batch_size, 3, 64, 64)
    predicted_rewards = rssm.reward(flatten_states, flatten_rnn_hiddens).view(chunk_length-1, batch_size, 1)


    obs_loss = 0.5 * F.mse_loss(recon_observations, observations[1:], reduction='none').mean([0, 1]).sum()
    reward_loss = 0.5 * F.mse_loss(predicted_rewards, rewards[:-1])


    model_loss = kl_loss + obs_loss + reward_loss
    model_optimizer.zero_grad()
    model_loss.backward()
    clip_grad_norm_(model_params, clip_grad_norm)
    model_optimizer.step()

    print("-----------------------")
    print(kl_loss.grad_fn)
    print("-----------------------")

    # --------------------------------------------------

    # --------------------------------------------------


    flatten_states = flatten_states.detach()
    flatten_rnn_hiddens = flatten_rnn_hiddens.detach()



    imaginated_states = torch.zeros(imagination_horizon + 1,
                                     *flatten_states.shape,
                                      device=flatten_states.device)
    imaginated_rnn_hiddens = torch.zeros(imagination_horizon + 1,
                                            *flatten_rnn_hiddens.shape,
                                            device=flatten_rnn_hiddens.device)



    imaginated_states[0] = flatten_states
    imaginated_rnn_hiddens[0] = flatten_rnn_hiddens


    for h in range(1, imagination_horizon + 1):


        actions = action_model(flatten_states, flatten_rnn_hiddens)
        flatten_states_prior, flatten_rnn_hiddens = rssm.transition.prior(rssm.transition.reccurent(flatten_states,
                                                               actions,
                                                               flatten_rnn_hiddens))
        flatten_states = flatten_states_prior.rsample()
        imaginated_states[h] = flatten_states
        imaginated_rnn_hiddens[h] = flatten_rnn_hiddens


    flatten_imaginated_states = imaginated_states.view(-1, state_dim)
    flatten_imaginated_rnn_hiddens = imaginated_rnn_hiddens.view(-1, rnn_hidden_dim)
    imaginated_rewards = \
        rssm.reward(flatten_imaginated_states,
                    flatten_imaginated_rnn_hiddens).view(imagination_horizon + 1, -1)
    imaginated_values = \
        value_model(flatten_imaginated_states,
                    flatten_imaginated_rnn_hiddens).view(imagination_horizon + 1, -1)


    lambda_target_values = lambda_target(imaginated_rewards, imaginated_values, gamma, lambda_)



    action_loss = -lambda_target_values.mean()
    action_optimizer.zero_grad()
    action_loss.backward()
    clip_grad_norm_(action_model.parameters(), clip_grad_norm)
    action_optimizer.step()


    imaginated_values = value_model(flatten_imaginated_states.detach(), flatten_imaginated_rnn_hiddens.detach()).view(imagination_horizon + 1, -1)        
    value_loss =  0.5 * F.mse_loss(imaginated_values, lambda_target_values.detach())
    value_optimizer.zero_grad()
    value_loss.backward()
    clip_grad_norm_(value_model.parameters(), clip_grad_norm)
    value_optimizer.step()
    print('update_step: %3d model loss: %.5f, kl_loss: %.5f, '
             'obs_loss: %.5f, reward_loss: %.5f, '
             'value_loss: %.5f action_loss: %.5f'
                % (update_step + 1, model_loss.item(), kl_loss.item(),
                    obs_loss.item(), reward_loss.item(),
                    value_loss.item(), action_loss.item()))

print('elasped time for update: %.2fs' % (time.time() - start))

log_dir = ".data/tmp" + str(datetime.datetime.now(pytz.timezone('Asia/Tokyo')))

print("log_dir",log_dir)
f = open("log_dir_name_store.txt","a")
f.write("{}\n".format(log_dir))
f.close()

#if (episode + 1) % model_save_interval == 0:

    #model_log_dir_name = str(now_time)+'/episode_%04d' % (episode + 1)+"_"
    #print(model_log_dir_name)
    #model_log_dir = os.path.join(log_dir, model_log_dir_name)
    #if(os.path.isfile(model_log_dir) == True):
    #    shutil.rmtree(model_log_dir)
os.makedirs(log_dir, exist_ok=True)
torch.save(encoder.state_dict(), os.path.join(log_dir, 'encoder.pth'))
torch.save(rssm.transition.state_dict(), os.path.join(log_dir, 'rssm.pth'))
torch.save(rssm.observation.state_dict(), os.path.join(log_dir, 'obs_model.pth'))
torch.save(rssm.reward.state_dict(), os.path.join(log_dir, 'reward_model.pth'))
torch.save(value_model.state_dict(), os.path.join(log_dir, 'value_model.pth'))
torch.save(action_model.state_dict(), os.path.join(model_log_dir, 'action_model.pth'))
