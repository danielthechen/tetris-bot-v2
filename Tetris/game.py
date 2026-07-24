import random
import pygame
from tetronimoes import shapes
from game_view import GameView
from game_state import Gamestate
from piece import Piece
from grid import Grid
from gravity import Gravity

class Game:
    def __init__(self):
        self.state = self.get_initial_state()
        self.view = GameView()

    #CHANGE THIS TO MAKE THIS A 7-BAG SYSTEM
    def get_random_shape_id(self):
        return random.choice(('I','J','L','Z','S','O','T'))

    def get_initial_state(self):
        return Gamestate(
            grid= Grid(),
            piece= Piece(self.get_random_shape_id()),
            gravity= Gravity(),
            #THIS NEEDS TO ALSO ACCOUNT FOR 7 BAG, PERHAPS MAKE EACH INSTANCE OF 7 BAG REMOVE A PIECE
            next_shape_id= self.get_random_shape_id(),
        )

    def start(self):
        pygame.init()
        pygame.display.set_caption("Tetris")
        pygame.key.set_repeat(400,10)
        clock = pygame.time.Clock()

        self.view.init_display()

        self.state.is_game_over = True

        inputs = set()

        is_running = True
        while is_running:
            dt = clock.tick(60)

            inputs.clear()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False
                elif event.type == pygame.KEYDOWN:
                    inputs.add(event.key)

            self.view.render(self.state)

            print(inputs)

        pygame.quit()
