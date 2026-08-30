from sqlite3 import Row

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
                shape = (40*10 + 1 + 5 + 1 + 49*3 + 24, ),
        )
        self.history={
        "blocked_holes": 0,
        "row_holes": 0,
        "bumpiness": 0,
        "blockades": 0,
        "overhangs": 0,
        "well_height": 0,
        "middle_diff": 0,
        "max_height" : 0,
        "well_position": 0
        }

        self.last_blocked_holes = 0
        self.last_row_holes = 0
        self.last_blockades = 0
        self.last_bumpiness = 0

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

    def get_row_holes(self,board):
        row_holes = ((board == 0) & (np.cumsum(board, axis=0) < np.sum(board, axis=0))).sum()
        return row_holes

    def get_blocked_holes(self,board):
        board2 = board[:TRUE_ROWS, :]

        visited = np.zeros_like(board2, dtype=bool)
        stack = []

        for x in range(BOARD_COLUMNS):
            col = board2[:, x]

            filled_blocks = np.where(col == 1)[0]
            highest = filled_blocks[-1] if len(filled_blocks) > 0 else -1
            
            for y in range(highest + 1, TRUE_ROWS):
                if board2[y, x] == 0:
                    stack.append((y, x))

        while stack:
            y, x = stack.pop()
            if not (0 <= y < TRUE_ROWS and 0 <= x < BOARD_COLUMNS):
                continue
            if visited[y, x] or board2[y, x] == 1:
                continue

            visited[y, x] = True

            stack.extend([
                (y+1, x),
                (y-1, x),
                (y, x+1),
                (y, x-1),
            ])

        blocked_holes = np.sum((board2 == 0) & (~visited))
        return blocked_holes

    def get_blockades(self,board):
        grid_of_1s = np.ones((TRUE_ROWS, BOARD_COLUMNS), dtype=np.int8)
        blockades = np.sum(board & (np.cumsum(board, axis=0) < grid_of_1s.cumsum(axis=0)))  
        return blockades

    def get_bumpiness(self,heights):
        bumpiness = sum(abs(heights[i] - heights[i+1]) for i in range(len(heights)-1))
        return bumpiness

    def get_overhangs(self,board):
        overhangs = 0
        for y in range(1,BOARD_ROWS+1):
            for x in range(BOARD_COLUMNS):
                if board[y,x] == 1:
                    if board[y-1,x] == 0:
                        left_open = (x > 0 and board[y-1, x-1] == 0)
                        right_open = (x < BOARD_COLUMNS-1 and board[y-1, x+1] == 0)
                        if left_open or right_open:
                            overhangs += 1
        return overhangs

    def get_middle_tower_difference(self,heights):
        middle_height = np.mean(heights[3:7])
        edgeL_height = np.mean(heights[0:3])
        edgeR_height = np.mean(heights[7:10])
        return (middle_height - edgeL_height) + ((middle_height - edgeR_height))

    def get_heuristics(self):
        temp_board = (np.array(self.game.state.grid.matrix) != EMPTY_BLOCK).astype(np.int8)
        board = np.flipud(temp_board)
        heights = self.get_heights(board)
        max_height = np.max(heights)
        blocked_holes = self.get_blocked_holes(board)
        row_holes = self.get_row_holes(board)
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
            # print(f"blocked_holes: {blocked_holes}")
            # print(f"row_holes: {row_holes}")
            # print(f"bumpiness: {bumpiness}")
            # print(f"blockades: {blockades}")
            # print(f"overhangs: {overhangs}")
            # print(f"well_position: {well_position}")
            # print(f"max_height: {max_height}")
            # print(f"middle_difference: {middle_difference}")

        return np.concatenate([
        heights,
        np.array([max_height], dtype=np.int32),
        np.array([blocked_holes], dtype=np.int32),
        np.array([row_holes], dtype=np.int32),
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
        placements_vec = np.zeros((49*3))
        for i, (px,py,prot) in enumerate(placements[:49]):
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
        return {"score":0,
                "blocked_holes": getattr(self,"last_blocked_holes",0),
                "row_holes": getattr(self,"last_row_holes",0),
                "blockades": getattr(self,"last_blockades",0),
                "bumpiness": getattr(self,"last_bumpiness",0),
                "_is_cheese": getattr(self, "episode_is_cheese", False),
                }

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.game.state = self.game.get_initial_state()
        self.episode_cheese = False

        cheese_height = self.np_random.integers(5,15)
        hole_prob = self.np_random.uniform(0.1,0.3)

        if self.np_random.random() < 0.4:
            self.episode_cheese = True
            for row in range (cheese_height):
                for col in range(BOARD_COLUMNS):
                    if self.np_random.random() > hole_prob:
                        self.game.state.grid.matrix[TRUE_ROWS - 1 - row][col] = 1
                guarantee_gap = self.np_random.integers(0,BOARD_COLUMNS)
                if self.game.state.grid.matrix[TRUE_ROWS - 1 - row][guarantee_gap] != 0:
                    self.game.state.grid.matrix[TRUE_ROWS - 1 - row][guarantee_gap] = 0

        self.cached_placements = bfs_positions(self.game.state)

        board = np.flipud((np.array(self.game.state.grid.matrix) != EMPTY_BLOCK).astype(np.int8))
        blocked_holes = self.get_blocked_holes(board)
        heights = self.get_heights(board)
        row_holes = self.get_row_holes(board)
        bumpiness = self.get_bumpiness(heights)
        blockades = self.get_blockades(board)
        overhangs = self.get_overhangs(board)
        well_position = np.argmin(heights)
        well_height = heights[well_position]
        max_height = np.max(heights)
        middle_diff = self.get_middle_tower_difference(heights)

        self.history={
                "blocked_holes": blocked_holes,
                "row_holes": row_holes,
                "bumpiness": bumpiness,
                "blockades": blockades,
                "overhangs": overhangs,
                "well_height": well_height,
                "middle_diff": middle_diff,
                "max_height" : max_height,
                "well_position": well_position,
        }

        self.last_blocked_holes = blocked_holes
        self.last_row_holes = row_holes
        self.last_blockades = blockades
        self.last_bumpiness = bumpiness
        
        obs = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self.game.view.render(self.game.state)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()
            pygame.time.wait(50) 

        return obs, info

    def step(self, action):
        lines_cleared, t_spin_type, pc = 0, 0, False
        placements = self.cached_placements
        place_height = 0
        if action == 0:
            self.game.hold()
        elif placements:
            idx = action - 1
            if idx < len(placements):
                px, py, prot = placements[idx]
                self.game.state.piece.x = px
                self.game.state.piece.y = py
                self.game.state.piece.shape = ROTATIONS[self.game.state.piece.name][prot]
                place_height = 40 - py
                lines_cleared, t_spin_type, pc = self.game.handle_piece_landing(text= False)
            else:
                #shouldn't ever get here
                self.game.state.game_over = True
                print("hi")

        board = np.flipud((np.array(self.game.state.grid.matrix) != EMPTY_BLOCK).astype(np.int8))
        blocked_holes = self.get_blocked_holes(board)
        heights = self.get_heights(board)
        row_holes = self.get_row_holes(board)
        bumpiness = self.get_bumpiness(heights)
        blockades = self.get_blockades(board)
        overhangs = self.get_overhangs(board)
        well_position = np.argmin(heights)
        well_height = heights[well_position]
        max_height = np.sum(heights) # meant to be mean #TODO
        middle_diff = self.get_middle_tower_difference(heights)

        heuristics = {
        "blocked_holes": blocked_holes,
        "row_holes": row_holes,
        "bumpiness": bumpiness,
        "blockades": blockades,
        "overhangs": overhangs,
        "well_height": well_height,
        "middle_diff": middle_diff,
        "max_height" : max_height,
        "well_position": well_position,
        }
        self.last_blocked_holes = blocked_holes
        self.last_row_holes = row_holes
        self.last_blockades = blockades
        self.last_bumpiness = bumpiness

        reward = 0
        reward += (TRUE_ROWS - well_height)/10 * 0.01
        #reward -= np.sum(heights) * 0.005
        reward += np.power((1 - min(place_height,20)/20),2)
        reward -= max_height * 0.005    #/20 * 0.1
        reward -= blocked_holes/13 * 0.2
        reward -= row_holes/20 * 0.05
        reward -= bumpiness/20 * 0.02
        reward -= blockades/80 * 0.02
        reward -= overhangs/10 * 0.01
        reward -= middle_diff * 0.05

        # if well_position == self.history["well_position"]:
        #     reward += 0.1
        # else:
        #     reward -= 0.1

        #punishment (prev 20;40):
        reward -= (well_height - self.history["well_height"]) * 0.1
        reward -= (max_height - self.history["max_height"]) * 0.06
        reward -= (bumpiness - self.history["bumpiness"]) * 0.02
        reward -= max(0,(blockades - self.history["blockades"]) * 0.01)
        reward -= (overhangs - self.history["overhangs"]) * 0.01
        reward -= (middle_diff - self.history["middle_diff"]) * 0.02

        #reward (prev 5):
        reward -= max(-1.5, min(0, (blocked_holes - self.history["blocked_holes"]) * 0.3))
        reward -= max(-0.5, min(0, (row_holes - self.history["row_holes"]) * 0.1))
        reward -= max(-0.05, min(0,(blockades - self.history["blockades"]) * 0.01))

        reward = max(reward, -2)

        reward -= min(max(0,(row_holes - self.history["row_holes"]) * 2), 10)
        reward -= min(max(0,(blocked_holes - self.history["blocked_holes"]) * 3), 9)

        piece = self.game.state.piece.name

        #(prev 100, 130)
        if lines_cleared == 1:
            reward += 2 # * (0.8 + 0.2 * (20 - place_height) / 20) * np.sqrt(self.game.Combo + 1)
        elif lines_cleared == 2:
            reward += 3 # * (0.8 + 0.2 * (20 - place_height) / 20) * np.sqrt(self.game.Combo + 1)
        elif lines_cleared == 3:
            reward += 5 # * (0.8 + 0.2 * (20 - place_height) / 20) * np.sqrt(self.game.Combo + 1)
        elif lines_cleared == 4:
            reward += 10 # * (0.8 + 0.2 * (20 - place_height) / 20) * np.sqrt(self.game.Combo + 1)

        if t_spin_type == 2 and lines_cleared == 2:
            reward += 6 # * np.sqrt(self.game.Combo + 1)
        elif t_spin_type == 2 and lines_cleared == 3:    
            reward += 7 # * np.sqrt(self.game.Combo + 1)
        elif t_spin_type == 1:   
            reward += 0.5 # * np.sqrt(self.game.Combo + 1)
        elif piece == 2 and (t_spin_type == 0 or lines_cleared == 0):
            reward -= 0

        if self.game.Combo != 0:
            reward += self.game.Combo

        if self.game.B2B != 0:
            reward += 3 * self.game.B2B
        
        if pc:
            reward += 100

        #prev 15,12,9,5
        if self.game.state.game_over:
            reward -= 100
        else:
            if self.game.state.turn_held:
                reward = 0
            else:
                reward += 2
                

        terminated = self.game.state.game_over
        observation = self._get_obs()
        info = self._get_info()
        self.cached_placements = bfs_positions(self.game.state)

        if self.render_mode == "human":
            # print(self.game.Combo)
            # print(self.game.B2B)
            # print(f"delta well_height: {well_height - self.history["well_height"]}")
            # print(f"delta max_height: {max_height - self.history["max_height"]}")
            # print(f"delta blocked_holes: {blocked_holes - self.history["blocked_holes"]}")
            # print(f"delta row_holes: {row_holes - self.history["row_holes"]}")
            # print(f"delta bumpiness: {(bumpiness - self.history["bumpiness"])}")
            # print(f"delta blockades: {blockades - self.history["blockades"]}")
            # print(f"delta overhangs: {overhangs - self.history["overhangs"]}")
            # print(f"delta middle_diff: {middle_diff - self.history["middle_diff"]}")
            # print(f"lines_cleared: = {lines_cleared}")
            print(f"REWARD = {reward}")
            self.game.view.render(self.game.state, reward=reward)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()

            # pygame.time.wait(50)

            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        waiting = False

        self.history = heuristics

        return observation, reward, terminated, False, info

    def close(self):
        pygame.display.quit()
        pygame.quit()

