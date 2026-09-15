import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv, VecNormalize
from stable_baselines3.common.utils import FloatSchedule
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback, BaseCallback
from tetris_Env import TetrisEnv
from sb3_contrib.common.wrappers import ActionMasker
from sb3_contrib import MaskablePPO
import numpy as np

class HoleLoggingCallback(BaseCallback):
    def __init__(self, log_freq=100, verbose=0):
        super().__init__(verbose)
        self.log_freq = log_freq
        self.episode_holes_made = []
        self.episode_lines_cleared = []
        self.episode_holes_per_step = []
    def _on_step(self) -> bool:
        for info in self.locals["infos"]:
            if "episode" in info:
                self.episode_holes_made.append(info["holes_made"])
                self.episode_lines_cleared.append(info["ep_lines_cleared"])
                self.episode_holes_per_step.append(info["holes_made"]/info["steps_made"])
        if len(self.episode_holes_made) >= self.log_freq:
            self.logger.record("custom/episode_holes_made_mean", np.mean(self.episode_holes_made))
            self.logger.record("custom/ep_lines_cleared", np.mean(self.episode_lines_cleared))
            self.logger.record("custom/episode_holes_per_step", np.mean(self.episode_holes_per_step))
            self.episode_holes_made = []
            self.episode_lines_cleared = []
            self.episode_holes_per_step = []
        return True

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

    placements = base_env.cached_placements
    mask = np.zeros(base_env.action_space.n, dtype=bool)
    mask [0] = not base_env.game.state.turn_held
    mask[1:len(placements)+1] = True
    return mask

if __name__ == "__main__":

    checkpoint_callback = CheckpointCallback(
    save_freq=156_250,
    save_path="./models/v2/v24/",
    name_prefix="tetris_bot_expansion_v24",
    save_vecnormalize= True
)
    
    env = SubprocVecEnv([make_env() for _ in range(32)])

    # env = VecNormalize(env, norm_obs=True, norm_reward=True, clip_obs = 10)
    # policy_kwargs = dict(
    #     net_arch=dict(pi=[256, 256], vf=[256, 256])
    # )
    # model = MaskablePPO("MlpPolicy", env, 
    #                     verbose=1,
    #                     n_steps= 1024, 
    #                     batch_size= 2048, 
    #                     ent_coef=0.01,
    #                     vf_coef=1.0,
    #                     learning_rate=1e-4,
    #                     target_kl=0.03,
    #                     clip_range=0.15,
    #                     policy_kwargs=policy_kwargs,
    #                     device='mps', 
    #                     tensorboard_log="./runs/tetris_project/v2/")
    # model.learn(total_timesteps=10_000)
    # model.save("ppo_tetris_expansion_v0.zip")
    # env.save("Tetris_Env_expansion_v0.pkl")

    env = VecNormalize.load("./history/oh_encoded/env/Tetris_Env_expansion_v23.pkl", env)
    model = MaskablePPO.load("./history/oh_encoded/ppo/ppo_tetris_expansion_v23.zip", env=env, device='mps', tensorboard_log="./runs/tetris_project/v2/")
    # env = VecNormalize.load("./models/v2/v23.1/tetris_bot_expansion_v23.1_vecnormalize_20000000_steps.pkl", env)
    # model = MaskablePPO.load("./models/v2/v23.1/tetris_bot_expansion_v23.1_20000000_steps.zip", env=env, device='mps', tensorboard_log = "./runs/tetris_project/v2/")
    model.learning_rate = FloatSchedule(1e-4)
    model.lr_schedule = FloatSchedule(1e-4)
    # model.clip_range = FloatSchedule(0.15)
    # model.target_kl = 0.03
    model.ent_coef = 0.02
    # model.vf_coef = 1.0
    print(model.lr_schedule(1.0))
    print(model.ent_coef)
    print("Learning!!!")
    model.learn(total_timesteps=45_000_000, callback=[checkpoint_callback, HoleLoggingCallback()])
    model.save("./history/oh_encoded/ppo/ppo_tetris_expansion_v24.zip")
    env.save("./history/oh_encoded/env/Tetris_Env_expansion_v24.pkl")
    env.close()

    # ./models/tetris_agent_1000000_steps

    # eval_env = DummyVecEnv([make_env()])
    # eval_env = eval_env = VecNormalize.load("Tetris_Env_V0.5.pkl", eval_env)
    # model = MaskablePPO.load("ppo_tetris_v2.zip", env=eval_env)
    # obs = eval_env.reset()
    # for _ in range(2000):
    #     action, _states = model.predict(obs, action_masks=mask_fn(eval_env.envs[0].env), deterministic=True)
    #     obs, reward, dones, info = eval_env.step(action)
    #     if dones[0]:
    #         obs = eval_env.reset()
    # eval_env.close()