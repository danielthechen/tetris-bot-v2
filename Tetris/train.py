import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv, VecNormalize
from tetris_Env import TetrisEnv
from bfs_search import bfs_positions
from sb3_contrib.common.wrappers import ActionMasker
from sb3_contrib import MaskablePPO
import numpy as np

def make_env():
    def _init():
        env = TetrisEnv(render_mode= "human")
        env = ActionMasker(env, mask_fn)
        return env
    return _init

def mask_fn(env):
    placements = bfs_positions(env.game.state)
    mask = np.zeros(env.action_space.n, dtype=bool)
    mask[:len(placements)] = True
    return mask


if __name__ == "__main__":
    gym.register(
        id="Tetris-v0",
        entry_point="tetris_Env:TetrisEnv",
    )

    env = gym.make("Tetris-v0")

    env = SubprocVecEnv([make_env() for _ in range(16)])

    env = VecNormalize(env, norm_obs=True, norm_reward=True, clip_obs = 10)

    model = MaskablePPO("MlpPolicy", env, verbose=1, n_steps= 4096, batch_size= 2048, learning_rate=1e-4)
    model.learn(total_timesteps=500000)
    model.save("ppo_tetris")
    env.save("vecnormalize_tetris.pkl")
    env.close()

    env = VecNormalize.load("vecnormalize_tetris.pkl",env)
    model = MaskablePPO.load("ppo_tetris", env=env)
    print("good")
    model.learn(total_timesteps=2000000)
    model.save("ppo_tetris_1")
    env.save("vecnormalize_tetris.pkl")
    env.close()


    eval_env = DummyVecEnv([make_env()])
    eval_env = VecNormalize.load("vecnormalize_tetris.pkl", eval_env)
    eval_env.training = False
    eval_env.norm_reward = False

    model = MaskablePPO.load("ppo_tetris_1", env=eval_env)

    obs = eval_env.reset()

    for _ in range(2000):
        action, _states = model.predict(obs, action_masks=mask_fn(eval_env.envs[0].env), deterministic=True)
        obs, reward, dones, info = eval_env.step(action)
        if dones[0]:
            obs = eval_env.reset()
    eval_env.close()