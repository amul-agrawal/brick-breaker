"""
This is the ball in our game
"""

from colorama import Fore, Style, Back
import random 
from config import *
import numpy as np
from time import sleep
from generic import MovingObject
import os

class Bullet(MovingObject):

    def __init__(self, x, y, vy):
        # Ball will spawn just above paddle
        super().__init__()
        os.system('aplay -q ./sounds/bullet.wav& 2>/dev/null')
        self.x = x
        self.y = y 
        self.width = 1
        self.height = 1
        self.vx = 0
        self.vy = vy
        self.is_active = 1
        self.slow = 0

    def set_active(self, active):
        self.is_active = active
        
    def check_active(self):
        return self.is_active

    def get_velocity(self):
        return self.vx, self.vy
    
    def get_obj(self):
        return np.array([[  Fore.GREEN + Back.LIGHTBLACK_EX + "O"
                            for i in range(self.width)]
                            for j in range(self.height)])


    def check_wall_collission(self):
        if self.x < 0:
            self.is_active = 0

        # right wall
        if self.x >= FRAME_WIDTH:
            self.is_active = 0
            
        # up wall
        if self.y < 0:
            self.is_active = 0

        # down wall
        if self.y >= FRAME_HEIGHT:
            self.is_active = 0

        
    # Update position of ball and handle collission
    def update(self):
        if not self.is_active:
            return

        self.slow += 1
        if self.slow % 2 == 0:
            self.x += self.vx
            self.y += self.vy

    