"""
=========================================================
GameBrain

Food Class

Handles:
1. Food Generation
2. Food Respawning
3. Collision-safe Placement

=========================================================
"""

import random


class Food:

    def __init__(self, grid_width=20, grid_height=20):

        self.grid_width = grid_width
        self.grid_height = grid_height

        self.position = (0, 0)

    # =====================================================
    # Spawn Food
    # =====================================================

    def spawn(self, snake_body):

        while True:

            x = random.randint(0, self.grid_width - 1)

            y = random.randint(0, self.grid_height - 1)

            position = (x, y)

            if position not in snake_body:

                self.position = position

                return

    # =====================================================
    # Get Position
    # =====================================================

    def get_position(self):

        return self.position

    # =====================================================
    # Check if Snake Eats Food
    # =====================================================

    def eaten(self, snake_head):

        return snake_head == self.position


# =========================================================
# Testing
# =========================================================

if __name__ == "__main__":

    snake = [

        (10, 10),

        (10, 11),

        (10, 12)

    ]

    food = Food()

    food.spawn(snake)

    print("Snake Body :", snake)

    print("Food Position :", food.get_position())

    print("Food Eaten ?", food.eaten((10, 10)))
    