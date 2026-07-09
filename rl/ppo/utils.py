"""
=========================================================
GameBrain

PPO Utilities

Contains helper functions for PPO training.

Author : Team GameBrain
=========================================================
"""

import torch


def compute_gae(
    rewards,
    values,
    dones,
    gamma=0.99,
    lam=0.95
):
    """
    Compute Generalized Advantage Estimation (GAE).

    Returns:
        returns
        advantages
    """

    returns = []

    advantages = []

    gae = 0

    next_value = 0

    values = values.tolist()

    rewards = rewards.tolist()

    dones = dones.tolist()

    for step in reversed(range(len(rewards))):

        mask = 1.0 - dones[step]

        delta = (

            rewards[step]

            + gamma * next_value * mask

            - values[step]

        )

        gae = (

            delta

            + gamma * lam * mask * gae

        )

        advantages.insert(

            0,

            gae

        )

        next_value = values[step]

        returns.insert(

            0,

            gae + values[step]

        )

    returns = torch.tensor(

        returns,

        dtype=torch.float32

    )

    advantages = torch.tensor(

        advantages,

        dtype=torch.float32

    )

    advantages = (

        advantages

        - advantages.mean()

    ) / (

        advantages.std()

        + 1e-8

    )

    return returns, advantages


if __name__ == "__main__":

    rewards = torch.tensor(

        [1.0, 1.0, 10.0]

    )

    values = torch.tensor(

        [0.8, 1.1, 2.0]

    )

    dones = torch.tensor(

        [0.0, 0.0, 1.0]

    )

    returns, advantages = compute_gae(

        rewards,

        values,

        dones

    )

    print()

    print("=" * 60)

    print("Returns")

    print(returns)

    print()

    print("Advantages")

    print(advantages)

    print("=" * 60)