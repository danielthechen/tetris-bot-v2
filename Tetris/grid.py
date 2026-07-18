from board import BOARD_COLUMNS, BOARD_ROWS

EMPTY_BLOCK = -1

class Grid:
    def  __init__(self):
        self.matrix = [[EMPTY_BLOCK] * BOARD_COLUMNS for _ in range(BOARD_ROWS)]

    def can_fit_shape(self, shape, x, y):
        for i, row in enumerate(shape):
            for j, is_solid in enumerate(row):
                
