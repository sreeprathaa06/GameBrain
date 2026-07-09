"""
epsilon_greedy.py

Implements the epsilon-greedy strategy used by DQN.

The agent explores at the beginning of training and
gradually exploits its learned knowledge.
"""

import random
import torch


class EpsilonGreedy:

    def __init__(
        self,
        start_epsilon=1.0,
        end_epsilon=0.01,
        decay=0.995
    ):

        self.epsilon = start_epsilon

        self.min_epsilon = end_epsilon

        self.decay = decay

    def choose_action(
        self,
        model,
        state,
        action_size,
        device
    ):

        # Exploration
        if random.random() < self.epsilon:

            return random.randint(
                0,
                action_size - 1
            )

        # Exploitation
        with torch.no_grad():

            state = torch.FloatTensor(state).unsqueeze(0).to(device)

            q_values = model(state)

            return torch.argmax(q_values).item()

    def decay_epsilon(self):

        if self.epsilon > self.min_epsilon:

            self.epsilon *= self.decay

            if self.epsilon < self.min_epsilon:

                self.epsilon = self.min_epsilon

    def get_epsilon(self):

        return self.epsilon




if __name__ == "__main__":

    from dqn_model import DQN

    device = torch.device("cpu")

    model = DQN(12, 4)

    strategy = EpsilonGreedy()

    dummy_state = [0] * 12

    print("Initial Epsilon:", strategy.get_epsilon())

    for i in range(5):

        action = strategy.choose_action(
            model=model,
            state=dummy_state,
            action_size=4,
            device=device
        )

        print("Chosen Action:", action)

        strategy.decay_epsilon()

        print("Updated Epsilon:", strategy.get_epsilon())