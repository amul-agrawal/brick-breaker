"""
UFO: The Best Devil
"""

from colorama import Fore, Style, Back
from config import *
import numpy as np
from generic import MovingObject
import os

class Ufo(MovingObject):

    def __init__(self):
        self.x = PADDLE_X
        self.y = UFO_Y
        self.width = UFO_WIDTH
        self.height = UFO_HEIGHT
        self.health = UFO_HEALTH
        self.drop_bomb_counter = 0
        self.is_critical = 0
        self.is_active = 1
        
    def check_active(self):
        return self.is_active
    
    def can_drop_bomb(self):
        self.drop_bomb_counter += 1
        if self.drop_bomb_counter % 200 == 0:
            return 1
        else:
            return 0

    def get_obj(self):
        return np.array([[ Back.BLACK + UFO_STRUCTURE[j][i] if j != 0 
                            else 
                                Style.BRIGHT + Fore.WHITE + Back.LIGHTBLACK_EX +UFO_STRUCTURE[j][i] 
                            for i in range(self.width)]
                            for j in range(self.height)])
    
    def set_position(self, x):
        self.x = x
    
    def get_x(self):
        return self.x
    
    def get_health(self):
        return self.health

    def check_critical(self):
        return self.is_critical

    def dec_health(self):
        self.health -= 1
        if self.health == 0:
            self.is_active = 0
            return 1
        if self.health <= 2:
            self.is_critical = 1

        return 0
