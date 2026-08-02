import numpy as np
import pygame
from rotation_masks import ROTATIONS
from game_view import GameView
from game_state import Gamestate
from config import BOARD_COLUMNS, BOARD_ROWS, lock_delay, max_lock_reset, DAS, ARR, SEED
from piece import Piece
from grid import Grid, EMPTY_BLOCK
from gravity import Gravity
from kicks import I_OFFSET_DATA, JLTSZ_OFFSET_DATA, KICKS_180, O_OFFSET_DATA
from bfs_search import bfs_positions
from bfs_kicks import KICK_DIFFS

class Tetris_Game:
    def __init__(self):
        self.bag = []
        self.rng = np.random.default_rng(seed=SEED)
        self.active_dir_key = None
        self.active_dir = 0
        self.press_time = 0
        self.left_press_time = 0
        self.right_press_time = 0
        self.state = self.get_initial_state()
        self.view = GameView()

    def refill(self):
            self.bag = ['I','J','L','Z','S','O','T']
            self.rng.shuffle(self.bag)
    
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
            did_rotate= False,
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
            self.state.did_rotate = False

        return can_move

    def rotate_piece(self, idx):
        piece = self.state.piece
        old_orientation = self.state.rotation_idx
        new_shape = piece.rotate(idx)
        new_orientation = (old_orientation - idx) % 4

        if idx != 2 and piece.name != 'O':
            if piece.name == 'I':
                offsets = KICK_DIFFS['I'][old_orientation][new_orientation]
            else:
                offsets = KICK_DIFFS['JLTSZ'][old_orientation][new_orientation]
        else:
            if piece.name == 'O':
                offsets = KICK_DIFFS['O'][old_orientation][new_orientation]
            else: 
                offsets = KICK_DIFFS['180'][old_orientation]

            # if piece.name == 'I':
            #     data = I_OFFSET_DATA
            # elif piece.name == 'O':
            #     data = O_OFFSET_DATA
            # else:
            #     data = JLTSZ_OFFSET_DATA
            # offsets = [tuple(a - b for a,b in zip(t1, t2)) for t1,t2 in zip(data[old_orientation],data[new_orientation])]
        # else:
        #     offsets = KICKS_180[old_orientation]


        for kick_num, (dx, dy) in enumerate(offsets):
            if self.state.grid.can_fit_shape(new_shape, piece.x + dx, piece.y + dy):
                piece.shape = new_shape
                piece.x += dx
                piece.y += dy
                self.state.did_rotate = True
                self.state.rotation_idx = new_orientation
                if not self.state.grid.can_fit_shape(piece.shape, piece.x, piece.y + 1):
                    self.state.lock_timer = 0
                    self.state.lock_resets += 1
                return (kick_num + 1)
        return None

    def handle_piece_landing(self, text= True):
        state = self.state
        state.grid.place_piece(state.piece)
        
        t_spin = self.is_t_spin(state.piece)

        self.lines_cleared = state.grid.clear_lines()

        pc = self.is_perfect_clear(state.grid.matrix)
    
        #credit: https://tetrio.wiki.gg/wiki/Spins#O-Spin

        if text:
            if self.lines_cleared == 4:
                print_line = "TETRIS"
            elif self.lines_cleared == 3:
                print_line = "TRIPLE"
            elif self.lines_cleared == 2:
                print_line = "DOUBLE"
            elif self.lines_cleared == 1:
                print_line = "SINGLE"
            else:
                print_line = ""

            if t_spin == 2:
                print("T SPIN", print_line)
            elif t_spin == 1:
                print("T SPIN MINI", print_line)
            elif print_line:
                print(print_line)

            if pc:
                print("PERFECT CLEAR")

        new_piece = Piece(state.next_shape_ids.pop(0))
        state.rotation_idx = 0
    
        if state.grid.can_fit_shape(new_piece.shape, new_piece.x, new_piece.y):
            state.piece = new_piece
            state.next_shape_ids.append(self.get_random_shape_id())
            state.turn_held = False

            # FIXME BFS RENDER
            # placements = bfs_positions(self.state)
            # # print(len(placements))
            # for (px, py, prot) in placements:
            #     temp_piece = Piece(state.piece.name)
            #     temp_piece.x, temp_piece.y = px, py
            #     # print(px, py, prot)
            #     temp_piece.shape = ROTATIONS[state.piece.name][prot]
            #     self.state.piece = temp_piece
            #     self.view.render(self.state)
            #     pygame.time.wait(50)
            # state.piece = new_piece
                    
        else:
            state.game_over = True
            state.next_shape_ids.append(self.get_random_shape_id())

        state.lock_timer = 0
        state.lock_resets = 0

        return self.lines_cleared, t_spin, pc

    def soft_drop(self):
        self.state.gravity.reset_progress()
        did_move = self.move_piece(0, 1)
        if did_move:
            self.state.did_rotate = False
        return did_move

    def instant_soft_drop(self):
        while self.soft_drop():
            pass

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

    def is_t_spin(self,piece):
        if piece.name != "T" or not self.state.did_rotate:
            return 0
        x, y = piece.x, piece.y
        corners = [(x , y), (x+2, y), (x+2, y+2), (x, y+2)]
        filled = 0
        for cx, cy in corners:
            if cx < 0 or cx >= BOARD_COLUMNS or cy < 0 or cy >= BOARD_ROWS:
                filled += 1
            elif self.state.grid.matrix[cy][cx] != EMPTY_BLOCK:
                filled += 1

        if filled >= 3:
            head_filled = 0
            head_checks = {
            0: [(x, y), (x+2, y)],
            1: [(x+2, y+2), (x+2, y)],
            2: [(x+2, y+2), (x, y+2)],
            3: [(x, y), (x, y+2)],
            }

            #print(self.state.rotation_idx)
            #print(head_checks[self.state.rotation_idx])

            head_filled = 0
            for hx, hy in head_checks[self.state.rotation_idx]:
                #print(self.state.grid.matrix[hy][hx])
                if self.state.grid.matrix[hy][hx] != EMPTY_BLOCK:
                    head_filled += 1

            #print(self.state.piece.kick)
            #print(head_filled)

            if head_filled == 2 or self.state.piece.kick == 5:
                return 2
            else:
                return 1
        return 0
            

    def is_perfect_clear(self,board):
        return all(cell == EMPTY_BLOCK for row in board for cell in row)

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

    def update(self, inputs, ticks=1):
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

        if self.active_dir_key and inputs[self.active_dir_key]:
            self.press_time += ticks
            if self.press_time >= DAS and ((self.press_time - DAS) % ARR == 0):
                self.move_piece(self.active_dir,0)
        else:
            self.press_time = 0

        if inputs[pygame.K_z]:
            self.instant_soft_drop()

        should_drop = self.state.gravity.update_progress(ticks)
        if should_drop:
            self.soft_drop()

        if not self.state.grid.can_fit_shape(
            self.state.piece.shape,
            self.state.piece.x,
            self.state.piece.y + 1
        ):
            self.state.lock_timer += ticks
            if self.state.lock_timer >= lock_delay or self.state.lock_resets >= max_lock_reset:
                self.handle_piece_landing()

    def start(self):
        pygame.init()
        pygame.display.set_caption("Tetris")
        clock = pygame.time.Clock()

        self.view.init_display()

        is_running = True
        while is_running:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False
                elif event.type == pygame.KEYDOWN:
                    if not self.state.game_over:
                        if event.key == pygame.K_UP:
                            self.state.piece.kick = self.rotate_piece(1)
        
                        elif event.key == pygame.K_DOWN:
                            self.state.piece.kick = self.rotate_piece(-1)

                        elif event.key == pygame.K_RSHIFT:
                            self.state.piece.kick = self.rotate_piece(2)

                        elif event.key == pygame.K_SPACE and not self.state.turn_held:
                            self.hold()
                
                        elif event.key == pygame.K_x:
                            self.hard_drop()

                        elif event.key == pygame.K_BACKQUOTE:
                            self.bag = []
                            self.state = self.get_initial_state()

            inputs = pygame.key.get_pressed()
            self.update(inputs, ticks=1)
        
            #print(self.state.piece.x, self.state.piece.y, self.state.rotation_idx)
            #print(self.state.piece.kick)
            self.view.render(self.state)

        pygame.quit()