"""
loss.py

Implements the DQN loss function.
"""

import torch
import torch.nn.functional as F


class DQNLoss:

    def __init__(self, gamma=0.99):

        self.gamma = gamma

    def compute_loss(

        self,

        model,

        target_model,

        states,

        actions,

        rewards,

        next_states,

        dones

    ):

        current_q = model(states)

        current_q = current_q.gather(
            1,
            actions.unsqueeze(1)
        ).squeeze(1)

        with torch.no_grad():

            next_q = target_model(next_states)

            max_next_q = next_q.max(1)[0]

            target_q = rewards + (
                self.gamma
                * max_next_q
                * (1 - dones)
            )

        loss = F.mse_loss(
            current_q,
            target_q
        )

        return loss




if __name__ == "__main__":

    from dqn_model import DQN

    model = DQN(12,4)

    target = DQN(12,4)

    criterion = DQNLoss()

    states = torch.rand(8,12)

    actions = torch.randint(0,4,(8,))

    rewards = torch.rand(8)

    next_states = torch.rand(8,12)

    dones = torch.zeros(8)

    loss = criterion.compute_loss(

        model,

        target,

        states,

        actions,

        rewards,

        next_states,

        dones

    )

    print("Loss :", loss.item())