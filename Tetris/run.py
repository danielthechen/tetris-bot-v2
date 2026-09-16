from ast import mod

from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from stable_baselines3.common.monitor import Monitor
from tetris_Env import TetrisEnv
from bfs_search import bfs_positions
from sb3_contrib.common.wrappers import ActionMasker
from sb3_contrib import MaskablePPO
import numpy as np

def make_env():
    def _init():
        env = TetrisEnv(render_mode= "human", key_playback=0)
        env = Monitor(env)
        env = ActionMasker(env, mask_fn)
        return env
    return _init

def mask_fn(env):
    base_env = getattr(env, "env", env)
    base_env = getattr(base_env, "unwrapped", base_env)

    placements = base_env.cached_placements
    mask = np.zeros(base_env.action_space.n, dtype=bool)
    mask [0] = not base_env.game.state.turn_held
    mask[1:len(placements)+1] = True
    return mask

# ./models/tetris_bot_v3.0_8000000_steps

if __name__ == "__main__":
    eval_env = DummyVecEnv([make_env()])

    version = 25
    steps = 5000000

    #In-Progress
    # eval_env = VecNormalize.load(f"./models/v2/v{version}/tetris_bot_expansion_v{version}_vecnormalize_{steps}_steps.pkl", eval_env)
    # model = MaskablePPO.load(f"./models/v2/v{version}/tetris_bot_expansion_v{version}_{steps}_steps.zip", env=eval_env)

    #Start anew
    eval_env = VecNormalize.load(f"./history/oh_encoded/env/Tetris_Env_expansion_v{version}.pkl", eval_env)
    model = MaskablePPO.load(f"./history/oh_encoded/ppo/ppo_tetris_expansion_v{version}.zip", env=eval_env)

    obs = eval_env.reset()
    for _ in range(2000):
        
        action, _states = model.predict(obs, action_masks=mask_fn(eval_env.envs[0].env), deterministic=True)
        obs, reward, dones, info = eval_env.step(action)
    eval_env.close()