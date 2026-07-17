import random
from tetronimoes import shape

class Piece:
    def __init__(self, name):
        self.name = name
        self.shape = shape[name]