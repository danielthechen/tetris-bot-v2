from enum import Enum
import gymnasium as gym
from gymnasium import spaces
import pygame
import numpy as np
from game import Tetris_Game
from grid import EMPTY_BLOCK
from game_view import GameView

PIECE_IDS = {
    "I": 0,
    "O": 1,
    "T": 2,
    "S": 3,
    "Z": 4,
    "J": 5,
    "L": 6
}

class Actions(Enum):
    left = 0
    right = 1
    turn_cw = 2
    turn_ccw = 3
    turn_180 = 4
    hard_drop = 5
    soft_drop = 6
    hold = 7

class TetrisEnv(gym.Env):
    metadata = {"render_modes": ["human","rgb_array"], "render_fps": 60}

    def __init__(self, render_mode=None):
        self.render_mode = render_mode
        self.game = Tetris_Game()
        
        self.observation_space = spaces.Box(
                low=0,
                high=7,
                shape = (40*10 + 1 + 5 + 1,),
                dtype = np.int8
        )

        self.action_space = spaces.Discrete(8)
        if render_mode == "human":
            self.view = GameView()
            pygame.init()
            pygame.display.set_caption("Tetris RL")
            self.view.init_display()

    def _get_obs(self):
        grid = (np.array(self.game.state.grid.matrix) != EMPTY_BLOCK).astype(np.int8).flatten()
        current_piece = np.array([PIECE_IDS[self.game.state.piece.name]], dtype=np.int8)
        queue = np.array([PIECE_IDS[name] for name in self.game.state.next_shape_ids], dtype=np.int8)
        hold_piece = np.array([PIECE_IDS[self.game.state.hold_piece] if self.game.state.hold_piece else 7],dtype=np.int8)
        return np.concatenate([grid,current_piece,queue,hold_piece])
    
    def _get_info(self):
        return {"score":0}

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.game.state = self.game.get_initial_state()
        obs = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return obs, info

    def step(self, action):
        reward = 0
        
        if action == Actions.left.value:
            self.game.move_piece(-1, 0)
        elif action == Actions.right.value:
            self.game.move_piece(1, 0)
        elif action == Actions.turn_cw.value:
            self.game.rotate_piece(-1)
        elif action == Actions.turn_ccw.value:
            self.game.rotate_piece(1)
        elif action == Actions.turn_180.value:
            self.game.rotate_piece(2)
        elif action == Actions.hard_drop.value:
            self.game.hard_drop()
            reward += 100
        elif action == Actions.soft_drop.value:
            self.game.instant_soft_drop()
            reward += 1
        elif action == Actions.hold.value:
            self.game.hold()
            self.game.state.turn_held = True

        self.game.update(inputs={
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False,
            pygame.K_z: False,
            pygame.K_BACKQUOTE: False,
        }, ticks=1)

        if self.game.state.lines_cleared > 0:
            reward += self.game.state.lines_cleared * 10
        if self.game.state.game_over:
            reward -= 1000
        
        terminated = self.game.state.game_over
        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()
        return observation, reward, terminated, False, info

    def render(self):
        if self.render_mode == "rgb_array":
            return self._render_frame()

    def _render_frame(self):
        self.view.render(self.game.state)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
        pygame.time.wait(50) 

    def close(self):
        pygame.display.quit()
        pygame.quit()

