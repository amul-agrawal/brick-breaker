# Brick Breaker
This is an arcade game in Python3 (terminal-based), inspired from the old classic brick breaker similar to [this](https://www.youtube.com/watch?v=BXEk0IHzHOM). The player will be using a paddle with a bouncing ball to smash a
wall of bricks and make high scores! The objective of the game is to break all the bricks as fast as possible and
beat the highest score! You lose a life when the ball touches the ground below the paddle.

## Controls
- <kbd>A</kbd>: move paddle left
- <kbd>D</kbd>: move paddle right
- <kbd>SPACE</kbd>: release ball
- <kbd>Q</kbd>: quit

## OOPS concept used

- Inheritance: Generic classes for game objects and all the objects inheriting these classes. BaseBrick class for different bricks.

- Polymorphism: One PowerUp class representing different powerups for different instances.

- Encapsulation: Class and object based approach for all the functionality implemented.

- Abstraction: Intuitive functionality like move(), break(), collide(), etc, showing away inner details from
the end user.