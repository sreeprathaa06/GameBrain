"""
=========================================================
GameBrain

Human Controller

Converts keyboard events into Snake actions.

Action Mapping
0 -> UP
1 -> DOWN
2 -> LEFT
3 -> RIGHT
=========================================================
"""

import pygame


class HumanController:

    def __init__(self):
        self.action = 3  # Start moving right

    def process_event(self, event):

        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_UP:
            self.action = 0

        elif event.key == pygame.K_DOWN:
            self.action = 1

        elif event.key == pygame.K_LEFT:
            self.action = 2

        elif event.key == pygame.K_RIGHT:
            self.action = 3

    def get_action(self):
        return self.action