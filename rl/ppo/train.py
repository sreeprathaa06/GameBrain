"""
=========================================================
GameBrain

PPO Training

=========================================================
"""

import os
import sys

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            ".."
        )
    )
)

from environments.snake_env import SnakeEnv
from rl.common.logger import TrainingLogger
from ppo_model import PPOModel
from memory import PPOMemory


EPISODES = 30


def train():

    env = SnakeEnv(render=True)

    model = PPOModel(
        state_size=12,
        action_size=4
    )

    memory = PPOMemory()

    logger = TrainingLogger()

    print()
    print("=" * 60)
    print("PPO Training Started")
    print("=" * 60)

    best_reward = float("-inf")

    for episode in range(EPISODES):

        state = env.reset()

        done = False

        total_reward = 0

        while not done:

            action, log_prob = model.act(state)

            value = model.evaluate(state)

            next_state, reward, done, info = env.step(action)

            memory.store(
                state,
                action,
                reward,
                next_state,
                done,
                log_prob,
                value
            )

            state = next_state

            total_reward += reward

        logger.log(
            episode=episode + 1,
            reward=total_reward,
            loss=0,
            epsilon=0
        )

        if total_reward > best_reward:

            best_reward = total_reward

            model.save()

            print("Best PPO Model Saved!")

        print(
            f"Episode {episode + 1:02d}"
            f" | Reward = {total_reward}"
            f" | Experiences = {memory.size()}"
        )

        memory.clear()

    env.close()

    print()
    print("=" * 60)
    print("PPO Training Finished")
    print("=" * 60)


if __name__ == "__main__":

    train()