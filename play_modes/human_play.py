"""
=========================================================
GameBrain

Human Play Mode

=========================================================
"""

import pygame

from controllers.human_controller import HumanController
from environments.snake_env import SnakeEnv


class HumanPlay:

    def __init__(self):

        self.env = SnakeEnv(render=True)
        self.controller = HumanController()

        pygame.init()
        self.clock = pygame.time.Clock()

    def run(self):

        self.env.reset()

        running = True

        while running:

            # Limit the game to 10 FPS
            self.clock.tick(10)

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False

                self.controller.process_event(event)

            action = self.controller.get_action()

            _, _, done, _ = self.env.step(action)

            if done:

                print(f"Game Over! Score: {self.env.score}")

                waiting = True

                while waiting:

                    for event in pygame.event.get():

                        if event.type == pygame.QUIT:
                            waiting = False
                            running = False

                        elif event.type == pygame.KEYDOWN:

                            # Press R to restart
                            if event.key == pygame.K_r:
                                self.env.reset()
                                waiting = False

                            # Press ESC to exit
                            elif event.key == pygame.K_ESCAPE:
                                waiting = False
                                running = False

        self.env.close()


if __name__ == "__main__":

    HumanPlay().run()