import random
import numpy as np
from tetronimoes import shapes

class Piece:
    def __init__(self, name):
        self.name = name
        self.shape = shapes[name]
        self.x = 3
        self.y = 0

    def move(self, move_x, move_y):
        self.x += move_x
        self.y += move_y

    def rotate(self, idx):
        return np.rot90(self.shape, k=idx)