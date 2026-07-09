import pygame
import numpy as np
import random

class PingPongEnv:
    def __init__(self, render=False, render_callback=None):
        self.width = 400
        self.height = 400
        self.render_game = render
        self.render_callback = render_callback

        self.paddle_h = 60
        self.paddle_w = 10
        self.ball_size = 10

        if render:
            if not pygame.get_init():
                pygame.init()
            if render_callback is None:
                self.display = pygame.display.set_mode((self.width, self.height))
                pygame.display.set_caption("Ping Pong Environment")
                self.clock = pygame.time.Clock()
            else:
                self.display = pygame.Surface((self.width, self.height))

        self.reset()

    def reset(self):
        self.paddle_y = self.height / 2 - self.paddle_h / 2
        self.opp_y = self.height / 2 - self.paddle_h / 2
        self.ball_x = self.width / 2
        self.ball_y = self.height / 2
        self.ball_dx = 5 * random.choice([1, -1])
        self.ball_dy = 5 * random.choice([1, -1])

        self.score = 0
        self.frame_iteration = 0
        return self.get_state()

    def get_state(self):
        return np.array([
            self.paddle_y / self.height,
            self.opp_y / self.height,
            self.ball_x / self.width,
            self.ball_y / self.height,
            self.ball_dx / 10.0,
            self.ball_dy / 10.0
        ], dtype=np.float32)

    def step(self, action):
        self.frame_iteration += 1

        # Action: 0 = stay, 1 = up, 2 = down
        if action == 1:
            self.paddle_y -= 10
        elif action == 2:
            self.paddle_y += 10

        self.paddle_y = max(0, min(self.height - self.paddle_h, self.paddle_y))

        # Opponent simple AI
        if self.opp_y + self.paddle_h/2 < self.ball_y:
            self.opp_y += 5
        elif self.opp_y + self.paddle_h/2 > self.ball_y:
            self.opp_y -= 5
        self.opp_y = max(0, min(self.height - self.paddle_h, self.opp_y))

        # Ball movement
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # Wall collisions (top/bottom)
        if self.ball_y <= 0 or self.ball_y >= self.height - self.ball_size:
            self.ball_dy *= -1

        reward = 0
        done = False

        # Paddle collisions
        # Player (Left)
        if self.ball_x <= 20 and self.paddle_y <= self.ball_y <= self.paddle_y + self.paddle_h:
            self.ball_dx *= -1
            self.ball_x = 20
            reward = 10
            self.score += 1
        # Opponent (Right)
        elif self.ball_x >= self.width - 20 - self.ball_size and self.opp_y <= self.ball_y <= self.opp_y + self.paddle_h:
            self.ball_dx *= -1
            self.ball_x = self.width - 20 - self.ball_size

        # Out of bounds
        if self.ball_x < 0:
            reward = -10
            done = True
        elif self.ball_x > self.width:
            reward = 10
            done = True
            
        if self.frame_iteration > 1000:
            done = True

        if self.render_game:
            self.render()

        return self.get_state(), reward, done, self.score

    def render(self):
        self.display.fill((0, 0, 0))
        pygame.draw.rect(self.display, (255, 255, 255), (10, self.paddle_y, self.paddle_w, self.paddle_h))
        pygame.draw.rect(self.display, (255, 255, 255), (self.width - 20, self.opp_y, self.paddle_w, self.paddle_h))
        pygame.draw.rect(self.display, (255, 255, 255), (self.ball_x, self.ball_y, self.ball_size, self.ball_size))
        
        if self.render_callback:
            self.render_callback(self.display)
            return
            
        pygame.display.flip()
        self.clock.tick(30)
