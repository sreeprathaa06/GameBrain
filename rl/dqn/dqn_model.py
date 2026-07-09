import torch
import torch.nn as nn


class DQN(nn.Module):
    """
    Deep Q Network

    This neural network receives the game state
    and predicts the Q-value for every possible action.
    """

    def __init__(self, input_size, output_size):
        super().__init__()

        self.network = nn.Sequential(

            nn.Linear(input_size, 128),
            nn.ReLU(),

            nn.Linear(128, 128),
            nn.ReLU(),

            nn.Linear(128, output_size)

        )

    def forward(self, x):
        return self.network(x)












if __name__ == "__main__":

    model = DQN(input_size=12, output_size=4)

    print(model)