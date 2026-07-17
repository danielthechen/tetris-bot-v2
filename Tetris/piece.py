import random
import numpy as np
from tetronimoes import shape

class Piece:
    def __init__(self, name):
        self.name = name
        self.shape = shape[name]

    def move(self, move_x, move_y):
        self.x += move_x
        self.y += move_y

    def rotate(self, idx):
        return np.rot90(self.shape, k=idx)