import pygame
import numpy as np

#Piece color values
colors = {
    'I' : pygame.Color(71, 153, 210),  # turquoise - I
    'J' : pygame.Color(41, 64, 191),  # dark blue - J
    'L' : pygame.Color(211, 100, 40),  # orange - L
    'O' : pygame.Color(217, 162, 55),  # yellow - O
    'Z' : pygame.Color(197, 46, 61),  # red - Z
    'S' : pygame.Color(111, 175, 52),  # lime - S
    'T' : pygame.Color(161, 53, 134),  # purple - T
}

shapes = {

    #I Piece
    'I' : np.array([
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]),

    #J Piece
    'J' : np.array([
        [1, 0, 0],
        [1, 1, 1],
        [0, 0, 0],
    ]),

    #L Piece
    'L' : np.array([
        [0, 0, 1],
        [1, 1, 1],
        [0, 0, 0],
    ]),

    #O Piece
    'O' : np.array([
        [1, 1],
        [1, 1],
    ]),

    #Z Piece
    'Z' : np.array([
        [1, 1, 0],
        [0, 1, 1],
        [0, 0, 0],
    ]),

    #S Piece
    'S' : np.array([
        [0, 1, 1],
        [1, 1, 0],
        [0, 0, 0],
    ]),

    #T Piece
    'T' : np.array([
        [0, 1, 0],
        [1, 1, 1],
        [0, 0, 0],
    ]),
}