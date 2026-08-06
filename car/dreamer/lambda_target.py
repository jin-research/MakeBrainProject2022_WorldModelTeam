# Based on Dreamer_PyTorch by Kaito Suzuki (MIT License).
#   https://github.com/cross32768/Dreamer_PyTorch
# Copyright (c) 2020 Kaito Suzuki
# Modified for Donkey Car / Jetson Nano by Make Brain Project 2022, Group 22-A.

import torch

def lambda_target(rewards, values, gamma, lambda_):
    V_lambda = torch.zeros_like(rewards, device=rewards.device)

    H = rewards.shape[0] - 1
    V_n = torch.zeros_like(rewards, device=rewards.device)
    V_n[H] = values[H]

    for n in range(1, H+1):


        V_n[:-n] = (gamma ** n) * values[n:]
        for k in range(1, n+1):
            if k == n:
                V_n[:-n] += (gamma ** (n-1)) * rewards[k:]
            else:
                V_n[:-n] += (gamma ** (k-1)) * rewards[k:-n+k]


        if n == H:
            V_lambda += (lambda_ ** (H-1)) * V_n
        else:
            V_lambda += (1 - lambda_) * (lambda_ ** (n-1)) * V_n # 最終的にV_lambdaは1に収束する?

    return V_lambda # 返された後に平均が求められる
