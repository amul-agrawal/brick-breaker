"""
PowerUps: Catch these to boost your strengths
"""
import numpy as np
from config import *
from colorama import Fore, Back, Style
from generic import MovingObject

class PowerUp(MovingObject):
    def __init__(self, x, y, vx, vy, Type):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.gravity = 1
        self.width = 1
        self.height = 1
        self.Type = Type
        self.is_active = 1
        self.cnt = 0
        self.slow = 0

    def get_string(self, Type):
        if Type == POWERUP_EXPAND_PADDLE:
            return Fore.BLACK + Back.LIGHTYELLOW_EX + "E" + Style.RESET_ALL
        elif Type == POWERUP_SHRINK_PADDLE:
            return Fore.BLACK + Back.LIGHTYELLOW_EX + "S" + Style.RESET_ALL
        elif Type == POWERUP_FAST_BALL:
            return Fore.BLACK + Back.LIGHTYELLOW_EX + "F" + Style.RESET_ALL
        elif Type == POWERUP_BALL_MULITIPLIER:
            return Fore.BLACK + Back.LIGHTYELLOW_EX + "M" + Style.RESET_ALL
        elif Type == POWERUP_THRU_BALL:
            return Fore.BLACK + Back.LIGHTYELLOW_EX + "T" + Style.RESET_ALL
        elif Type == POWERUP_GRAB_BALL:
            return Fore.BLACK + Back.LIGHTYELLOW_EX + "G" + Style.RESET_ALL
        elif Type == POWERUP_SHOOTING_BULLET:
            return Fore.BLACK + Back.LIGHTYELLOW_EX + "B" + Style.RESET_ALL
        elif Type == POWERUP_FIREBALL:
            return Fore.BLACK + Back.LIGHTYELLOW_EX + "L" + Style.RESET_ALL
        else:
            print(Type)

    def get_obj(self):
        return np.array([[  self.get_string(self.Type) 
                            for i in range(self.width)]
                            for j in range(self.height)])

    def check_wall_collission(self):
        if not self.is_active:
            return 

        if self.x < 0:
            self.x = 0
            self.vx *= -1

        # right wall
        if self.x >= FRAME_WIDTH:
            self.x = FRAME_WIDTH - 1
            self.vx *= -1  
        
        # up wall
        if self.y < 0:
            self.y = 0
            self.vy *= -1

        # down wall
        if self.y >= FRAME_HEIGHT:
            self.is_active = 0
            self.is_active = 0


    def get_type(self):
        return self.Type

    def deactivate(self):
        self.is_active = 0

    def update_vy(self):
        self.cnt += 1
        if self.cnt % 10 == 0:
            self.vy += self.gravity
            self.vy = max(-2, self.vy)
            self.vy = min(2, self.vy)

    def update(self):
        self.slow += 1
        if self.slow % 3 == 0:
            return 
        self.y += self.vy
        self.x += self.vx

        self.update_vy()


        if self.y >= FRAME_HEIGHT:
            self.is_active = 0
