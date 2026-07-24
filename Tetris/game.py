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
        self.bag = []
        self.state = self.get_initial_state()
        self.view = GameView()

    def refill(self):
            self.bag = ['I','J','L','Z','S','O','T']
            random.shuffle(self.bag)
    
    def get_random_shape_id(self):
        if not self.bag:
            self.refill()
        return self.bag.pop()

    #Complete randomness
    # def get_random_shape_id(self):
    #     return random.choice(('I','J','L','Z','S','O','T'))

    def get_initial_state(self):
        return Gamestate(
            grid= Grid(),
            piece= Piece(self.get_random_shape_id()),
            gravity= Gravity(),
            next_shape_ids= [self.get_random_shape_id() for _ in range (5)],
            hold_piece = '',
            turn_held = False
        )

    def move_piece(self, move_x, move_y):
        piece = self.state.piece

        can_move = self.state.grid.can_fit_shape(
            piece.shape, piece.x + move_x, piece.y + move_y
        )

        if can_move:
            piece.move(move_x, move_y)

        return can_move

    def rotate_piece(self, idx):
        piece = self.state.piece

        new_shape = piece.rotate(idx)
        can_rotate = self.state.grid.can_fit_shape(new_shape, piece.x, piece.y)

        if can_rotate:
            piece.shape = new_shape

        return can_rotate

    def handle_piece_landing(self):
        state = self.state
        state.grid.place_piece(state.piece)

        cleared_lines = state.grid.clear_lines()
        state.score += cleared_lines

        new_piece = Piece(state.next_shape_ids.pop(0))

        if state.grid.can_fit_shape(new_piece.shape, new_piece.x, new_piece.y):
            state.piece = new_piece
            state.next_shape_ids.append(self.get_random_shape_id())
            self.state.turn_held = False
        else:
            state.game_over = True

    def soft_drop(self):
        self.state.gravity.reset_progress()

        did_move = self.move_piece(0, 1)
        if not did_move:
            self.handle_piece_landing()

        return did_move

    def hard_drop(self):
        while self.soft_drop():
            pass

    def hold(self):
        state = self.state

        if state.hold_piece:
            held_piece = Piece(state.hold_piece)
        else:
            held_piece = Piece(state.next_shape_ids.pop(0))
            state.next_shape_ids.append(self.get_random_shape_id())

        if state.grid.can_fit_shape(held_piece.shape, held_piece.x, held_piece.y):
            state.piece, state.hold_piece = held_piece, state.piece.name
            self.state.turn_held = True
        else:
            state.game_over = True

    def update(self, inputs, dt):
        if self.state.game_over:
            if pygame.K_BACKQUOTE in inputs:
                self.bag = []
                self.state = self.get_initial_state()
            return

        if pygame.K_LEFT in inputs:
            self.move_piece(-1, 0)

        if pygame.K_RIGHT in inputs:
            self.move_piece(1,0)

        if pygame.K_UP in inputs:
            self.rotate_piece(1)

        if pygame.K_DOWN in inputs:
            self.rotate_piece(-1)

        if pygame.K_RSHIFT in inputs:
            self.rotate_piece(2)

        if (pygame.K_SPACE in inputs) and not self.state.turn_held:
            self.hold()

        if pygame.K_x in inputs:
            self.hard_drop()

        if pygame.K_z in inputs:
            self.soft_drop()

        should_drop = self.state.gravity.update_progress(dt)
        if should_drop:
            self.soft_drop()

    def start(self):
        pygame.init()
        pygame.display.set_caption("Tetris")
        pygame.key.set_repeat(400,10)
        clock = pygame.time.Clock()

        self.view.init_display()

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

            self.update(inputs, dt)
            self.view.render(self.state)

        pygame.quit()
