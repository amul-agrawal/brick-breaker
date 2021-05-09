
"""
Utility functions:
"""

import subprocess as sp

def clear_terminal_screen():
    """
    Clears terminal screen
    """
    sp.call('clear', shell=True)


def check_intersection(obj1, obj2):
    """
    check if objects intersect 
    """
    (x1, y1, w1, h1) = obj1.get_box()
    (x2, y2, w2, h2) = obj2.get_box()
    if x2 + w2 - 1 < x1 or x2 >= x1 + w1:
        return False
    if y2 + h2 - 1 < y1 or y2 >= y1 + h1:
        return False
    
    return True
 