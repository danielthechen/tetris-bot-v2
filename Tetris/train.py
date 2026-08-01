import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv, VecNormalize
from tetris_Env import TetrisEnv

def make_env():
    return TetrisEnv(render_mode= None)


if __name__ == "hi":
    env = SubprocVecEnv([make_env for _ in range(16)])

    env = VecNormalize(env, norm_obs=True, norm_reward=True, clip_obs = 10)

    # gym.register(
    #     id="Tetris-v0",
    #     entry_point="tetris_Env:TetrisEnv",
    # )

    # env = gym.make("Tetris-v0")

    model = PPO("MlpPolicy", env, verbose=1, n_steps= 8192, batch_size= 2048, learning_rate=1e-4)
    model.learn(total_timesteps=5000000)
    model.save("ppo_tetris")
    env.save("vecnormalize_tetris.pkl")


    eval_env = TetrisEnv(render_mode="human")
    eval_env = VecNormalize.load("vecnormalize_tetris.pkl", eval_env)
    eval_env.training = False
    eval_env.norm_reward = False

    model = PPO.load("ppo_tetris", env=eval_env)

    obs, info = eval_env.reset()
    for _ in range(200):
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = eval_env.step(action)
        if terminated or truncated:
            obs, info = eval_env.reset()

    eval_env.close()

    # env = gym.make("Tetris-v0", render_mode="human")

    # obs, info = env.reset()
    # for _ in range(200):  # play 200 steps
    #     action, _states = model.predict(obs, deterministic=True)
    #     obs, reward, terminated, truncated, info = env.step(action)

    #     if terminated or truncated:
    #         obs, info = env.reset()

    # env.close()