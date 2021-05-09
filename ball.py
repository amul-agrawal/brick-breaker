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

class Ball(MovingObject):

    def __init__(self, *args, **kwargs):
        # Ball will spawn just above paddle
        super().__init__()
        if kwargs.get("paddle"):
            paddle = kwargs.get("paddle")
            (p_x, p_y, p_width, p_height) = paddle.get_box()
            self.x = random.randint(p_x, p_x + p_width)
            self.y = p_y - 1
            self.width = 1
            self.height = 1
            self.vx = 0
            self.vy = 1
            self.type = NORMAL_BALL
            self.grabbable = 0
            self.grabbed = 0
            self.is_active = 1
            self.state = BALL_HOLD
            self.slow = 0
            self.on_fire = 0
        # Ball divided
        else:
            self.width = 1
            self.height = 1
            self.is_active = 1
            self.type = NORMAL_BALL
            self.grabbed = 0
            self.grabbable = 0
            self.state = BALL_RELEASED
            self.slow = 0
            self.on_fire = 0


    def set_fire(self):
        self.on_fire = 1
    
    def check_fire(self):
        return self.on_fire

    def unset_grabbable(self):
        self.grabbable = 0
    
    def unset_grabbed(self):
        self.grabbed = 0
        
    def set_grabbable(self):
        self.grabbable = 1

    def get_velocity(self):
        return self.vx, self.vy
    
    def get_grabbable(self):
        return self.grabbable 

    def set_type(self, Type):
        self.type = Type
    
    def get_type(self):
        return self.type
    
    def inc_speed(self, m):
        self.vx *= 2
        self.vy *= 2
        self.vx = max(-2, self.vx)
        self.vx = min(2, self.vx)
        self.vy = max(-2, self.vy)
        self.vy = min(2, self.vy)

    def set_state(self, state):
        self.state = state


    def _which_segment(self, paddle, x):
        # get paddle segment on which it landed
        (p_x, p_y, p_width, p_height) = paddle.get_box()
        x -= p_x
        segment_width = p_width // PADDLE_SEGMENTS
        x //= segment_width
        return x

    def hit_paddle(self, paddle, x, y):

        (p_x, p_y, p_width, p_height) = paddle.get_box()
        # not over paddle
        if y != p_y - 1:
            return 
        
        if x < p_x or x > p_x + p_width:
            return 

        self.vx += (self._which_segment(paddle, self.x) - 2)
        self.vx = max(-2, self.vx)
        self.vx = min(2, self.vx)
        self.vy *= -1

    
    def change_velocity(self, fac_x, fac_y):
        self.vx *= fac_x
        self.vy *= fac_y
        self.vx = max(-2, self.vx)
        self.vx = min(2, self.vx)
        self.vy = max(-2, self.vy)
        self.vy = min(2, self.vy)

    def get_obj(self):

        if self.on_fire:   
            return np.array([[  Fore.YELLOW + Back.LIGHTBLACK_EX + "O"
                            for i in range(self.width)]
                            for j in range(self.height)])
        else:
            return np.array([[  Fore.CYAN + Back.LIGHTBLACK_EX + "O"
                            for i in range(self.width)]
                            for j in range(self.height)])
    # Ball release on space bar
    def handle_key_press(self, paddle, key):

        # print(f"h1 {key}")
        if key == " " and self.state == BALL_HOLD:
            self.state = BALL_RELEASED
            self.hit_paddle(paddle, self.x, self.y)
        
        if key == " " and self.grabbed:
            self.grabbed = 0
        
        if self.grabbed:
            if key == 'a':
                # print("here")
                self.x -= 2
            elif key == 'd':
                self.x += 2
            
            if self.x < -1 * self.width:
                self.x = FRAME_WIDTH
            
            if self.x > FRAME_WIDTH + self.width:
                self.x = 0

    def check_wall_collission(self):
        if self.x < 0:
            os.system('aplay -q ./sounds/paddle_bounce.wav& 2>/dev/null')
            self.x = 0
            self.vx *= -1

        # right wall
        if self.x >= FRAME_WIDTH:
            os.system('aplay -q ./sounds/paddle_bounce.wav& 2>/dev/null')
            self.x = FRAME_WIDTH - 1
            self.vx *= -1  
        
        # up wall
        if self.y < 0:
            os.system('aplay -q ./sounds/paddle_bounce.wav& 2>/dev/null')
            self.y = 0
            self.vy *= -1

        # down wall
        if self.y >= FRAME_HEIGHT:
            self.is_active = 0
            self.state = BALL_LOST

    def check_paddle_collission(self, paddle):
        (p_x, p_y, p_width, p_height) = paddle.get_box()
        if  p_y <= self.y < p_y + p_height:
            if p_x <= self.x < p_x + p_width:
                os.system('aplay -q ./sounds/paddle_bounce.wav& 2>/dev/null')
                if self.grabbed:
                    return 1

                if self.vy > 0:
                    # upper collision
                    self.y = p_y - 1
                    # velocity change
                    self.hit_paddle(paddle, self.x, self.y)
                    if self.grabbable:
                        self.grabbed = 1
                        
                else:
                    # bottom collision
                    self.y = p_y + p_height
                    self.hit_paddle(paddle, self.x, self.y)

                return 1
        return 0
    
    def check_ufo_collission(self, ufo):

        if not check_intersection(self, ufo):
            return 0
        
        os.system('aplay -q ./sounds/paddle_bounce.wav& 2>/dev/null')

        (u_x, u_y, u_width, u_height) = ufo.get_box()
        old_x = self.x - self.vx
        old_y = self.y - self.vy

        if self.vx == 0:
            if self.vy > 0:
                # Down
                self.y = u_y - 1
                self.vy *= -1
                is_destroyed = ufo.dec_health()
                return is_destroyed
            else:
                # up
                self.y = u_y + u_height 
                self.vy *= -1
                is_destroyed = ufo.dec_health()
                return is_destroyed
        
        if self.vy == 0:
            if self.vx > 0:
                # right
                self.x = u_x - 1
                self.vx *= -1
                is_destroyed = ufo.dec_health()
                return is_destroyed
            else:
                # left
                self.x = u_x + u_width 
                self.vx *= -1
                is_destroyed = ufo.dec_health()
                return is_destroyed
        
        if self.vx < 0 and self.vy < 0:
            # top left movement
            if old_x >= u_x + u_width:
                # right wall collission
                self.vx *= -1
                self.x = u_x + u_width
                is_destroyed = ufo.dec_health()
                return is_destroyed
            else:
                # bottom wall collision
                self.vy *= -1
                self.y = u_y + u_height
                is_destroyed = ufo.dec_health()
                return is_destroyed
        
        if self.vx > 0 and self.vy < 0:
            # top right movement
            if old_x < u_x:
                # left wall collission
                self.vx *= -1
                self.x = u_x - 1
                is_destroyed = ufo.dec_health()
                return is_destroyed
            else:
                # bottom wall collision
                self.vy *= -1
                self.y = u_y + u_height
                is_destroyed = ufo.dec_health()
                return is_destroyed
        
        if self.vx < 0 and self.vy > 0:
            # bottom left movement
            if old_x >= u_x + u_width:
                # right wall collission
                self.vx *= -1
                self.x = u_x + u_width
                is_destroyed = ufo.dec_health()
                return is_destroyed
            else:
                # top wall collision
                self.vy *= -1
                self.y = u_y - 1
                is_destroyed = ufo.dec_health()
                return is_destroyed

        if self.vx > 0 and self.vy > 0:
            # top right movement
            if old_x < u_x:
                # left wall collission
                self.vx *= -1
                self.x = u_x - 1
                is_destroyed = ufo.dec_health()
                return is_destroyed
            else:
                # top wall collision
                self.vy *= -1
                self.y = u_y - 1
                is_destroyed = ufo.dec_health()
                return is_destroyed

        return 0
        
    # Update position of ball and handle collission
    def update(self):
        if self.state == BALL_HOLD or not self.is_active:
            return
        if not self.grabbed:
            self.slow += 1
            if self.slow % 2 == 0:
                self.x += self.vx
                self.y += self.vy

    