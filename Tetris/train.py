import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv, VecNormalize
from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback
from tetris_Env import TetrisEnv
from bfs_search import bfs_positions
from sb3_contrib.common.wrappers import ActionMasker
from sb3_contrib import MaskablePPO
import numpy as np

def make_env():
    def _init():
        env = TetrisEnv(render_mode= None)
        env = ActionMasker(env, mask_fn)
        return env
    return _init

def mask_fn(env):
    placements = bfs_positions(env.game.state)
    mask = np.zeros(env.action_space.n, dtype=bool)
    mask[:len(placements)] = True
    return mask


if __name__ == "__main__":

    checkpoint_callback = CheckpointCallback(
    save_freq=2_000_000,
    save_path="./models/",
    name_prefix="tetris_agent"
)

    eval_env = DummyVecEnv([make_env()])
    eval_env = VecNormalize.load("Tetris_Env_V0.1.pkl", eval_env)
    eval_env.training = False
    eval_env.norm_reward = False

    eval_callback = EvalCallback(
    eval_env,
    best_model_save_path="./models/best_model/",
    log_path="./logs/",
    eval_freq=1_000_000,
    deterministic=True,
    render=False
)

    env = SubprocVecEnv([make_env() for _ in range(8)])

    # env = VecNormalize(env, norm_obs=True, norm_reward=True, clip_obs = 10)

    # model = MaskablePPO("MlpPolicy", env, verbose=1, n_steps= 4096, batch_size= 2048, learning_rate=1e-4)
    # model.learn(total_timesteps=10000)
    # model.save("ppo_heuristic_tetris")
    # env.save("Tetris_Env_V0.1.pkl")
    # env.close()

    env = VecNormalize.load("Tetris_Env_V0.1.pkl", env)
    model = MaskablePPO.load("ppo_heuristic_tetris", env=env)
    print("good")
    model.learn(total_timesteps=6_000_000, callback=[checkpoint_callback, eval_callback])
    model.save("ppo_heuristic_tetris")
    env.save("Tetris_Env_V0.1.pkl")
    env.close()

    # model = MaskablePPO.load("ppo_heuristic_tetris", env=eval_env)

    # obs = eval_env.reset()

    # for _ in range(2000):
    #     action, _states = model.predict(obs, action_masks=mask_fn(eval_env.envs[0].env), deterministic=True)
    #     obs, reward, dones, info = eval_env.step(action)
    #     if dones[0]:
    #         obs = eval_env.reset()
    # eval_env.close()