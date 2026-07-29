import pygame

color_empty = pygame.Color("#DDCFCF")
color_background = pygame.Color("#000000")
color_Font = pygame.Color("#FFFFFF")
color_game_over = pygame.Color("#2E2E2E")
alpha_overlay = 200

lock_delay = 500 #milliseconds
max_lock_reset = 15

DAS = 92
ARR = 8

TRUE_ROWS = 40
BOARD_ROWS = 20
OFFSET = TRUE_ROWS - BOARD_ROWS
BOARD_COLUMNS = 10

GRAV = 0
GRAV_ACCEL = 0
GRAV_THRESH = 100

CELL_SIZE = 40
QUEUE_BORDER = 0
QUEUE_BLOCK_WIDTH = 6
HOLD_BLOCK_WIDTH = 6