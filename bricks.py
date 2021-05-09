"""
Bricks/Obstacles for our game
"""
import numpy as np
from colorama import Fore, Style, Back
from config import *
from time import sleep
from generic import StationaryObject
from utils import check_intersection
import os

def get_brick_color(id):
    if int(id) == WEAK_BRICK_ID:
        return WEAK_BRICK_COLOR
    elif int(id) == NORMAL_BRICK_ID:
        return NORMAL_BRICK_COLOR
    elif int(id) == STRONG_BRICK_ID:
        return STRONG_BRICK_COLOR
    elif int(id) == UNBREAKABLE_BRICK_ID:
        return UNBREAKABLE_BRICK_COLOR
    elif int(id) == EXPLODING_BRICK_ID:
        return EXPLODING_BRICK_COLOR
    else:
        return ""

class BaseBrick(StationaryObject):
    def __init__(self, x, y,i, j, health, color, id):
        self.i = i
        self.j = j
        self.x = x
        self.y = y
        self.width = BRICK_WIDTH
        self.height = BRICK_HEIGHT
        self.is_active = 1
        self.health = health
        self.color = color
        self.contact = 0
        self.id = id
        self.y_fall = 0

    def get_obj(self):
        return np.array([[  self.color + " "
                            for i in range(self.width)]
                            for j in range(self.height)])
    
    def set_y_fall(self, y_fall):
        self.y_fall = y_fall

    def set_x(self, x):
        if not self.is_active:
            return 
        self.x = x

    def get_box(self):
        return self.x, self.y + self.y_fall, self.width, self.height

    # returns 1 on brick destruction
    def dec_health(self, Type=None):
        if not self.is_active:
            return 0

        if Type and Type == THRU_BALL:
            self.is_active = 0
            if self.health > 0:
                self.health = 0
            return 1


        if self.health == -1:
            return 0

        self.health -= 1
        if self.health == 0:
            os.system('aplay -q ./sounds/explosion.wav&')
            self.is_active = 0
            return 1
        else:
            os.system('aplay -q ./sounds/paddle_bounce.wav& 2>/dev/null')
            self.id -= 1
            self.color = get_brick_color(self.id)
            return 0
    
    def destroy(self):
        if self.id == UNBREAKABLE_BRICK_ID:
            return
        self.health = 0
        self.is_active = 0


    def handle_collission_bullet(self, bullet):
        if not self.is_active:
            return 0

        if check_intersection(bullet, self):
            bullet.set_active(0)
            is_destroyed = self.dec_health()
            return is_destroyed
        else:
            return 0 

    # returns 1 on brick destruction
    def handle_collission(self, ball, bricks = None):
        if not self.is_active:
            return 0

        b_x, b_y, b_width, b_height = ball.get_box()
        if b_x >= self.x + self.width or b_x + b_width <= self.x:
            return 0
        if b_y >= self.y + self.height + self.y_fall or b_y + b_height <= self.y + self.y_fall:
            return 0

        if not check_intersection(ball, self):
            return 0
        else:
            self.contact = 1

        # colliding
        if ball.get_type() == THRU_BALL:
            is_destroyed = self.dec_health(ball.get_type())
            return is_destroyed


        b_vx, b_vy = ball.get_velocity()
        old_x = b_x - b_vx
        old_y = b_y - b_vy

        is_destroyed = 0

        if b_vx == 0:
            if b_vy > 0:
                ball.set_y(self.y + self.y_fall-1)
                ball.change_velocity(1, -1)
                is_destroyed = self.dec_health(ball.get_type())
            else:
                ball.set_y(self.y + self.y_fall + self.height)
                ball.change_velocity(1, -1)
                is_destroyed = self.dec_health(ball.get_type())
        
        if b_vy == 0:
            if b_vx > 0:
                ball.set_x(self.x-1)
                ball.change_velocity(-1, 1)
                is_destroyed = self.dec_health(ball.get_type())
            else:
                ball.set_x(self.x+self.width)
                ball.change_velocity(-1, 1)
                is_destroyed = self.dec_health(ball.get_type())

        if b_vx < 0 and b_vy < 0:
            # top left movement
            if old_x >= self.x + self.width:
                # right wall collission
                ball.change_velocity(-1, 1)
                ball.set_x(self.x + self.width)
                is_destroyed = self.dec_health(ball.get_type())
            else:
                # bottom wall collision
                ball.change_velocity(1, -1)
                ball.set_y(self.y + self.y_fall + self.height)
                is_destroyed = self.dec_health(ball.get_type())
        
        if b_vx > 0 and b_vy < 0:
            # top right movement
            if old_x < self.x:
                # left wall collission
                ball.change_velocity(-1, 1)
                ball.set_x(self.x - 1)
                is_destroyed = self.dec_health(ball.get_type())
            else:
                # bottom wall collision
                ball.change_velocity(1, -1)
                ball.set_y(self.y + self.y_fall + self.height)
                is_destroyed = self.dec_health(ball.get_type())
        
        if b_vx < 0 and b_vy > 0:
            # bottom left movement
            if old_x >= self.x + self.width:
                # right wall collission
                ball.change_velocity(-1, 1)
                ball.set_x(self.x + self.width)
                is_destroyed = self.dec_health(ball.get_type())
            else:
                # top wall collision
                ball.change_velocity(1, -1)
                ball.set_y(self.y + self.y_fall - 1)
                is_destroyed = self.dec_health(ball.get_type())
        
        if b_vx > 0 and b_vy > 0:
            # bottom right movement
            if old_x < self.x:
                # left wall collission
                ball.change_velocity(-1, 1)
                ball.set_x(self.x - 1)
                is_destroyed = self.dec_health(ball.get_type())
            else:
                # top wall collision
                ball.change_velocity(1, -1)
                ball.set_y(self.y + self.y_fall - 1)
                is_destroyed = self.dec_health(ball.get_type())

        if not is_destroyed or (not ball.check_fire()) or self.i == -1:
            return is_destroyed

        Is = [-1, 1, 0, 0]
        Js = [0, 0, -1, 1]
        for idx in range(4):
            ni = self.i + Is[idx]
            nj = self.j + Js[idx]
            
            if bricks[ni][nj] != 'X':
                bricks[ni][nj].destroy()               

        return is_destroyed

class WeakBrick(BaseBrick):
    def __init__(self, x, y, i = -1, j = -1):
        super().__init__(x, y,i, j, WEAK_BRICK_HEALTH, WEAK_BRICK_COLOR, WEAK_BRICK_ID)
    
    def get_type(self):
        return WEAK_BRICK_ID
        

class NormalBrick(BaseBrick):
    def __init__(self, x, y, i = -1, j = -1):
        super().__init__(x, y,i, j, NORMAL_BRICK_HEALTH, NORMAL_BRICK_COLOR, NORMAL_BRICK_ID)
    
    def get_type(self):
        return NORMAL_BRICK_ID

class StrongBrick(BaseBrick):
    def __init__(self, x, y, i = -1, j = -1):
        super().__init__(x, y,i, j, STRONG_BRICK_HEALTH, STRONG_BRICK_COLOR, STRONG_BRICK_ID)
    
    def get_type(self):
        return STRONG_BRICK_ID

class UnbreakableBrick(BaseBrick):
    def __init__(self, x, y, i = -1, j = -1):
        super().__init__(x, y,i, j, -1, UNBREAKABLE_BRICK_COLOR, UNBREAKABLE_BRICK_ID)
    
    def get_type(self):
        return UNBREAKABLE_BRICK_ID

class ExplodingBrick(BaseBrick):
    def __init__(self, x, y, i = -1, j = -1):
        super().__init__(x, y,i, j, EXPLODING_BRICK_HEALTH, EXPLODING_BRICK_COLOR, EXPLODING_BRICK_ID)
    
    def get_type(self):
        return EXPLODING_BRICK_ID

class RainbowBrick(BaseBrick):
    def __init__(self, x, y, i = -1, j = -1):
        super().__init__(x, y,i, j, WEAK_BRICK_HEALTH, WEAK_BRICK_COLOR, WEAK_BRICK_ID)

    def change_type(self):
        if self.contact == 0:
            if self.id == WEAK_BRICK_ID:
                self.id = NORMAL_BRICK_ID
                self.health = NORMAL_BRICK_HEALTH
                self.color = NORMAL_BRICK_COLOR
            elif self.id == NORMAL_BRICK_ID:
                self.id = STRONG_BRICK_ID
                self.health = STRONG_BRICK_HEALTH
                self.color = STRONG_BRICK_COLOR
            else:
                self.id = WEAK_BRICK_ID
                self.health = WEAK_BRICK_HEALTH
                self.color = WEAK_BRICK_COLOR
        
    def get_obj(self):
        self.change_type()
        return np.array([[  self.color + " "
                            for i in range(self.width)]
                            for j in range(self.height)])   
    
    def get_type(self):
            return RAINBOW_BRICK_ID