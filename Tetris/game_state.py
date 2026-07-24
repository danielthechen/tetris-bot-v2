from gravity import Gravity
from grid import Grid
from piece import Piece

class Gamestate:
    def __init__(self, grid: Grid, piece: Piece, gravity: Gravity, next_shape_ids: list, hold_piece: str, turn_held: bool):
        self.game_over = False
        self.score = 0
        self.grid = grid
        self.piece = piece
        self.gravity = gravity
        self.next_shape_ids = next_shape_ids
        self.hold_piece = hold_piece
        self.turn_held = turn_held