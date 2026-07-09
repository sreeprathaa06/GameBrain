"""
=========================================================
GameBrain

PPO Actor Network

Maps game state -> action probabilities

=========================================================
"""

import torch
import torch.nn as nn


class Actor(nn.Module):

    def __init__(self, state_size, action_size):

        super().__init__()

        self.network = nn.Sequential(

            nn.Linear(state_size, 128),
            nn.ReLU(),

            nn.Linear(128, 128),
            nn.ReLU(),

            nn.Linear(128, action_size),
            nn.Softmax(dim=-1)

        )

    def forward(self, state):

        return self.network(state)


if __name__ == "__main__":

    model = Actor(
        state_size=12,
        action_size=4
    )

    dummy = torch.randn(1, 12)

    output = model(dummy)

    print("Action Probabilities:")

    print(output)

    print("Sum =", output.sum())