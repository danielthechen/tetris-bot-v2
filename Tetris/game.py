import random
import pygame
from tetronimoes import shapes
from game_view import GameView
from game_state import Gamestate
from config import lock_delay, max_lock_reset, DAS, ARR
from piece import Piece
from grid import Grid
from gravity import Gravity
from kicks import I_KICKS, JLTSZO_KICKS

class Game:
    def __init__(self):
        self.bag = []
        self.active_dir_key = None
        self.active_dir = 0
        self.press_time = 0
        self.left_press_time = 0
        self.right_press_time = 0
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
            turn_held = False,
            lock_timer= 0,
            lock_resets= 0,
            rotation_idx= 0,
        )

    def move_piece(self, move_x, move_y):
        piece = self.state.piece

        can_move = self.state.grid.can_fit_shape(
            piece.shape, piece.x + move_x, piece.y + move_y
        )

        if can_move:
            piece.move(move_x, move_y)
            if not self.state.grid.can_fit_shape(piece.shape, piece.x, piece.y + 1):
                self.state.lock_timer = 0
                self.state.lock_resets += 1

        return can_move

    def rotate_piece(self, idx):
        piece = self.state.piece
        old_orientation = self.state.rotation_idx
        new_shape = piece.rotate(idx)
        new_orientation = (old_orientation - idx) % 4

        kicks = I_KICKS if piece.name == 'I' else JLTSZO_KICKS
        offsets = kicks.get((old_orientation,new_orientation), [(0,0)])

        for dx, dy in offsets:
            if self.state.grid.can_fit_shape(new_shape, piece.x + dx, piece.y + dy):
                piece.shape = new_shape
                piece.x += dx
                piece.y += dy
                self.state.rotation_idx = new_orientation
                if not self.state.grid.can_fit_shape(piece.shape, piece.x + dx, piece.y + dy +1):
                    self.state.lock_timer = 0
                    self.state.lock_resets += 1
                return True
        return False

    def handle_piece_landing(self):
        state = self.state
        state.grid.place_piece(state.piece)

        cleared_lines = state.grid.clear_lines()
        state.score += cleared_lines

        new_piece = Piece(state.next_shape_ids.pop(0))
        state.rotation_idx = 0
    
        if state.grid.can_fit_shape(new_piece.shape, new_piece.x, new_piece.y):
            state.piece = new_piece
            state.next_shape_ids.append(self.get_random_shape_id())
            state.turn_held = False
        else:
            state.game_over = True

        state.lock_timer = 0
        state.lock_resets = 0

    def soft_drop(self):
        self.state.gravity.reset_progress()
        did_move = self.move_piece(0, 1)
        return did_move

    def hard_drop(self):
        while self.soft_drop():
            pass
        self.handle_piece_landing()

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

    def get_active_direction(self, inputs, time_now):
        if inputs[pygame.K_LEFT]:
            if self.left_press_time == 0:
                self.left_press_time = time_now
        else:
            self.left_press_time = 0

        if inputs[pygame.K_RIGHT]:
            if self.right_press_time == 0:
                self.right_press_time = time_now
        else:
            self.right_press_time = 0

        if self.left_press_time and (self.right_press_time == 0 or self.left_press_time > self.right_press_time):
            return pygame.K_LEFT, -1
        elif self.right_press_time and (self.left_press_time == 0 or self.right_press_time > self.left_press_time):
            return pygame.K_RIGHT, 1
        else:
            return None, 0

    def update(self, inputs, dt):
        time_now = pygame.time.get_ticks()
        old_active_key = self.active_dir_key

        if self.state.game_over:
            if inputs[pygame.K_BACKQUOTE]:
                self.bag = []
                self.state = self.get_initial_state()
            return

        self.active_dir_key, self.active_dir = self.get_active_direction(inputs, time_now)

        if self.active_dir_key and self.active_dir_key != old_active_key:
            self.move_piece(self.active_dir, 0)
            self.press_time = time_now

        if self.active_dir_key and inputs[self.active_dir_key]:
            elapsed = time_now - self.press_time
            if elapsed >= DAS and ((elapsed - DAS) % ARR < dt):
                self.move_piece(self.active_dir,0)

        if inputs[pygame.K_z]:
            self.soft_drop()

        should_drop = self.state.gravity.update_progress(dt)
        if should_drop:
            self.soft_drop()

        if not self.state.grid.can_fit_shape(
            self.state.piece.shape,
            self.state.piece.x,
            self.state.piece.y + 1
        ):
            self.state.lock_timer += dt
            if self.state.lock_timer >= lock_delay or self.state.lock_resets >= max_lock_reset:
                self.handle_piece_landing()

    def start(self):
        pygame.init()
        pygame.display.set_caption("Tetris")
        clock = pygame.time.Clock()

        self.view.init_display()

        is_running = True
        while is_running:
            dt = clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False
                elif event.type == pygame.KEYDOWN:
                    if not self.state.game_over:
                        if event.key == pygame.K_UP:
                            self.rotate_piece(1)
        
                        elif event.key == pygame.K_DOWN:
                            self.rotate_piece(-1)

                        elif event.key == pygame.K_RSHIFT:
                            self.rotate_piece(2)

                        elif event.key == pygame.K_SPACE and not self.state.turn_held:
                            self.hold()
                
                        elif event.key == pygame.K_x:
                            self.hard_drop()

                        elif event.key == pygame.K_BACKQUOTE:
                            self.bag = []
                            self.state = self.get_initial_state()

            inputs = pygame.key.get_pressed()

            self.update(inputs, dt)
            self.view.render(self.state)

        pygame.quit()