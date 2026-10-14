from utils import *
from game import AlienShooter
from agent import Agent 

epsiodes = 10000
max_epsiode_steps = 10000
total_steps = 0
step_repaet = 4
max_epsiode_steps = max_epsiode_steps/step_repaet

batch_size = 64
learning_rate = 0.0001
epsilon = 1
min_epsilon = 0.1
epsilon_decay = 0.995
gamma = 0.99

hidden_layer = 1024
dropout = 0.2

WINDOW_WIDTH, WINDOW_HEIGHT = 1200,800
WORLD_WIDTH,WORLD_HEIGHT = 1800,1200
FPS = 60

env = AlienShooter(window_width=WINDOW_WIDTH, window_height=WINDOW_HEIGHT,
                   world_height=WORLD_HEIGHT,world_width=WORLD_WIDTH,
                   fps=FPS, sound=False)

summary_writer_suffix = f"dqn_lr={learning_rate}_h1={hidden_layer}_batch_size={batch_size}_dropout={dropout}"

agent = Agent(env, dropout=dropout, hidden_layer=hidden_layer
              learning_rate=learning_rate step_repeat=step_repaet,
              gamma=gamma)

agent.train(epsiodes=epsiodes, max_episode_steps=max_epsiode_steps, summary_writer_suffix=summary_writer_suffix,
            batch_size=batch_size, epsilon=epsilon, epsilon_decay=epsilon_decay, min_epsilon=min_epsilon)