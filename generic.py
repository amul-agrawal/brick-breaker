"""
Object Prototype
"""

class StationaryObject:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.is_active = 1

    def set_x(self, x):
        self.x = x
    
    def set_y(self, y):
        self.y = y
        
    def get_position(self):
        return self.x, self.y
    
    def set_position(self, x, y):
        self.x, self.y = x, y
    
    def get_width(self):
        return self.width
    
    def set_width(self, width):
        self.width = width
    
    def get_height(self):
        return self.height
    
    def set_height(self, height):
        self.height = height

    def check_active(self):
        return self.is_active
    
    def get_box(self):
        return self.x, self.y , self.width, self.height


class MovingObject(StationaryObject):
    def __init__(self):
        super().__init__()
        self.vx = 0
        self.vy = 0
    
    def get_velocity(self):
        return self.vx, self.vy
    
    def set_velocity(self, vx, vy):
        self.vx, self.vy = vx, vy