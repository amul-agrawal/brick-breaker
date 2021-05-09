"""
Paddle for our Brick Game
"""

from colorama import Fore, Style, Back
from config import *
import numpy as np
from generic import MovingObject
import os


class Paddle(MovingObject):

    def __init__(self):
        self.x = PADDLE_X
        self.y = PADDLE_Y
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.have_bulltet_powerup = 0
        self.powerup_start_ticks = 0

    def set_powerup_start_time(self, ticks):
        self.powerup_start_ticks = ticks

    def get_powerup_start_time(self):
        return self.powerup_start_ticks

    def set_have_bullet_powerup(self, have=1):
        self.have_bulltet_powerup = have

    def check_have_bullet_powerup(self):
        return self.have_bulltet_powerup

    def change_width(self, inc_width):
        self.width += inc_width
        # width restrictions
        self.width = min(self.width, PADDLE_WIDTH + 2*INC_PADDLE_WIDTH)
        self.width = max(self.width, PADDLE_WIDTH - 2*SHRINK_PADDLE_WIDTH)

    def get_color_string(self, i):
        segment_length = self.width // PADDLE_SEGMENTS
        i = i // segment_length
        if i % 2 == 0:
            if self.have_bulltet_powerup: 
                return Style.DIM + Back.BLACK + " "
            else:
                return Style.DIM + Back.GREEN + " "
        else:
            if self.have_bulltet_powerup: 
                return Style.DIM + Back.RED + " "
            else:
                return Style.DIM + Back.BLUE + " "

    def get_obj(self):
        return np.array([[self.get_color_string(i)
                          for i in range(self.width)]
                         for j in range(self.height)])

    def set_default(self):
        self.x = PADDLE_X
        self.y = PADDLE_Y
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.have_bulltet_powerup = 0
        self.powerup_start_ticks = 0

    def handle_key_press(self, key, ufo=None):
        if key == 'a':
            self.x -= 2
        elif key == 'd':
            self.x += 2
        else:
            return
    
        if self.x < -1 * self.width:
            self.x = FRAME_WIDTH

        if self.x > FRAME_WIDTH + self.width:
            self.x = 0

        if ufo is not None:
            ufo.set_position(self.x)
