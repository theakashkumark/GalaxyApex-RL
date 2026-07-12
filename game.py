
import time
import cv2
import torch
import numpy as np
import pygame
from obstacles import *
from spaceships import *
from utils import *
from blaze import *
import sys
import random
import math

class TreasureChest():

    def __init__(self,x,y):
        self.closed_image = pygame.image.load("images/chest_closed.png").convert_alpha()
        self.opened_image = pygame.image.load("images/chest_opened.png").convert_alpha()

        self.size = 50
        self.closed_image = pygame.transform.scale(self.closed_image, (self.size,self.size))
        self.opened_image = pygame.transform.scale(self.opened_image,(self.size,self.size))
        
        self.rect = pygame.Rect(x,y,self.size,self.size)
        self.is_opened = False

    def draw(self, screen, camera_x, camera_y):
        if self.is_opened:
            screen.blit(self.opened_image,(self.rect.x-camera_x,self.rect.y-camera_y))
        else:
            screen.blit(self.closed_image,(self.rect.x-camera_x,self.rect.y-camera_y))

class HealthDrop():

    def __init__(self, x, y):
        self.image = pygame.image.load("images/charge.png").convert_alpha()
        self.size = 30
        self.image = pygame.transform.scale(self.image, (self.size,self.size))

        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x,self.y,self.size,self.y)

    def draw(self, screen, camera_x, camera_y):
        screen.blit(self.image,(self.rect.x-camera_x,self.rect.y-camera_y))


class AlienShooter():

    def __init__(self,window_width,window_height,world_width,world_height,fps,sound=False,human=False):
        self.window_width = window_width
        self.window_height = window_height
        self.world_width = world_width
        self.world_height = world_height

        self.treasure_chest = None
        self.energy_drop = None
        
        self.paused = False
        
        self.blaze_type = 'single'
        self.fire_mode = 'single'

        pygame.init()
        self.screen = pygame.display.set_mode((window_width,window_height))

        pygame.display.set_caption("Galaxy Apex")

        self.font = pygame.font.SysFont(None,36)

        self.clock = pygame.time.Clock()
        self.fps=fps

        self.walls = walls_1

        #load images
        self.bg_image = pygame.transform.scale(pygame.image.load("images/background.jpg"), (self.world_width, self.world_height))
        self.debris_image = pygame.image.load("images/debris.png")

        self.debris = []
        for wall in self.walls:
            self.debris.append([pygame.transform.scale(self.debris_image,(wall.width,wall.height)),wall.x,wall.y])

        self.blaze_images = {}
        for dir in ['left','right','down','up']:
            img = pygame.image.load(f"images/electric_blaze_{dir}.png")
            img1 = pygame.transform.scale(img,(50,50))
            self.blaze_images[dir]=img1

        self.m_blaze_images = {}
        for dir in ['left','right','down','up']:
            img = pygame.image.load(f"images/m_blaze_{dir}.png")
            img1 = pygame.transform.scale(img,(27,27))
            self.m_blaze_images[dir]=img1

        #TO DO: Define player
        self.G_apex = GalaxyApex(self.world_width,self.world_height,self.walls)

        self.background_color = (181,101,29) 
        self.wall_color = (1,50,32)
        self.border_color = (255,0,0)

        self.annocement_font = pygame.font.SysFont(None,100)

        self.reset()

        self.sound = sound

        self.human=human

    def reset(self):
        self.done = False

        self.level = 1
        self.level_goal = 5
        self.max_drone_count = 5
        self.walls = walls_1
        self.G_apex = GalaxyApex(self.world_width,self.world_height,self.walls)
        self.G_apex_score = 0
        self.G_apex_health = 5
        self.max_drone_count = 5
        self.drone_top_speed = 1
        self.total_frames = 0
        self.last_blaze_frame = 0
        self.multi_blaze_count = 0
        self.out_of_ammo_messaged_displayed = False
        self.blaze_type = "single"

        self.blazers = []
        self.drone = []

        return self._get_obs,self._get_info


    def start_next_level(self):
        self.level+=1

        if self.level>3:
            next_level_surface = self.annocement_font.render("YOU WON!", True, (255,155,255))
        else:
            next_level_surface = self.annocement_font.render(f"Entering Level {self.level}", True, (255,155,255))
        
        next_level_rect = next_level_surface.get_rect(center=(self.window_width//2,self.window_height//2))

        self.drone = []
        self.blazers = []
        self.debris = []

        if self.level == 2:
            # TODO : play sound
            self.walls = walls_2
            self.level_goal = 10

        elif self.level == 3:
            # TODO : play sound
            self.walls = walls_3
            self.level_goal = 30

        for wall in self.walls:
                self.debris.append([pygame.transform.scale(self.debris_image,(wall.width,wall.height)),wall.x,wall.y])

        self.screen.blit(next_level_surface,next_level_rect)

        # TODO: Add loot drops
        x, y = random.randint(50,self.world_width-50), random.randint(50,self.world_height-50)
        self.treasure_chest = TreasureChest(x, y)


        self.max_drone_count += 2

        self.G_apex = GalaxyApex(self.world_width,self.world_height,self.walls)

        pygame.display.flip()
        pygame.time.wait(4000)        

        if self.level>3:
            self.done = True
            
            #sys.exit()
            #pygame.quit()

    def game_over(self):

        game_over_surface = self.annocement_font.render("GAME OVER", True, (255,155,255))

        w=game_over_surface.get_width()
        h=game_over_surface.get_height()

        self.screen.blit(game_over_surface,(self.window_width//2-w//2,self.window_height//2-h//2))

        pygame.display.flip()

        self.done = True

        pygame.time.wait(2000)

        pygame.quit()
        sys.exit()

        #if self.level>3:
        #    pygame.quit()
        #    sys.exit()
    
    def fill_background(self,camera_x,camera_y):
        self.screen.blit(self.bg_image,(0-camera_x,0-camera_y))

        score_surface = self.font.render(f"score: {self.G_apex_score}", True, (255,155,255))
        self.screen.blit(score_surface, (10,10))

        health_surface = self.font.render(f"Health : {self.G_apex_health}", True, (255,155,255))
        self.screen.blit(health_surface, (10,35))

        level_surface = self.font.render(f"Level : {self.level}", True, (255,155,255))
        self.screen.blit(level_surface, (10,60))

        ammo_surface = self.font.render(f"MultiBlaze Ammo : {self.multi_blaze_count}", True, (255,155,255))
        self.screen.blit(ammo_surface,(10,85))

        if self.out_of_ammo_messaged_displayed and self.blaze_type == "multi":
            out_of_ammo_surface = self.font.render(
                "Out of Multi Blaze ammo! press TAB to switch to a single shot", True, (255,155,255)
            )
            out_of_ammo_cent = out_of_ammo_surface.get_rect(center=(self.window_width//2,self.window_height//2))
            self.screen.blit(out_of_ammo_surface,out_of_ammo_cent)


    #firing mode or blazing mode
    def fire_single_blaze(self):
        if self.G_apex.direction=='left' or self.G_apex.direction=='right':
            blaze = SingleBlaze(self.G_apex.rect.centerx,self.G_apex.rect.centery-20,self.G_apex.direction,self.blaze_images)
        else:
            blaze = SingleBlaze(self.G_apex.rect.centerx-20,self.G_apex.rect.centery,self.G_apex.direction,self.blaze_images)           
        self.blazers.append(blaze)

        #TODO : add sound
        
    def fire_multi_blaze(self):
        if self.multi_blaze_count>0:
            directions = [
                (self.G_apex.direction,0),
                (self.G_apex.direction,math.radians(13)),
                (self.G_apex.direction,math.radians(-13))
            ]

            for direction,angle_offset in directions:
                if self.G_apex.direction == "left" or self.G_apex.direction == "right":
                    blaze=MultiBlaze(self.G_apex.rect.centerx,self.G_apex.rect.centery-20,direction,angle_offset,self.m_blaze_images)
                else:
                    blaze=MultiBlaze(self.G_apex.rect.centerx-20,self.G_apex.rect.centery,direction,angle_offset,self.m_blaze_images)
                self.blazers.append(blaze)

            self.multi_blaze_count-=1
            self.out_of_ammo_messaged_displayed=False

            print('!bam bam bam')

            #TODO : add sound

        else:
            print("out of multi blaze ammo")
            self.out_of_ammo_messaged_displayed=True
    
    def _get_info(self):

        blaze_type_num= 1 if self.blaze_type == 'single' else 2

        return {
            "health": self.G_apex_health,
            "multiblaze_ammo": self.multi_blaze_count,
            "blaze_type": blaze_type_num,
            "blazes": len(self.blazers) 
        }
    
    def _get_obs(self):

        screen_array = pygame.surfarray.pixels3d(self.screen)

        screen_array = np.transpose(screen_array, (1, 0, 2))

        downscaled_image = cv2.resize(screen_array, (128, 128), interpolation = cv2.INTER_NEAREST)

        grayscale = cv2.cvtColor(downscaled_image, cv2.COLOR_RGB2GRAY)
        print(grayscale)

        observation = torch.from_numpy(grayscale).float().unsqueeze(0)

        return observation



    def toggle_pause(self):
        #complete toggle pass method
        pass
        
    def step(self, action, repeat=4):

        total_reward = 0
        for _ in range(repeat):
            reward, done, truncated = self._step(action)
            total_reward+=reward

            if action==6:
                action = 0

            if done == True:
                break

        return self._get_obs(), total_reward, done, truncated, self._get_info()
            

    def _step(self,action):

        self.total_frames+=1

        up = True if action == 1 else False
        down = True if action == 2 else False
        left = True if action == 3 else False
        right = True if action == 4 else False
        #will do stwich gun 
        fire = True if action == 6 else False
        pause = False

        reward, truncated = 0, False

        if fire and (self.total_frames-self.last_blaze_frame>10):
            self.fire_single_blaze()
            self.last_blaze_frame=self.total_frames
            
        if self.paused:
            return
        
        player_moved = False

        if len(self.drone)<self.max_drone_count and random.randint(0,100)<3:
            self.drone.append(AlienDrone(self.world_width,self.world_height,size=80,speed=random.randint(1,self.drone_top_speed)))

        new_G_apex_y = self.G_apex.y

        if up:
            new_G_apex_y -= self.G_apex.speed
            self.G_apex.direction = 'up'
        elif down:
            new_G_apex_y += self.G_apex.speed
            self.G_apex.direction = 'down'

        G_apex_rect = pygame.Rect(self.G_apex.x,new_G_apex_y,self.G_apex.size,self.G_apex.size)

        collision = check_collision(G_apex_rect,self.walls)

        if not collision and new_G_apex_y != self.G_apex.y and 0<=new_G_apex_y<=self.world_height-self.G_apex.size:
            self.G_apex.y=new_G_apex_y

        #TODO : walking sound

        new_G_apex_x = self.G_apex.x

        if left:
            new_G_apex_x-=self.G_apex.speed
            self.G_apex.direction = 'left'
        elif right:
            new_G_apex_x+=self.G_apex.speed
            self.G_apex.direction = 'right' 

        G_apex_rect = pygame.Rect(new_G_apex_x,self.G_apex.y,self.G_apex.size,self.G_apex.size)

        collision = check_collision(G_apex_rect,self.walls)

        if not collision and self.G_apex.x != new_G_apex_x and 0<=new_G_apex_x<=self.world_width-self.G_apex.size :
            self.G_apex.x = new_G_apex_x

        self.G_apex.rect = pygame.Rect(self.G_apex.x, self.G_apex.y, self.G_apex.size, self.G_apex.size)

        collision = False

        camera_x = self.G_apex.x - self.window_width // 2
        camera_y = self.G_apex.y - self.window_height // 2

        camera_x = max(0, min(camera_x, self.world_width - self.window_width))
        camera_y = max(0, min(camera_y, self.world_height - self.window_height))

        self.temp_drone=[]

        for dron in self.drone:
            if check_collision(dron.rect,self.blazers):
                blazer = get_collision(dron.rect,self.blazers)
                self.blazers.remove(blazer)
                self.G_apex_score+=1
                reward += 1

                if random.randint(0,100)<=20:
                    self.energy_drop = HealthDrop(dron.rect.x,dron.rect.y)

            elif check_collision(dron.rect,[self.G_apex]):
                self.G_apex_health -= 1
                reward -= 1
            
            else:
                self.temp_drone.append(dron)

        self.drone=self.temp_drone

        for dron in self.drone:
            dron.move_towards_player(self.G_apex.x,self.G_apex.y,self.walls)

        self.fill_background(camera_x,camera_y)

        self.G_apex.draw(self.screen,camera_x,camera_y)

        #TODO : bullet logic
        new_blazers = []
        for blaze in self.blazers:
            blaze.move()
            blaze.draw(self.screen,camera_x,camera_y)

            if check_collision(blaze.rect,self.walls)==False:
                new_blazers.append(blaze)
        
        self.blazers = new_blazers

        for drone in self.drone:
            drone.draw(self.screen,camera_x,camera_y)

        for debri in self.debris:
            self.screen.blit(debri[0],(debri[1]-camera_x,debri[2]-camera_y))

        if self.treasure_chest:
            self.treasure_chest.draw(self.screen,camera_x,camera_y)

        if self.treasure_chest and self.G_apex.rect.colliderect(self.treasure_chest.rect):
            if not self.treasure_chest.is_opened:
                self.treasure_chest.is_opened = True
                reward += 1

                self.multi_blaze_count = min(self.multi_blaze_count+5,20)
                print(f"Multi Blaze refilled! Current Blaze : {self.multi_blaze_count}")
            
        if self.energy_drop:
            self.energy_drop.draw(self.screen,camera_x,camera_y)
        
        if self.energy_drop and self.G_apex.rect.colliderect(self.energy_drop.rect):
            self.energy_drop=None
            self.G_apex_health+=1
            reward += 1

        if self.G_apex_score>self.level_goal:
            self.start_next_level()
        
        if self.G_apex_health<=0:
            self.game_over()

        pygame.display.flip()

        if self.human:
            self.clock.tick(self.fps)
        else:
            self.clock.tick()

        return reward, self.done, truncated