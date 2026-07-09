"""
=========================================================
GameBrain

Snake RL Environment

Responsible for:
1. Game State
2. Snake Movement
3. Reward Calculation
4. Rendering

NOTE:
This environment DOES NOT handle keyboard events.
Those belong to the play mode/controller.
=========================================================
"""
import pygame
import numpy as np

from environments.snake import Snake
from environments.food import Food
from environments.renderer import Renderer


class SnakeEnv:

    def __init__(
        self,
        grid_width=20,
        grid_height=20,
        render=False,
        render_callback=None
    ):

        self.grid_width = grid_width
        self.grid_height = grid_height

        self.render_game = render
        self.render_callback = render_callback

        self.snake = Snake(grid_width, grid_height)
        self.food = Food(grid_width, grid_height)

        self.renderer = None

        if render and render_callback is None:
            self.renderer = Renderer(
                grid_width,
                grid_height
            )

        self.score = 0

        self.food.spawn(
            self.snake.get_body()
        )

    # =====================================================
    # Reset
    # =====================================================

    def reset(self):

        self.snake.reset()

        self.score = 0

        self.food.spawn(
            self.snake.get_body()
        )

        return self.get_state()

    # =====================================================
    # State
    # =====================================================

    def get_state(self):

        head_x, head_y = self.snake.head()

        food_x, food_y = self.food.get_position()

        return np.array([

            head_x / self.grid_width,

            head_y / self.grid_height,

            food_x / self.grid_width,

            food_y / self.grid_height,

            self.snake.direction[0],

            self.snake.direction[1],

            self.snake.length(),

            abs(food_x - head_x),

            abs(food_y - head_y),

            int(food_x < head_x),

            int(food_x > head_x),

            int(food_y < head_y)

        ], dtype=np.float32)

    # =====================================================
    # Step
    # =====================================================

    def step(self, action):

        directions = {

            0: (0, -1),
            1: (0, 1),
            2: (-1, 0),
            3: (1, 0)

        }

        self.snake.set_direction(
            directions[action]
        )

        head_x, head_y = self.snake.head()
        food_x, food_y = self.food.get_position()

        old_distance = (
            abs(food_x - head_x)
            + abs(food_y - head_y)
        )

        self.snake.move()

        new_head_x, new_head_y = self.snake.head()

        new_distance = (
            abs(food_x - new_head_x)
            + abs(food_y - new_head_y)
        )

        reward = 0.05

        if new_distance < old_distance:
            reward += 0.3
        else:
            reward -= 0.3

        done = False

        if self.snake.is_dead():

            reward = -20

            done = True

        elif self.food.eaten(
            self.snake.head()
        ):

            reward = 20

            self.score += 1

            self.snake.grow()

            self.food.spawn(
                self.snake.get_body()
            )

        if self.render_game or self.render_callback is not None:
            self.render()

        return (
            self.get_state(),
            reward,
            done,
            self.score
        )

    # =====================================================
    # Render
    # =====================================================

    def render(self):

        if self.render_callback is not None:

            self.render_callback(

                self.snake.get_body(),

                self.food.get_position(),

                self.score

            )

        elif self.renderer is not None:

            self.renderer.draw(

                self.snake.get_body(),

                self.food.get_position(),

                self.score

            )
            pygame.time.delay(80)
    # =====================================================
    # Close
    # =====================================================

    def close(self):

        if self.renderer is not None:

            self.renderer.close()


if __name__ == "__main__":

    env = SnakeEnv(render=True)

    state = env.reset()

    done = False

    while not done:

        action = np.random.randint(0, 4)

        state, reward, done, _ = env.step(action)

    env.close()