"""
The actual game and rendering related functions
"""

import os
import random
import math
import time
import numpy as np
from colorama import init as coloroma_init, Fore, Style, Back
from config import *
from utils import clear_terminal_screen, check_intersection
from paddle import Paddle
from ball import Ball
from powerups import PowerUp
from kbhit import KBHit
from bricks import WeakBrick, NormalBrick, StrongBrick, UnbreakableBrick, ExplodingBrick, RainbowBrick
from bullet import Bullet
from ufo import Ufo
from bomb import Bomb


class Game:
    """
    The actual game and rendering related functions
    """

    _refresh_time = 1 / FRAME_RATE

    # DECLARING EVERYTHING
    def __init__(self):
        coloroma_init(autoreset=False)
        self.__score = 0
        self.__last_level_score = 0
        self.__ticks = 0
        self.__level_ticks = 0
        self.__level = 1
        self.__lives_used = 0
        self.__paddle = Paddle()
        self.__bricks_broken = 0
        self.__balls = [Ball(paddle=self.__paddle)]
        self.__cnt_active_balls = 0
        self.__cnt_active_bricks = 100
        self.__game_status = GAME_END
        self.__powerups = []
        self.__kb = KBHit()
        self.__explode_ids = [x for x in range(8, 14)]
        self.__explode_nbrs_ids = [7, 14, 28, 29, 30, 31, 32, 33]
        self.__brick_structure_y_fall = 0
        self.__fall_bricks = 0
        self.__bullets = []
        self.__ufo = Ufo()
        self.__ufo_bombs = []
        self.__ufo_bricks = []
        self.__map_position_to_bricks = []

        clear_terminal_screen()
        self._draw_bricks()
        self._loop()

    # DRAW THE OBJECT IN GIVEN RANGE
    def _draw_obj(self, coord, obj):
        y1 = 0
        for y in range(coord[1], coord[1] + coord[3]):
            x1 = 0
            for x in range(coord[0], coord[0] + coord[2]):
                # (x, y) wrt frame (x1, y1) wrt obj
                if 0 <= x < FRAME_WIDTH and 0 <= y < FRAME_HEIGHT:
                    self.__frame[y][x] = obj[y1][x1]
                x1 += 1
            y1 += 1

    # TOP INFO BAR
    def _top_info_print(self):
        s = f"SCORE:{self.__score}       "[:13]
        s += f"LIVES REMAINING:{LIVES - self.__lives_used}       "[:24]
        s += f"TIME: {self.__level_ticks//10}       "[:14]
        s += f"LEVEL: {self.__level}        "
        if self.__paddle.check_have_bullet_powerup():
            # (self.__ticks - self.__paddle.get_powerup_start_time())//10 >= POWERUP_LIFE
            # (X - S) // 10 = POWERUP_LIFE
            # X = S + 10*POWERUP_LIFE
            # ANSWER = X - NOW.
            x = self.__paddle.get_powerup_start_time() + 10*POWERUP_LIFE
            s += f"POWERUP TIME LEFT: {x - self.__ticks}        "

        if self.__level == UFO_LEVEL:
            s += f"UFO HEALTH: {self.__ufo.get_health()}        "
            s += f"Press q to quit."
        else:
            s += f"Press q to quit."
        self.__frame[1][2: 2 + len(s)] = [Style.BRIGHT +
                                          Fore.WHITE + Back.LIGHTBLACK_EX + x for x in s]

    # DRAW THE BRICK STRUCTURE
    def _draw_bricks(self):
        self.__bricks = []
        y = BRICK_STRUCTURE_Y

        if self.__level == UFO_LEVEL:
            y += 7

        dummy_row = ["X" for i in range(len(BRICK_STRUCTURE[self.__level - 1][0]) + 2)]

        self.__map_position_to_bricks = [dummy_row]

        for i, row in enumerate(BRICK_STRUCTURE[self.__level - 1]):
            x = BRICK_STRUCTURE_X
            row_bricks = ["X"]
            for j, brick_type in enumerate(row):
                if brick_type == " ":
                    row_bricks.append("X")
                    x += BRICK_WIDTH
                    continue
                if int(brick_type) == WEAK_BRICK_ID:
                    self.__bricks.append(WeakBrick(x, y, i + 1, j + 1))
                elif int(brick_type) == NORMAL_BRICK_ID:
                    self.__bricks.append(NormalBrick(x, y, i + 1, j + 1))
                elif int(brick_type) == STRONG_BRICK_ID:
                    self.__bricks.append(StrongBrick(x, y, i + 1, j + 1))
                elif int(brick_type) == UNBREAKABLE_BRICK_ID:
                    self.__bricks.append(UnbreakableBrick(x, y, i + 1, j + 1))
                elif int(brick_type) == EXPLODING_BRICK_ID:
                    self.__bricks.append(ExplodingBrick(x, y, i + 1, j + 1))
                elif int(brick_type) == RAINBOW_BRICK_ID:
                    self.__bricks.append(RainbowBrick(x, y, i + 1, j + 1))
                
                row_bricks.append(self.__bricks[-1])
                x += BRICK_WIDTH
           
            row_bricks.append("X")
            self.__map_position_to_bricks.append(row_bricks)
            y += BRICK_HEIGHT
        
        self.__map_position_to_bricks.append(dummy_row)
        # print(len(self.__map_position_to_bricks), len(self.__map_position_to_bricks[0]), len(B))
        # input()

    # HOLD SCREEN. BETWEEN LIFE LOSTS
    def _draw_hold_screen(self, message=""):
        self.__frame = np.array([[Style.BRIGHT + Fore.WHITE + Back.LIGHTBLACK_EX + " "
                                  for _ in range(FRAME_WIDTH)]
                                 for _ in range(FRAME_HEIGHT)])
        self._top_info_print()
        s = message + " Press ENTER to continue."
        self.__frame[FRAME_HEIGHT//2][50: 50 + len(s)] = [x for x in s]
        sra = str(Style.RESET_ALL)
        # get the grid string
        grid_str = "\n".join(
            [sra + " "*4 + "".join(row) + sra for row in self.__frame])
        # displaying the grid
        os.write(1, str.encode(grid_str))

    # DRAW ONE FRAME
    def _draw(self):
        # drawing the grid
        self.__frame = np.array([[Style.BRIGHT + Fore.WHITE + Back.LIGHTBLACK_EX + " "
                                  for _ in range(FRAME_WIDTH)]
                                 for _ in range(FRAME_HEIGHT)])
        self.__bricks_broken = 0
        
        # TOP INFO BAR
        self._top_info_print()
        
        # PADDLE
        self._draw_obj(self.__paddle.get_box(), self.__paddle.get_obj())
        
        # UFO
        if self.__level == UFO_LEVEL:
            if self.__ufo.check_active():
                self._draw_obj(self.__ufo.get_box(), self.__ufo.get_obj())
        
        # UFO BRICKS
        for ufo_brick in self.__ufo_bricks:
            if not ufo_brick.check_active():
                continue
            self._draw_obj(ufo_brick.get_box(), ufo_brick.get_obj())

        # BRICKS
        for brick in self.__bricks:
            if brick.check_active():
                self._draw_obj(brick.get_box(), brick.get_obj())
            else:
                self.__bricks_broken += 1
        
        #BULLETS
        for bullet in self.__bullets:
            if bullet.check_active():
                self._draw_obj(bullet.get_box(), bullet.get_obj())
        
        #BOMBS
        for bomb in self.__ufo_bombs:
            if bomb.check_active():
                self._draw_obj(bomb.get_box(), bomb.get_obj())
        
        # BALLS
        for ball in self.__balls:
            if ball.check_active():
                self._draw_obj(ball.get_box(), ball.get_obj())
        
        # POWERUPS
        for powerup in self.__powerups:
            if powerup.check_active():
                self._draw_obj(powerup.get_box(), powerup.get_obj())


        sra = str(Style.RESET_ALL)
        grid_str = "\n".join(
            [sra + " "*4 + "".join(row) + sra for row in self.__frame])
        os.write(1, str.encode(grid_str))

    # TAKE INPUT FROM KBHIT
    def _get_input(self):
        c = ""
        if self.__kb.kbhit():
            c = self.__kb.getch()
        self.__kb.flush()
        return c

    # HANDLE THE INPUT TAKEN
    def _handle_input(self, key):
        key = key.lower()
        if key == 'q':
            self.Quit()
        if key in "ad":
            if self.__level == UFO_LEVEL:
                self.__paddle.handle_key_press(key, self.__ufo)
                for idx, brick in enumerate(self.__ufo_bricks):
                    brick.set_x(self.__ufo.get_x() + idx*BRICK_WIDTH)
            else:
                self.__paddle.handle_key_press(key)
        if key in " ad":
            for ball in self.__balls:
                ball.handle_key_press(self.__paddle, key)
        if key == 'l':
            self.change_level()
    
    # DIVIDE THE BALL INTO TWO
    def divide_ball(self, ball):
        new_ball = Ball()
        x, y = ball.get_position()
        vx, vy = ball.get_velocity()
        if vx != 0:
            new_ball.set_velocity(vx * -1, vy)
        else:
            new_ball.set_velocity(-1, vy)
        new_ball.set_position(x, y)
        new_ball.set_state(BALL_RELEASED)
        return new_ball

    # DIFFRENT COLLISIONS
    def _ball_and_wall(self):
        for ball in self.__balls:
            if ball.check_active():
                ball.check_wall_collission()

    def _ball_and_paddle(self):
        for ball in self.__balls:
            if ball.check_active():
                if ball.check_paddle_collission(self.__paddle) and self.__fall_bricks:
                    self.__brick_structure_y_fall += 1
                    if self.__brick_structure_y_fall + BRICK_STRUCTURE_Y + len(BRICK_STRUCTURE[self.__level-1])*BRICK_HEIGHT == PADDLE_Y:
                        self.Quit()

    def _bomb_and_paddle(self):
        for bomb in self.__ufo_bombs:
            if bomb.check_active():
                if bomb.check_paddle_collission(self.__paddle):
                    self.__cnt_active_balls = 0
    
    def _ball_and_ufo(self):
        for ball in self.__balls:
            if ball.check_active():
                if ball.check_ufo_collission(self.__ufo):
                    self.Quit()

    def _powerup_and_paddle(self):
        for powerup in self.__powerups:
            if not powerup.check_active():
                continue
            if check_intersection(powerup, self.__paddle):
                if powerup.get_type() == POWERUP_EXPAND_PADDLE:
                    self.__paddle.change_width(INC_PADDLE_WIDTH)

                elif powerup.get_type() == POWERUP_SHRINK_PADDLE:
                    self.__paddle.change_width(-1 * SHRINK_PADDLE_WIDTH)

                elif powerup.get_type() == POWERUP_FAST_BALL:
                    for ball in self.__balls:
                        ball.inc_speed(2)

                elif powerup.get_type() == POWERUP_BALL_MULITIPLIER:
                    new_balls = []
                    for ball in self.__balls:
                        if ball.check_active():
                            new_balls.append(self.divide_ball(ball))
                    for new_ball in new_balls:
                        self.__balls.append(new_ball)

                elif powerup.get_type() == POWERUP_THRU_BALL:
                    for ball in self.__balls:
                        ball.set_type(THRU_BALL)
                elif powerup.get_type() == POWERUP_GRAB_BALL:
                    for ball in self.__balls:
                        ball.set_grabbable()
                elif powerup.get_type() == POWERUP_SHOOTING_BULLET:
                    self.__paddle.set_have_bullet_powerup(1)
                    self.__paddle.set_powerup_start_time(self.__ticks)
                elif powerup.get_type() == POWERUP_FIREBALL:
                    for ball in self.__balls:
                        ball.set_fire()
                else:
                    continue
                powerup.deactivate()

    def _update(self):

        # ball moved
        self.__cnt_active_balls = 0
        for ball in self.__balls:
            if ball.check_active():
                ball.update()
                self.__cnt_active_balls += 1
        
        # Powerup moved
        powerup_remove = []
        for id, powerup in enumerate(self.__powerups):
            if powerup.check_active():
                powerup.update()
            else:
                powerup_remove.append(id)
        for id in sorted(powerup_remove, reverse=True):
            del self.__powerups[id]

        # Bullet moved
        bullet_remove = []
        for id, bullet in enumerate(self.__bullets):
            if bullet.check_active():
                bullet.update()
            else:
                bullet_remove.append(id)
        for id in sorted(bullet_remove, reverse=True):
            del self.__bullets[id]
        
        # Bomb moved
        bomb_remove = []
        for id, bomb in enumerate(self.__ufo_bombs):
            if bomb.check_active():
                bomb.update()
            else:
                bomb_remove.append(id)
        for id in sorted(bomb_remove, reverse=True):
            del self.__ufo_bombs[id]

        # Bullet powerup done
        if self.__paddle.check_have_bullet_powerup() and (self.__ticks - self.__paddle.get_powerup_start_time())//10 >= POWERUP_LIFE:
            self.__paddle.set_have_bullet_powerup(0)

        # Generate Bullet 
        if self.__paddle.check_have_bullet_powerup() and self.__ticks % 8 == 0:
            x, y = self.__paddle.get_position()
            self.__bullets.append(Bullet(x + PADDLE_WIDTH//2, y, -1))
        
        # Generate Bomb
        if self.__level == UFO_LEVEL and self.__ufo.can_drop_bomb():
            u_x, u_y, u_width, u_height = self.__ufo.get_box()
            self.__ufo_bombs.append(Bomb(u_x + u_width//2, u_y + u_height))

        # ball and wall collissins
        self._ball_and_wall()
        # ball and paddle collissions
        self._ball_and_paddle()
        # bomb and paddle
        if self.__level == UFO_LEVEL:
            self._bomb_and_paddle()
        # powerup and paddle collissions
        self._powerup_and_paddle()

        # ufo bricks and ball
        if self.__level == UFO_LEVEL:
            for brick in self.__ufo_bricks:
                if not brick.check_active():
                    continue
                for ball in self.__balls:
                    if not ball.check_active():
                        continue
                    is_destroyed = brick.handle_collission(ball)

        # ufo and ball
        if self.__level == UFO_LEVEL:
            got_critical = True
            if self.__ufo.check_critical():
                got_critical = False

            self._ball_and_ufo()
            
            if not self.__ufo.check_critical():
                got_critical = False
            
            if got_critical:
                u_x, u_y, u_width, u_height = self.__ufo.get_box()
                for i in range(UFO_WIDTH // BRICK_WIDTH):
                    b_x = u_x + i*BRICK_WIDTH
                    b_y = u_y + u_height
                    self.__ufo_bricks.append(WeakBrick(b_x, b_y))
        

        for powerup in self.__powerups:
            if powerup.check_active():
                powerup.check_wall_collission()

        for brick in self.__bricks:
            if brick.check_active():
                for bullet in self.__bullets:
                    if bullet.check_active():
                        vx, vy = bullet.get_velocity()
                        is_destroyed = brick.handle_collission_bullet(bullet)
                        if not is_destroyed:
                            continue
                        if is_destroyed and brick.id == EXPLODING_BRICK_ID:
                            os.system('aplay -q ./sounds/explosions.wav&')
                            for i in self.__explode_ids:
                                if self.__bricks[i].check_active():
                                    self.__bricks[i].destroy()
                            for i in self.__explode_nbrs_ids:
                                if self.__bricks[i].check_active():
                                    self.__bricks[i].destroy()
                        if is_destroyed and random.random() > POWERUP_PROBABILITY:
                            # generate power_up
                            (x, y, _, _) = brick.get_box()
                            powerup_type = random.randint(0,7)
                            self.__powerups.append(
                                PowerUp(x, y, vx, vy, powerup_type))

        self.__cnt_active_bricks = 0
        for brick in self.__bricks:
            if brick.check_active():
                if brick.get_type() != UNBREAKABLE_BRICK_ID:
                    self.__cnt_active_bricks += 1
                for ball in self.__balls:
                    if ball.check_active():
                        vx, vy = ball.get_velocity()
                        is_destroyed = brick.handle_collission(ball, self.__map_position_to_bricks)
                        if is_destroyed and brick.id == EXPLODING_BRICK_ID:
                            for i in self.__explode_ids:
                                if self.__bricks[i].check_active():
                                    self.__bricks[i].destroy()
                            for i in self.__explode_nbrs_ids:
                                if self.__bricks[i].check_active():
                                    self.__bricks[i].destroy()
                        if is_destroyed and random.random() > POWERUP_PROBABILITY:
                            # generate power_up
                            (x, y, _, _) = brick.get_box()
                            powerup_type = random.randint(0,7)
                            # powerup_type = POWERUP_FIREBALL
                            self.__powerups.append(
                                PowerUp(x, y, vx, vy, powerup_type))

        for brick in self.__bricks:
            if brick.check_active():
                brick.set_y_fall(self.__brick_structure_y_fall)

        if (self.__level_ticks // 10) == LEVEL_TIME[self.__level - 1]:
            self.__fall_bricks = 1

    def _get_score(self):
        self.__score = max(0, 100*self.__bricks_broken -
                           (self.__ticks // 100)*10)
        
        if self.__level == UFO_LEVEL:
            self.__score += (max(0, 1000*(UFO_HEALTH - self.__ufo.get_health())))
        
        return self.__score + self.__last_level_score

    def refresh(self):
        self.__powerups = []
        self.__paddle.set_default()
        self.__balls = [Ball(paddle=self.__paddle)]
        self.__bullets = []

    def change_level(self):
        if self.__level == MAX_LEVEL:
            self.Quit()

        self.__level += 1

        while True:
            print("\033[0;0H")
            self._draw_hold_screen(f"Moving to level {self.__level}.")
            last_key_pressed = self._get_input().lower()
            if last_key_pressed == "\n":
                print("\033[0;0H")
                break
            elif last_key_pressed == "q":
                self.Quit()
                break

        if self.__level == UFO_LEVEL:
            os.system('aplay -q ./sounds/ufo.wav& 2>/dev/null')

        self._draw_bricks()
        self.__brick_structure_y_fall = 0
        self.__fall_bricks = 0
        self.__level_ticks = 0
        self.__last_level_score = self.__score
        self.refresh()

    # loop over frames
    def _loop(self):
        self.__game_status = GAME_START
        clear_terminal_screen()

        while self.__game_status == GAME_START:

            # 1. Clear Screen
            # 2. update positions and handle collisions
            # 3. update info
            # 4. draw
            # 5. handle input

            # clear screen and reposition cursor.
            print("\033[0;0H")

            self._update()

            if self.__cnt_active_bricks == 0 and self.__level != UFO_LEVEL:
                self.change_level()

            if self.__cnt_active_balls == 0:
                self.refresh()
                self.__lives_used += 1
                self.__game_status = GAME_HOLD
                while self.__game_status == GAME_HOLD:
                    print("\033[0;0H")
                    self._draw_hold_screen("Life lost. Game Paused.")
                    last_key_pressed = self._get_input().lower()
                    if last_key_pressed == "\n":
                        print("\033[0;0H")
                        self.__game_status = GAME_START
                    elif last_key_pressed == "q":
                        self.Quit()
                        break

            if LIVES - self.__lives_used == 0:
                self.Quit()
                break

            self._draw()
            last = time.time()

            last_key_pressed = self._get_input()
            self._handle_input(last_key_pressed)

            self.__score = self._get_score()
            self.__ticks += 1
            self.__level_ticks += 1

            while time.time() - last < self._refresh_time:
                pass

    def Quit(self):
        clear_terminal_screen()
        self.__game_status = GAME_END
        s = " "*5
        s = "GAME OVER!\n"
        s += f"SCORE:{self.__score}\n"[:13]
        s += f"LIVES USED:{self.__lives_used}\n"[:24]
        s += f"TIME: {self.__ticks//10}\n"
        os.write(1, str.encode(s))
        os.system('setterm -cursor on')
        os._exit(0)
