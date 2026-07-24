from config import BOARD_COLUMNS, BOARD_ROWS
from piece import Piece

EMPTY_BLOCK = -1

class Grid:
    def  __init__(self):
        self.matrix = [[EMPTY_BLOCK] * BOARD_COLUMNS for _ in range(BOARD_ROWS)]

    def can_fit_shape(self, shape, x, y):
        for i, row in enumerate(shape):
            for j, filled in enumerate(row):
                if not filled:
                    continue

                board_x, board_y = x + j, y + i

                #IMPLEMENT SRS DETECTION HERE:

                #Wall Collision
                if board_x < 0 or board_x >= BOARD_COLUMNS:
                    return False

                #Floor Collision
                if board_y >= BOARD_ROWS:
                    return False
                
                if self.matrix[board_y][board_x] != EMPTY_BLOCK:
                    return False

        return True
    
    def place_piece(self, piece: Piece):
        for i,row in enumerate(piece.shape):
            for j,filled in enumerate(row):
                if filled:
                    self.matrix[i + piece.y][j + piece.x] = piece.name

    def clear_lines(self):
        cleared_lines = 0

        for i in reversed(range(len(self.matrix))):
            if all(block != EMPTY_BLOCK for block in self.matrix[i]):
                cleared_lines += 1
            elif cleared_lines > 0:
                self.matrix[i + cleared_lines] = self.matrix[i][:]

        for i in range (cleared_lines):
            self.matrix[i] = [EMPTY_BLOCK] * BOARD_COLUMNS
        
        return cleared_lines