"""
=========================================================
GameBrain

PPO Critic Network

Estimates the value of a given state.

Author : Team GameBrain
=========================================================
"""

import torch
import torch.nn as nn


class Critic(nn.Module):
    """
    Critic Network

    Input:
        Game state

    Output:
        Estimated state value V(s)
    """

    def __init__(self, state_size):

        super().__init__()

        self.network = nn.Sequential(

            nn.Linear(state_size, 128),
            nn.ReLU(),

            nn.Linear(128, 128),
            nn.ReLU(),

            nn.Linear(128, 1)

        )

    def forward(self, state):

        return self.network(state)


if __name__ == "__main__":

    model = Critic(state_size=12)

    dummy_state = torch.randn(1, 12)

    value = model(dummy_state)

    print()
    print("=" * 50)
    print("Critic Output")
    print("=" * 50)
    print(value)
    print("Shape :", value.shape)