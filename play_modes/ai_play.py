"""
=========================================================
GameBrain

AI Play Mode

=========================================================
"""

import pygame

from environments.snake_env import SnakeEnv
from rl.dqn.agent import DQNAgent


class AIPlay:

    def __init__(self):

        self.env = SnakeEnv(render=True)

        self.agent = DQNAgent(
            state_size=12,
            action_size=4
        )

        # Load trained model
        self.agent.load_model("best_dqn_model.pth")

        pygame.init()

        self.clock = pygame.time.Clock()

    # =====================================================

    def run(self):

        state = self.env.reset()

        running = True

        while running:

            self.clock.tick(12)

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    running = False

            action = self.agent.predict(state)

            state, reward, done, info = self.env.step(action)

            if done:

                state = self.env.reset()

        self.env.close()


if __name__ == "__main__":

    AIPlay().run()