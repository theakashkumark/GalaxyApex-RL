from game import AlienShooter
import pygame
import sys
import torch
import numpy as np 
import cv2

window_width,window_height = 1200,800
world_width,world_height = 1800,1200
fps=60

game = AlienShooter(window_width=window_width,window_height=window_height,world_height=world_height,world_width=world_width,fps=fps,sound=True,human=True)

while True:

    action = 0

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type==pygame.KEYDOWN:
            if event.key==pygame.K_TAB:
                action = 5    
            elif event.key==pygame.K_SPACE:
                action = 6
            elif event.key==pygame.K_ESCAPE:
                action = 7

    keys = pygame.key.get_pressed()

    if action == 0:
        if keys[pygame.K_w]:
            action = 1
        if keys[pygame.K_s]:
            action = 2
        if keys[pygame.K_a]:
            action=  3
        if keys[pygame.K_d]:
            action = 4

    observation, reward, done, truncated, info = game.step(action=action)

    if reward!=0:
        print("Reward: ",reward)
        print("Done: ",done)

        img_array = torch.clip(observation.squeeze(0),0,255).numpy().astype(np.uint8)
        result = cv2.imwrite("temp/screen.jpg",img_array)
    