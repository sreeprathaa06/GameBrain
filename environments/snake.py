"""
=========================================================
GameBrain

Snake Class

Handles:
1. Snake Creation
2. Snake Movement
3. Snake Growth
4. Collision Detection
5. Reset

=========================================================
"""

from collections import deque


class Snake:

    def __init__(self, grid_width=20, grid_height=20):

        self.grid_width = grid_width
        self.grid_height = grid_height

        self.reset()

    # =====================================================
    # Reset Snake
    # =====================================================

    def reset(self):

        start_x = self.grid_width // 2
        start_y = self.grid_height // 2

        self.body = deque([
            (start_x, start_y)
        ])

        self.direction = (1, 0)

        self.grow_next = False

    # =====================================================
    # Head Position
    # =====================================================

    def head(self):

        return self.body[0]

    # =====================================================
    # Change Direction
    # =====================================================

    def set_direction(self, direction):

        opposite = (
            -self.direction[0],
            -self.direction[1]
        )

        if direction != opposite:
            self.direction = direction

    # =====================================================
    # Move Snake
    # =====================================================

    def move(self):

        head_x, head_y = self.head()

        dx, dy = self.direction

        new_head = (
            head_x + dx,
            head_y + dy
        )

        self.body.appendleft(new_head)

        if self.grow_next:
            self.grow_next = False
        else:
            self.body.pop()

    # =====================================================
    # Grow Snake
    # =====================================================

    def grow(self):

        self.grow_next = True

    # =====================================================
    # Wall Collision
    # =====================================================

    def hit_wall(self):

        x, y = self.head()

        return (
            x < 0 or
            x >= self.grid_width or
            y < 0 or
            y >= self.grid_height
        )

    # =====================================================
    # Self Collision
    # =====================================================

    def hit_self(self):

        return self.head() in list(self.body)[1:]

    # =====================================================
    # Game Over?
    # =====================================================

    def is_dead(self):

        return self.hit_wall() or self.hit_self()

    # =====================================================
    # Length
    # =====================================================

    def length(self):

        return len(self.body)

    # =====================================================
    # Body
    # =====================================================

    def get_body(self):

        return list(self.body)


# =========================================================
# Test
# =========================================================

if __name__ == "__main__":

    snake = Snake()

    print("Initial Body:", snake.get_body())

    snake.move()

    print("After Move:", snake.get_body())

    snake.grow()

    snake.move()

    print("After Grow:", snake.get_body())

    print("Snake Length:", snake.length())

    print("Dead?", snake.is_dead())