import pygame
import numpy as np
import random

try:
    import chess
    CHESS_AVAILABLE = True
except ImportError:
    CHESS_AVAILABLE = False

class ChessEnv:
    def __init__(self, render=False, render_callback=None):
        self.render_game = render
        self.render_callback = render_callback
        
        self.width = 400
        self.height = 400
        self.square_size = 50

        if render:
            if not pygame.get_init():
                pygame.init()
            if render_callback is None:
                self.display = pygame.display.set_mode((self.width, self.height))
                pygame.display.set_caption("Chess Environment")
                self.clock = pygame.time.Clock()
            else:
                self.display = pygame.Surface((self.width, self.height))

        if CHESS_AVAILABLE:
            self.board = chess.Board()
            # actions mapped to all possible 64*64 source/dest combinations (simplified)
            self.action_size = 4096 
        else:
            self.board = None

        self.reset()

    def reset(self):
        if CHESS_AVAILABLE:
            self.board.reset()
        
        self.score = 0
        self.frame_iteration = 0
        self.mock_x = 0
        self.mock_y = 0
        return self.get_state()

    def get_state(self):
        if CHESS_AVAILABLE:
            # Flatten 64 squares into one-hot encoding for 12 pieces = 768 elements
            state = np.zeros(768, dtype=np.float32)
            for i in range(64):
                piece = self.board.piece_at(i)
                if piece:
                    # piece type 1-6, color True/False
                    idx = i * 12 + (piece.piece_type - 1) + (0 if piece.color else 6)
                    state[idx] = 1.0
            return state
        else:
            # Return dummy state for placeholder
            return np.array([self.mock_x / 8.0, self.mock_y / 8.0], dtype=np.float32)

    def step(self, action):
        self.frame_iteration += 1
        reward = 0
        done = False
        
        if CHESS_AVAILABLE:
            # action mapped to move (src, dest)
            src = action // 64
            dest = action % 64
            move = chess.Move(src, dest)
            
            if move in self.board.legal_moves:
                self.board.push(move)
                reward = 0
                # Opponent random move
                if not self.board.is_game_over():
                    opp_move = random.choice(list(self.board.legal_moves))
                    self.board.push(opp_move)
                else:
                    done = True
                    if self.board.is_checkmate():
                        reward = 100
            else:
                # invalid move penalty
                reward = -10
                done = True
                
            if self.board.is_game_over():
                done = True
                
            self.score = reward
        else:
            # Mock behavior
            if action == 1: self.mock_x = min(7, self.mock_x + 1)
            elif action == 2: self.mock_y = min(7, self.mock_y + 1)
            reward = 1 if action in [1, 2] else 0
            self.score += reward
            if self.frame_iteration > 50:
                done = True
                
        if self.render_game:
            self.render()

        return self.get_state(), reward, done, self.score

    def render(self):
        self.display.fill((255, 206, 158))
        for r in range(8):
            for c in range(8):
                if (r + c) % 2 == 0:
                    pygame.draw.rect(self.display, (209, 139, 71), (c*self.square_size, r*self.square_size, self.square_size, self.square_size))
        
        if not CHESS_AVAILABLE:
            # Draw mock piece
            pygame.draw.circle(self.display, (0, 0, 0), (self.mock_x * self.square_size + 25, self.mock_y * self.square_size + 25), 20)
            
        if self.render_callback:
            self.render_callback(self.display)
            return

        pygame.display.flip()
        self.clock.tick(10)
