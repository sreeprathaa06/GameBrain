"""
===========================================================
GameBrain
Dummy Snake Environment
===========================================================

This is a temporary environment used until the
real Snake environment is completed.

It follows the Gymnasium API.

Author : GameBrain Team
"""

import random
import numpy as np


class DummySnakeEnv:

    def __init__(self):

        self.state_size = 12

        self.action_size = 4

        self.max_steps = 100

        self.current_step = 0

        self.state = None

    # ============================================
    # Reset Environment
    # ============================================

    def reset(self):

        self.current_step = 0

        self.state = np.zeros(
            self.state_size,
            dtype=np.float32
        )

        return self.state

    # ============================================
    # Perform One Action
    # ============================================

    def step(self, action):

        self.current_step += 1

        next_state = np.random.rand(
            self.state_size
        ).astype(np.float32)

        reward = random.choice(
            [-1, 0, 1]
        )

        done = self.current_step >= self.max_steps

        info = {
            "step": self.current_step
        }

        self.state = next_state

        return (

            next_state,

            reward,

            done,

            info

        )

    # ============================================
    # Render
    # ============================================

    def render(self):

        print()

        print("Current Step :", self.current_step)

        print("State :", self.state)

        print()

    # ============================================
    # Close
    # ============================================

    def close(self):

        print("Environment Closed.")



if __name__ == "__main__":

    env = DummySnakeEnv()

    state = env.reset()

    print("Initial State")

    print(state)

    print()

    for i in range(5):

        action = random.randint(0, 3)

        next_state, reward, done, info = env.step(action)

        print("------------------------")

        print("Action :", action)

        print("Reward :", reward)

        print("Done :", done)

        print(info)

    env.close()