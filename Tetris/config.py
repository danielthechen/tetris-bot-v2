import pygame
import numpy as np

color_empty = pygame.Color("#DDCFCF")
color_background = pygame.Color("#000000")
color_Font = pygame.Color("#FFFFFF")
color_game_over = pygame.Color("#2E2E2E")
alpha_overlay = 200

lock_delay = 30 #frames, in 60fps so 0.5 ms, this is changed for the RL
max_lock_reset = 15

SEED = 10

#Frames
DAS = 5.5
ARR = 0.5

TRUE_ROWS = 40
BOARD_ROWS = 20
OFFSET = TRUE_ROWS - BOARD_ROWS
BOARD_COLUMNS = 10

GRAV = 0
GRAV_ACCEL = 0
GRAV_THRESH = 1000

CELL_SIZE = 40
QUEUE_BORDER = 0
QUEUE_BLOCK_WIDTH = 6
HOLD_BLOCK_WIDTH = 6