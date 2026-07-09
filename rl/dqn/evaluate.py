"""
=========================================================
GameBrain

DQN Evaluation

Runs a trained model without exploration.

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

from environments.dummy_snake_env import DummySnakeEnv
from agent import DQNAgent


EPISODES = 5


def evaluate():

    env = DummySnakeEnv()

    agent = DQNAgent(
        state_size=12,
        action_size=4
    )

    model_path = "gamebrain_dqn.pth"

    agent.load_model(model_path)

    print()
    print("=" * 60)
    print("Evaluation Started")
    print("=" * 60)

    total_reward = 0

    for episode in range(EPISODES):

        state = env.reset()

        done = False

        episode_reward = 0

        while not done:

            action = agent.predict(state)

            next_state, reward, done, info = env.step(action)

            state = next_state

            episode_reward += reward

        total_reward += episode_reward

        print(
            f"Episode {episode + 1} Reward : {episode_reward}"
        )

    print()
    print("=" * 60)

    print(
        f"Average Reward : {total_reward / EPISODES:.2f}"
    )

    print("=" * 60)

    env.close()


if __name__ == "__main__":

    evaluate()