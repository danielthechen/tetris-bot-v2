import gymnasium as gym
from gymnasium import spaces
import pygame
import numpy as np
from config import BOARD_COLUMNS, BOARD_ROWS, TRUE_ROWS
from bfs_search import bfs_positions
from game import Tetris_Game
from grid import EMPTY_BLOCK
from rotation_masks import ROTATIONS

class TetrisEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 60}

    def __init__(self, render_mode=None):
        self.render_mode = render_mode
        self.game = Tetris_Game()
        
        self.observation_space = spaces.Box(
                low=0,
                high=7,
                shape = (40*10 + 1 + 5 + 1 + 50*3 + 23, ),
        )

        #variable action-space
        self.action_space = spaces.Discrete(50)

        if render_mode == "human":
            pygame.init()
            pygame.display.set_caption("Tetris RL")
            self.game.view.init_display()

    def get_heights(self,board):
        range_1_40 = np.array(list(range(1,TRUE_ROWS  + 1)))
        heights = np.array([int((column * range_1_40).max()) for column in board.T])
        return heights

    def get_holes(self,board):
        holes = ((board == 0) & (np.cumsum(board, axis=0) < np.sum(board, axis=0))).sum()
        return holes

    def get_blockades(self,board):
        grid_of_1s = np.ones((TRUE_ROWS, BOARD_COLUMNS), dtype=np.int8)
        blockades = np.sum(board & (np.cumsum(board, axis=0) < grid_of_1s.cumsum(axis=0)))  
        return blockades

    def get_bumpiness(self,heights):
        bumpiness = sum(abs(heights[i] - heights[i+1]) for i in range(len(heights)-1))
        return bumpiness

    def get_overhangs(self,board):
        overhangs = 0
        for y in range(BOARD_ROWS - 1):
            for x in range(BOARD_COLUMNS):
                if board[y,x] == 1:
                    if board[y+1,x] == 0:
                        left_open = (x > 0 and board[y+1, x-1] == 0)
                        right_open = (x < BOARD_COLUMNS-1 and board[y+1, x+1] == 0)
                        if left_open or right_open:
                            overhangs += 1
        return overhangs

    def get_middle_tower_difference(self,heights):
        middle_height = np.median(heights[3:7])
        edgeL_height = np.median(heights[0:3])
        edgeR_height = np.median(heights[7:10])
        return (middle_height - edgeL_height) + ((middle_height - edgeR_height))

    def get_heuristics(self):
        temp_board = (np.array(self.game.state.grid.matrix) != EMPTY_BLOCK).astype(np.int8)
        board = np.flipud(temp_board)
        heights = self.get_heights(board)
        max_height = np.max(heights)
        holes = self.get_holes(board)
        bumpiness = self.get_bumpiness(heights)
        blockades = self.get_blockades(board)
        overhangs = self.get_overhangs(board)
        well_position = np.argmin(heights)
        middle_difference = self.get_middle_tower_difference(heights)

        t_spin = self.game.T_Spin
        wasted_t = int(self.game.state.piece.name == 2 and t_spin == 0)
        pc = int(self.game.PC)
        tetris = int(self.game.Tetris)
        combo = self.game.Combo
        b2b = self.game.B2B

        if self.render_mode == "human":
            print(temp_board[20:])
            print(f"holes: {holes}")
            print(f"bumpiness: {bumpiness}")
            print(f"blockades: {blockades}")
            print(f"overhangs: {overhangs}")
            print(f"well_position: {well_position}")
            print(f"middle_difference: {middle_difference}")

        return np.concatenate([
        heights,
        np.array([max_height], dtype=np.int32),
        np.array([holes], dtype=np.int32),
        np.array([bumpiness], dtype=np.int32),
        np.array([blockades], dtype=np.int32),
        np.array([overhangs], dtype=np.int32),
        np.array([well_position], dtype=np.int32),
        np.array([middle_difference], dtype=np.int32),
        np.array([t_spin, wasted_t, pc, tetris, combo, b2b], dtype=np.int32)
    ], dtype=np.int32)


    def _get_obs(self):
        grid = (np.array(self.game.state.grid.matrix) != EMPTY_BLOCK).astype(np.int8).flatten()
        current_piece = np.array([self.game.state.piece.name])
        queue = np.array([name for name in self.game.state.next_shape_ids])
        hold_piece = np.array([self.game.state.hold_piece if self.game.state.hold_piece else 7])
        placements = np.array(bfs_positions(self.game.state))
        placements_vec = np.zeros((50*3))
        for i, (px,py,prot) in enumerate(placements[:50]):
            placements_vec[i*3:(i*3)+3] = [px,py,prot]
        heuristics = self.get_heuristics()

        return np.concatenate([
            grid,
            current_piece,
            queue,hold_piece, 
            placements_vec,
            heuristics,
             ])
    
    def _get_info(self):
        return {"score":0}

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.game.state = self.game.get_initial_state()
        self.game.bag = []
        obs = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self.game.view.render(self.game.state)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()
            pygame.time.wait(5000) 

        return obs, info

    def step(self, action):
        board = np.flipud((np.array(self.game.state.grid.matrix) != EMPTY_BLOCK).astype(np.int8))
        heights = self.get_heights(board)
        holes = self.get_holes(board)
        bumpiness = self.get_bumpiness(heights)
        blockades = self.get_blockades(board)
        overhangs = self.get_overhangs(board)
        #middle_diff = self.get_middle_tower_difference(heights)
        reward = 0

        reward -= holes
        reward -= bumpiness * 0.5
        reward -= blockades * 0.5
        reward -= overhangs  *0.1
        #reward -= middle_diff * 1.5 / 40

        lines_cleared, t_spin_type, pc = 0, 0, False
        piece = self.game.state.piece.name

        placements = bfs_positions(self.game.state)
        if placements:
            if action < len(placements):
                px, py, prot = placements[action]
                self.game.state.piece.x = px
                self.game.state.piece.y = py
                self.game.state.piece.shape = ROTATIONS[self.game.state.piece.name][prot]
                lines_cleared, t_spin_type, pc = self.game.handle_piece_landing(text= False)
            else:
                #shouldn't ever get here
                self.game.state.game_over = True
                print("hi")

        if lines_cleared == 1:
            reward += 5
        elif lines_cleared == 2:
            reward += 10
        elif lines_cleared == 3:
            reward += 15
        elif lines_cleared == 4:
            reward += 30

        if t_spin_type == 2:
            reward += 35
        elif t_spin_type == 1:
            reward += 6
        elif piece == 2 and t_spin_type == 0:
            reward -= 1

        if pc:
            reward += 40

        if self.game.state.game_over:
            reward -= 150
        else:
            reward += 2

        terminated = self.game.state.game_over
        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            print(f"REWARD = {reward}")
            self.game.view.render(self.game.state)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()
            pygame.time.wait(5000) 

        return observation, reward, terminated, False, info


    def close(self):
        pygame.display.quit()
        pygame.quit()

