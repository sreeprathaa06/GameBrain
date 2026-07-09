import pygame
import numpy as np
import random

class FlappyBirdEnv:
    def __init__(self, render=False, render_callback=None):
        self.width = 400
        self.height = 500
        self.render_game = render
        self.render_callback = render_callback

        self.bird_x = 50
        self.bird_size = 20
        self.gravity = 1.0
        self.flap_strength = -10
        
        self.pipe_width = 50
        self.pipe_gap = 120
        self.pipe_vel_x = -4

        if render or render_callback is not None:
            if not pygame.get_init():
                pygame.init()
            if render_callback is None:
                self.display = pygame.display.set_mode((self.width, self.height))
                pygame.display.set_caption("Flappy Bird Environment")
                self.clock = pygame.time.Clock()
            else:
                self.display = pygame.Surface((self.width, self.height))

        self.reset()

    def reset(self):
        self.bird_y = self.height / 2
        self.bird_vel_y = 0
        
        self.pipes = [self.create_pipe(self.width + 100)]
        
        self.score = 0
        self.frame_iteration = 0
        return self.get_state()

    def create_pipe(self, x):
        h = random.randint(50, self.height - self.pipe_gap - 50)
        return {'x': x, 'h': h}

    def get_state(self):
        # find closest pipe in front of bird
        closest_pipe = self.pipes[0]
        for p in self.pipes:
            if p['x'] + self.pipe_width > self.bird_x:
                closest_pipe = p
                break

        return np.array([
            self.bird_y / self.height,
            self.bird_vel_y / 15.0,
            (closest_pipe['x'] - self.bird_x) / self.width,
            closest_pipe['h'] / self.height
        ], dtype=np.float32)

    def step(self, action):
        self.frame_iteration += 1
        reward = 0.1
        done = False

        # Action: 0 = do nothing, 1 = flap
        if action == 1:
            self.bird_vel_y = self.flap_strength

        self.bird_vel_y += self.gravity
        self.bird_y += self.bird_vel_y

        # update pipes
        for p in self.pipes:
            p['x'] += self.pipe_vel_x

        if self.pipes and self.pipes[0]['x'] < -self.pipe_width:
            self.pipes.pop(0)

        if self.pipes[-1]['x'] < self.width - 200:
            self.pipes.append(self.create_pipe(self.width))

        # Check collisions
        # Floor / Ceiling
        if self.bird_y > self.height - self.bird_size or self.bird_y < 0:
            done = True
            reward = -10

        # Pipes
        for p in self.pipes:
            if self.bird_x + self.bird_size > p['x'] and self.bird_x < p['x'] + self.pipe_width:
                # check gap
                if self.bird_y < p['h'] or self.bird_y + self.bird_size > p['h'] + self.pipe_gap:
                    done = True
                    reward = -10
            elif p['x'] == self.bird_x:
                reward = 10
                self.score += 1

        if self.render_game or self.render_callback is not None:
            self.render()

        return self.get_state(), reward, done, self.score

    def render(self):
        self.display.fill((135, 206, 250))
        center = (int(self.bird_x + self.bird_size / 2), int(self.bird_y + self.bird_size / 2))
        radius = int(self.bird_size / 2)
        
        # Body (Yellow)
        pygame.draw.circle(self.display, (255, 200, 0), center, radius)
        
        # Eye (White)
        eye_center = (int(center[0] + radius / 2), int(center[1] - radius / 3))
        pygame.draw.circle(self.display, (255, 255, 255), eye_center, radius // 2)
        
        # Pupil (Black)
        pygame.draw.circle(self.display, (0, 0, 0), eye_center, radius // 4)
        
        # Beak (Orange)
        beak_points = [
            (center[0] + radius - 2, center[1]),
            (center[0] + radius + 8, center[1] + 2),
            (center[0] + radius - 2, center[1] + 6)
        ]
        pygame.draw.polygon(self.display, (255, 140, 0), beak_points)
        
        for p in self.pipes:
            # Top pipe
            pygame.draw.rect(self.display, (34, 139, 34), (p['x'], 0, self.pipe_width, p['h']))
            # Bottom pipe
            pygame.draw.rect(self.display, (34, 139, 34), (p['x'], p['h'] + self.pipe_gap, self.pipe_width, self.height - p['h'] - self.pipe_gap))
            
        if self.render_callback:
            self.render_callback(self.display)
            return

        pygame.display.flip()
        self.clock.tick(30)

    def close(self):
        pass
