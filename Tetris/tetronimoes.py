import pygame
import numpy as np

#Piece color values
colors = {
    1 : pygame.Color(217, 162, 55),  # yellow - O
    2 : pygame.Color(161, 53, 134),  # purple - T
    3 : pygame.Color(111, 175, 52),  # lime - S
    4 : pygame.Color(197, 46, 61),  # red - Z
    5 : pygame.Color(41, 64, 191),  # dark blue - J
    6 : pygame.Color(211, 100, 40),  # orange - L
    7 : pygame.Color(71, 153, 210),  # turquoise - I
}

shapes = {
    #O Piece
    1 : np.array([
        [0, 1, 1],
        [0, 1, 1],
        [0, 0, 0],
    ]),

     #T Piece
    2 : np.array([
        [0, 1, 0],
        [1, 1, 1],
        [0, 0, 0],
    ]),

    #S Piece
    3 : np.array([
        [0, 1, 1],
        [1, 1, 0],
        [0, 0, 0],
    ]),

    #Z Piece
    4 : np.array([
        [1, 1, 0],
        [0, 1, 1],
        [0, 0, 0],
    ]),

    #J Piece
    5 : np.array([
        [1, 0, 0],
        [1, 1, 1],
        [0, 0, 0],
    ]),

    #L Piece
    6 : np.array([
        [0, 0, 1],
        [1, 1, 1],
        [0, 0, 0],
    ]),

    #I Piece
    7 : np.array([
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]),
}

