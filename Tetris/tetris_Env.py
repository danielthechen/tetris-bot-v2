import gymnasium as gym
from gymnasium import spaces
import pygame
import numpy as np
from bfs_search import bfs_positions
from game import Tetris_Game
from grid import EMPTY_BLOCK
from game_view import GameView
from rotation_masks import ROTATIONS
from piece import Piece

PIECE_IDS = {
    "I": 0,
    "O": 1,
    "T": 2,
    "S": 3,
    "Z": 4,
    "J": 5,
    "L": 6
}

class TetrisEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 60}

    def __init__(self, render_mode=None):
        self.render_mode = render_mode
        self.game = Tetris_Game()
        
        self.observation_space = spaces.Box(
                low=0,
                high=7,
                shape = (40*10 + 1 + 5 + 1 + 50*3 , ),
                dtype = np.int8
        )

        #variable action-space
        self.action_space = spaces.Discrete(50)

        if render_mode == "human":
            pygame.init()
            pygame.display.set_caption("Tetris RL")
            self.game.view.init_display()

    def _get_obs(self):
        grid = (np.array(self.game.state.grid.matrix) != EMPTY_BLOCK).astype(np.int8).flatten()
        current_piece = np.array([PIECE_IDS[self.game.state.piece.name]], dtype=np.int8)
        queue = np.array([PIECE_IDS[name] for name in self.game.state.next_shape_ids], dtype=np.int8)
        hold_piece = np.array([PIECE_IDS[self.game.state.hold_piece] if self.game.state.hold_piece else 7],dtype=np.int8)
        placements = np.array(bfs_positions(self.game.state))
        placements_vec = np.zeros((50*3),dtype=np.int8)
        for i, (px,py,prot) in enumerate(placements[:50]):
            placements_vec[i*3:(i*3)+3] = [px,py,prot]
        return np.concatenate([grid,current_piece,queue,hold_piece, placements_vec])
    
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
            pygame.time.wait(50) 

        return obs, info

    def step(self, action):
        reward = 0

        lines_cleared, t_spin_type, pc = 0, 0, False

        placements = bfs_positions(self.game.state)

        if placements:
            if action < len(placements):
                px, py, prot = placements[action]
                self.game.state.piece.x = px
                self.game.state.piece.y = py
                self.game.state.piece.shape = ROTATIONS[self.game.state.piece.name][prot]
                lines_cleared, t_spin_type, pc = self.game.handle_piece_landing(text= False)
            else:
                self.game.state.game_over = True

        if lines_cleared == 1:
            reward += 1
        elif lines_cleared == 2:
            reward += 2
        elif lines_cleared == 3:
            reward += 5
        elif lines_cleared == 4:
            reward += 10

        if t_spin_type == 2:
            reward += 6
        elif t_spin_type == 1:
            reward += 1

        if pc:
            reward += 20

        if self.game.state.game_over:
            reward -= 100
        else:
            reward += 0.1

        terminated = self.game.state.game_over
        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self.game.view.render(self.game.state)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()
            pygame.time.wait(50) 

        pygame.time.wait(300)
        return observation, reward, terminated, False, info

    def close(self):
        pygame.display.quit()
        pygame.quit()

