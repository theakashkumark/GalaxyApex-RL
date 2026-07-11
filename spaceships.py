import random
import pygame
import math
from utils import *

class GalaxyApex:

    def __init__(self,world_width,world_height,walls):

        self.size = 80
        self.speed = 5

        self.rect = None

        self.x = world_width//2
        self.y = world_height//2

        while True:

            self.rect = pygame.Rect(self.x,self.y,self.size,self.size)
            
            if check_collision(self.rect,walls):
                self.x += random.randint(-5,5)
                self.y += random.randint(-5,5)
            else:
                break
        
        self.score = 0
        self.ammo = 10
        self.health = 5

        self.images = {}

        for dir in ('up','right','down','left'):
            image = pygame.image.load(f'images/predator_{dir}.png')
            self.images[dir] = pygame.transform.scale(image,(self.size,self.size))
        
        self.direction = 'up'

    def draw(self, screen, camera_x, camera_y):
        screen.blit(self.images[self.direction],(self.x-camera_x, self.y-camera_y))

class AlienDrone:

    def __init__(self, world_width, world_height, size=50, speed=1):

        self.world_width = world_width
        self.world_height = world_height
        self.size=size
        self.speed=speed

        self.x,self.y = self.spawn()

        self.images = {}

        for dir in ('up','right','down','left'):
            image = pygame.image.load(f"images/drone_{dir}.png")
            self.images[dir] = pygame.transform.scale(image,(self.size,self.size))

        self.direction = 'right'

        self.rect = pygame.Rect(0,0,self.size,self.size)
        self.rect.center =  (self.x,self.y)

    def move_towards_player(self, player_x, player_y, walls):

        dx,dy = player_x-self.x,player_y-self.y

        distance = math.hypot(dx,dy)

        if distance!=0:
            dx,dy = dx/distance, dy/distance

        #try horizontal dist
        new_x = self.x + dx*self.speed
        new_rect = pygame.Rect(new_x,self.y,self.size,self.size)
        can_move_x = not check_collision(new_rect,walls)

        if can_move_x:
            self.x = new_x
        else:
            new_y = self.y + dy*self.speed + 2
            new_rect = pygame.Rect(self.x,new_y,self.size,self.size)
            if(not check_collision(new_rect,walls)):
                self.y=new_y

        #try vertical dist
        new_y = self.y + dy*self.speed
        new_rect = pygame.Rect(self.x,new_y,self.size,self.size)
        can_move_y = not check_collision(new_rect,walls)

        if can_move_y:
            self.y = new_y
        else:
            new_x = self.x + dx*self.speed + 2
            new_rect = pygame.Rect(new_x,self.y,self.size,self.size)
            if(not check_collision(new_rect,walls)):
                self.x=new_x

        #update position and direction
        self.rect.topleft = (self.x,self.y)

        if abs(dx)>abs(dy):
            if dx>0:
                self.direction='right'
            else:
                self.direction='left'
        else:
            if dy>0:
                self.direction='down'
            else:
                self.direction='up'

    def spawn(self):
        spawn_positions=[
            (random.randint(0,self.world_width-self.size),0),
            (random.randint(0,self.world_width-self.size),self.world_height),
            (0,random.randint(0,self.world_height-self.size)),
            (self.world_width,random.randint(0,self.world_height-self.size)),
        ]

        return random.choice(spawn_positions)
    
    def draw(self,screen,camera_x,camera_y):
        screen.blit(self.images[self.direction],(self.x-camera_x,self.y-camera_y))
