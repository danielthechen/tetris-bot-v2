import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv, VecNormalize
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback
from tetris_Env import TetrisEnv
from bfs_search import bfs_positions
from sb3_contrib.common.wrappers import ActionMasker
from sb3_contrib import MaskablePPO
import numpy as np

def make_env():
    def _init():
        env = TetrisEnv(render_mode= None)
        env = Monitor(env)
        env = ActionMasker(env, mask_fn)
        return env
    return _init

def mask_fn(env):
    base_env = getattr(env, "env", env)
    base_env = getattr(base_env, "unwrapped", base_env)

    placements = bfs_positions(base_env.game.state)
    mask = np.zeros(base_env.action_space.n, dtype=bool)
    mask[:len(placements)] = True
    return mask

if __name__ == "__main__":

    checkpoint_callback = CheckpointCallback(
    save_freq=31_250,
    save_path="./models/",
    name_prefix="tetris_bot"
)

    eval_env = DummyVecEnv([make_env()])
    eval_env = VecNormalize.load("Tetris_Env_V0.5.pkl", eval_env)
    eval_env.training = False
    eval_env.norm_reward = False

    eval_callback = EvalCallback(
    eval_env,
    best_model_save_path="./models/best_model/",
    log_path="./logs/",
    eval_freq=31_250,
    deterministic=True,
    render=False
)

    env = SubprocVecEnv([make_env() for _ in range(16)])

    # env = VecNormalize(env, norm_obs=True, norm_reward=True, clip_obs = 10)
    # model = MaskablePPO("MlpPolicy", env, verbose=1, n_steps= 512, batch_size= 1024, ent_coef=0.01,learning_rate=1e-4, device='mps', tensorboard_log="./runs/tetris_project")
    # model.learn(total_timesteps=10000)
    # model.save("ppo_tetris_v2.zip")
    # env.save("Tetris_Env_V0.5.pkl")
    # env.close()

    env = VecNormalize.load("Tetris_Env_V0.5.pkl", env)
    model = MaskablePPO.load("./models/tetris_agent_500000_steps.zip", env=env, device='mps')
    print("Learning!!!")
    model.learn(total_timesteps=8_000_000, callback=[checkpoint_callback, eval_callback])
    model.save("ppo_tetris_v2.zip")
    env.save("Tetris_Env_V0.5.pkl")
    env.close()

    # ./models/tetris_agent_1000000_steps

    # eval_env = DummyVecEnv([make_env()])
    # eval_env = eval_env = VecNormalize.load("Tetris_Env_V0.5.pkl", eval_env)
    # model = MaskablePPO.load("./models/tetris_agent_500000_steps.zip", env=eval_env)
    # obs = eval_env.reset()
    # for _ in range(2000):
    #     action, _states = model.predict(obs, action_masks=mask_fn(eval_env.envs[0].env), deterministic=True)
    #     obs, reward, dones, info = eval_env.step(action)
    #     if dones[0]:
    #         obs = eval_env.reset()
    # eval_env.close()