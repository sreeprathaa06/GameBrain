"""
=========================================================
GameBrain

Renderer

Handles:
1. Window
2. Drawing Snake
3. Drawing Food
4. Drawing Score
5. Game Over Screen

=========================================================
"""

import pygame


class Renderer:

    def __init__(self, grid_width=20, grid_height=20, cell_size=25):

        pygame.init()

        self.grid_width = grid_width
        self.grid_height = grid_height
        self.cell_size = cell_size

        self.width = grid_width * cell_size
        self.height = grid_height * cell_size

        self.screen = pygame.display.set_mode(
            (self.width, self.height)
        )

        pygame.display.set_caption("GameBrain Snake")

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("Arial", 24)
        self.big_font = pygame.font.SysFont("Arial", 42, bold=True)

    # =====================================================
    # Draw Game
    # =====================================================

    def draw(self, snake_body, food_position, score):

        self.screen.fill((30, 30, 30))

        # Snake
        for x, y in snake_body:

            pygame.draw.rect(

                self.screen,

                (0, 255, 0),

                (
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
            )

        # Food
        fx, fy = food_position

        pygame.draw.rect(

            self.screen,

            (255, 0, 0),

            (
                fx * self.cell_size,
                fy * self.cell_size,
                self.cell_size,
                self.cell_size
            )
        )

        score_text = self.font.render(
            f"Score : {score}",
            True,
            (255, 255, 255)
        )

        self.screen.blit(score_text, (10, 10))

        pygame.display.flip()

    # =====================================================
    # Game Over Screen
    # =====================================================

    def show_game_over(self, score):

        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))

        self.screen.blit(overlay, (0, 0))

        title = self.big_font.render(
            "GAME OVER",
            True,
            (255, 80, 80)
        )

        self.screen.blit(
            title,
            (self.width // 2 - title.get_width() // 2, 80)
        )

        score_text = self.font.render(
            f"Score : {score}",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            score_text,
            (self.width // 2 - score_text.get_width() // 2, 150)
        )

        restart_button = pygame.Rect(
            self.width // 2 - 110,
            240,
            220,
            50
        )

        exit_button = pygame.Rect(
            self.width // 2 - 110,
            320,
            220,
            50
        )

        pygame.draw.rect(
            self.screen,
            (0, 170, 255),
            restart_button,
            border_radius=10
        )

        pygame.draw.rect(
            self.screen,
            (220, 60, 60),
            exit_button,
            border_radius=10
        )

        restart_text = self.font.render(
            "Restart",
            True,
            (255, 255, 255)
        )

        exit_text = self.font.render(
            "Exit",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            restart_text,
            (
                restart_button.centerx - restart_text.get_width() // 2,
                restart_button.centery - restart_text.get_height() // 2
            )
        )

        self.screen.blit(
            exit_text,
            (
                exit_button.centerx - exit_text.get_width() // 2,
                exit_button.centery - exit_text.get_height() // 2
            )
        )

        pygame.display.flip()

        return restart_button, exit_button

    # =====================================================

    def close(self):

        pygame.quit()