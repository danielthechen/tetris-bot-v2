import pygame
from config import BOARD_COLUMNS, BOARD_ROWS, CELL_SIZE, QUEUE_BLOCK_WIDTH, QUEUE_BORDER, color_background, color_empty, color_Font
from game_state import Gamestate
from tetronimoes import colors, shapes

BOARD_WIDTH = BOARD_COLUMNS * CELL_SIZE
BOARD_HEIGHT = BOARD_ROWS * CELL_SIZE

SIDEBAR_WIDTH = QUEUE_BLOCK_WIDTH * CELL_SIZE
SIDEBAR_CONTENT_X = BOARD_WIDTH + QUEUE_BORDER + CELL_SIZE
SIDEBAR_CONTENT_Y = CELL_SIZE

GAME_WIDTH = BOARD_WIDTH + QUEUE_BORDER + SIDEBAR_WIDTH
GAME_HEIGHT = BOARD_HEIGHT

class GameView:
    def init_display(self):
        self.screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
        self.font = pygame.font.SysFont("Monaco", 32, bold=True)

    def draw_block(self, color, x, y):
        self.screen.fill(color, (x, y, CELL_SIZE - 1, CELL_SIZE-1))

    def draw_shape(self, shape, shape_id, x, y):
        for i, row in enumerate(shape):
            for j, filled in enumerate(row):
                if filled:
                    self.draw_block(
                        colors[shape_id], x + j * CELL_SIZE, y + i * CELL_SIZE
                        )

    def draw_sidebar(self,next_shape_id, score):
        self.screen.fill(
            color_empty, (BOARD_WIDTH, 0, QUEUE_BORDER, GAME_HEIGHT)
        )

        self.draw_shape(
            shapes[next_shape_id],
            next_shape_id,
            SIDEBAR_CONTENT_X,
            SIDEBAR_CONTENT_Y
        )

        score_surface = self.font.render("Score:", True, color_Font)
        self.screen.blit(score_surface, (SIDEBAR_CONTENT_X, CELL_SIZE * 5))

        score_surface = self.font.render(f"{score:06}", True, color_Font)
        self.screen.blit(score_surface, (SIDEBAR_CONTENT_X, CELL_SIZE * 6))

    def draw_game_over_screen(self):
        overlay = pygame.Surface(BOARD_WIDTH, BOARD_HEIGHT)
        overlay.set_alpha(ALPHA_GAME_OVER_OVERLAY)

    def render(self, state: Gamestate):
        self.screen.fill(color_background)

        self.draw_shape(
            state.piece.shape,
            state.piece.name,
            state.piece.x * CELL_SIZE,
            state.piece.y * CELL_SIZE,
        )

        self.draw_sidebar(next_shape_id=state.next_shape_id, score=state.score)

        pygame.display.flip()