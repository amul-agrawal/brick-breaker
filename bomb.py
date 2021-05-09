"""
This is the ball in our game
"""

from colorama import Fore, Style, Back
import random 
from config import *
import numpy as np
from time import sleep
from generic import MovingObject
from utils import check_intersection
import os

class Bomb(MovingObject):

    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y 
        self.width = 1
        self.height = 1
        self.vy = 1
        self.is_active = 1
        self.slow = 0

    def set_active(self, active):
        self.is_active = active
        
    def check_active(self):
        return self.is_active

    def get_velocity(self):
        return self.vx, self.vy
    
    def get_obj(self):
        return np.array([[  Fore.YELLOW + Back.LIGHTBLACK_EX + "O"
                            for i in range(self.width)]
                            for j in range(self.height)])

    def check_paddle_collission(self, paddle):
        if not self.is_active:
            return 0
        if check_intersection(self, paddle):
            self.is_active = 0
            return 1
        return 0

    # Update position of ball and handle collission
    def update(self):
        if not self.is_active:
            return
        self.slow += 1
        if not (self.slow % 3 == 0):
            return 

        self.y += self.vy

        if self.y == FRAME_HEIGHT:
            self.is_active = 0

    