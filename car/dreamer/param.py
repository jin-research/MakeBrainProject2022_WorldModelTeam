# coding: utf-8
# Based on Dreamer_PyTorch by Kaito Suzuki (MIT License).
#   https://github.com/cross32768/Dreamer_PyTorch
# Copyright (c) 2020 Kaito Suzuki
# Modified for Donkey Car / Jetson Nano by Make Brain Project 2022, Group 22-A.
import replaybuffer as ReplayBuffer


class param():

    def __init__(self):

        buffer_capacity = 300000  
        replay_buffer = ReplayBuffer(capacity=buffer_capacity,
                              observation_shape=env.observation_space.shape,
                              action_dim=env.action_space.shape[0])
        print("observation_shape",env.observation_space.shape)

        state_dim = 30  
        rnn_hidden_dim = 200  

        encoder = Encoder().to(device)
        rssm = RSSM(state_dim,env.action_space.shape[0],rnn_hidden_dim, )
        print("rssm done")
        value_model = ValueModel(state_dim, rnn_hidden_dim).to(device)
        action_model = ActionModel(state_dim, rnn_hidden_dim,
                             env.action_space.shape[0]).to(device)
        



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


        # モデル読み込み用(追)
        # PATH = "model_save/now_time8.pth"
        # checkpoint = torch.load(PATH)
        # encoder.load_state_dict(checkpoint['encoder_state_dict'])
        # rssm.transition.load_state_dict(checkpoint['rssm_state_dict'])
        # rssm.observation.load_state_dict(checkpoint['observation_state_dict'])
        # rssm.reward.load_state_dict(checkpoint['reward_state_dict'])
        # value_model.load_state_dict(checkpoint['value_state_dict'])
        # action_model.load_state_dict(checkpoint['action_state_dict'])

        
        # model_optimizer.load_state_dict(checkpoint['model_optimizer'])
        # value_optimizer.load_state_dict(checkpoint['value_optimizer'])
        # action_optimizer.load_state_dict(checkpoint['action_optimizer'])



        
        # for state in optimizer.state.values():
        #     for k, v in state.items():
        #         if isinstance(v, torch.Tensor):
        #             state[k] = v.to(device)
        # epoch = checkpoint['epoch']
        # model_loss = checkpoint['model_loss']
        # kl_loss = checkpoint['kl_loss']
        # obs_loss = checkpoint['obs_loss']
        # reward_loss = checkpoint['reward_loss']
        # value_loss = checkpoint['value_loss:']
        # action_loss = checkpoint['action_loss']




