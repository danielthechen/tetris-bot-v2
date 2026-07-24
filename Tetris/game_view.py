import pygame
from grid import EMPTY_BLOCK
from config import BOARD_COLUMNS, BOARD_ROWS, CELL_SIZE, HOLD_BLOCK_WIDTH, QUEUE_BLOCK_WIDTH, QUEUE_BORDER, color_background, color_empty, color_Font, alpha_overlay, color_game_over
from game_state import Gamestate
from tetronimoes import colors, shapes

HOLD_WIDTH = HOLD_BLOCK_WIDTH * CELL_SIZE
HOLD_CONTENT_X = CELL_SIZE
HOLD_CONTENT_Y = CELL_SIZE

BOARD_WIDTH = BOARD_COLUMNS * CELL_SIZE
BOARD_HEIGHT = BOARD_ROWS * CELL_SIZE

QUEUE_WIDTH = QUEUE_BLOCK_WIDTH * CELL_SIZE
QUEUE_CONTENT_X = HOLD_WIDTH + BOARD_WIDTH + QUEUE_BORDER + CELL_SIZE
QUEUE_CONTENT_Y = CELL_SIZE

GAME_WIDTH = HOLD_WIDTH + BOARD_WIDTH + QUEUE_BORDER + QUEUE_WIDTH
GAME_HEIGHT = BOARD_HEIGHT

class GameView:
    def init_display(self):
        self.screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
        self.font = pygame.font.SysFont("Monaco", 32, bold=True)

    def draw_block(self, color, x, y):
        self.screen.fill(color, (x, y, CELL_SIZE - 1, CELL_SIZE - 1))

    def draw_shape(self, shape, shape_id, x, y):
        for i, row in enumerate(shape):
            for j, filled in enumerate(row):
                if filled:
                    self.draw_block(
                        colors[shape_id], x + j * CELL_SIZE, y + i * CELL_SIZE
                        )

    def draw_sidebar(self,next_shape_ids, score):
        self.screen.fill(
            color_empty, (BOARD_WIDTH, 0, QUEUE_BORDER, GAME_HEIGHT)
        )

        for shape_Num in range(len(next_shape_ids)):
            self.draw_shape(
                shapes[next_shape_ids[shape_Num]],
                next_shape_ids[shape_Num],
                QUEUE_CONTENT_X,
                QUEUE_CONTENT_Y + shape_Num * CELL_SIZE * 3
            )


        # score_surface = self.font.render("Score:", True, color_Font)
        # self.screen.blit(score_surface, (QUEUE_CONTENT_X, CELL_SIZE * 5))

        # score_surface = self.font.render(f"{score:06}", True, color_Font)
        # self.screen.blit(score_surface, (QUEUE_CONTENT_X, CELL_SIZE * 6))

    def draw_game_over_screen(self):
        overlay = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT))
        overlay.set_alpha(alpha_overlay)
        overlay.fill(color_game_over)
        self.screen.blit(overlay,(HOLD_WIDTH,0))
        text_surface = self.font.render("Game over", True, color_Font)
        text_center = text_surface.get_rect().centerx
        self.screen.blit(text_surface, (HOLD_WIDTH + BOARD_WIDTH / 2 - text_center, CELL_SIZE * 5))

    def draw_grid(self,grid):
        for i,row in enumerate(grid.matrix):
            for j,shape_id in enumerate(row):
                color = (
                    color_empty if shape_id == EMPTY_BLOCK
                    else colors[shape_id]
                )
                self.draw_block(color, j * CELL_SIZE + HOLD_WIDTH, i * CELL_SIZE)

    def draw_hold(self,hold_piece):
        if hold_piece:
            self.draw_shape(
            shapes[hold_piece],
            hold_piece,
            HOLD_CONTENT_X,
            HOLD_CONTENT_Y
            )

    def render(self, state: Gamestate):
        self.screen.fill(color_background)

        self.draw_grid(state.grid)

        self.draw_hold(state.hold_piece)

        self.draw_shape(
            state.piece.shape,
            state.piece.name,
            state.piece.x * CELL_SIZE + HOLD_WIDTH,
            state.piece.y * CELL_SIZE,
        )

        self.draw_sidebar(next_shape_ids=state.next_shape_ids, score=state.score)

        if state.game_over:
            self.draw_game_over_screen()

        pygame.display.flip()