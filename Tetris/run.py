from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from stable_baselines3.common.monitor import Monitor
from tetris_Env import TetrisEnv
from bfs_search import bfs_positions
from sb3_contrib.common.wrappers import ActionMasker
from sb3_contrib import MaskablePPO
import numpy as np

def make_env():
    def _init():
        env = TetrisEnv(render_mode= "human")
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
    eval_env = eval_env = VecNormalize.load("Tetris_Env_v21.pkl", eval_env)
    #model = MaskablePPO.load("ppo_tetris_v26.zip", env=eval_env)
    model = MaskablePPO.load("./models/tetris_bot_v27.1_500000_steps.zip", env=eval_env)
    obs = eval_env.reset()
    for _ in range(2000):
        
        action, _states = model.predict(obs, action_masks=mask_fn(eval_env.envs[0].env), deterministic=True)
        obs, reward, dones, info = eval_env.step(action)
    eval_env.close()