import gymnasium as gym
from tetris_Env import TetrisEnv
from stable_baselines3 import PPO
import pygame

gym.register(
    id="Tetris-v0",
    entry_point="tetris_Env:TetrisEnv",
)

env = gym.make("Tetris-v0")

model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=50000)

env = gym.make("Tetris-v0", render_mode="human")

obs, info = env.reset()
for _ in range(2000):  # play 200 steps
    action, _states = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, info = env.step(action)

    if terminated or truncated:
        obs, info = env.reset()

env.close()