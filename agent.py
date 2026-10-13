from model import G_apexNet, hard_update, soft_update
from buffer import ReplayBuffer
import torch
import torch.optim as optim
import torch.nn.functional as F
import datetime
import time
import random
import os
from game import AlienShooter

class Agent():

    def __init__(self, env : AlienShooter, dropout, hidden_layer, learning_rate, step_repeat, gamma):
        
        self.env = env

        self.step_repeat = step_repeat

        self.gamma = gamma

        observation, info = self.env.reset()

        self.device = 'cuda:0' if torch.cuda.is_available() else 'cpu'

        print("Model loaded on: ", self.device)

        self.memory = ReplayBuffer(max_size=500000, input_shape=observation.shape, n_actions= env.action_space.n, device= self.device)

        self.model_1 = G_apexNet(action_dim=env.action_space.n, observation_shape = observation.shape, hidden_dim = hidden_layer, dropout = dropout).to(self.device)
        self.model_2 = G_apexNet(action_dim=env.action_space.n, observation_shape = observation.shape, hidden_dim = hidden_layer, dropout = dropout).to(self.device)

        self.target_model_1 = G_apexNet(action_dim=env.action_space.n, observation_shape = observation.shape, hidden_dim = hidden_layer, dropout = dropout).to(self.device)
        self.target_model_2 = G_apexNet(action_dim=env.action_space.n, observation_shape = observation.shape, hidden_dim = hidden_layer, dropout = dropout).to(self.device)

        hard_update(self.target_model_1, self.model_1)
        hard_update(self.target_model_2, self.model_2)

        self.optimizer_1 = optim.Adam(self.model_1.parameters(), lr=learning_rate)
        self.optimizer_2 = optim.Adam(self.model_2.parameters(), lr=learning_rate)

        self.learning_rate = learning_rate

    def train(self, episodes, max_episode_steps,epsilon):

        for episode in episodes:

            done = False
            episode_reward = 0
            state,info = self.env.reset()
            episode_steps = 0

            episode_start_time = time.time()

            while not done and episode_steps < max_episode_steps:

                if random.random()<epsilon:
                    action = self.env.action_space.sample()

                else:
                    q_values_1 = self.model_1.forward(state.unsqueeze(0).to(self.device))[0]
                    q_values_2 = self.model_2.forward(state.unsqueeze(0).to(self.device))[0]
                    q_values = min(q_values_1,q_values_2)
                    action = torch.argmax(q_values, dim=-1).item()

                
