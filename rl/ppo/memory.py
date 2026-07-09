"""
=========================================================
GameBrain

PPO Memory

Stores rollout trajectories for PPO training.

Author : Team GameBrain
=========================================================
"""

import torch
import random


class PPOMemory:

    def __init__(self):

        self.clear()

    def store(
        self,
        state,
        action,
        reward,
        next_state,
        done,
        log_prob,
        value
    ):

        self.states.append(state)

        self.actions.append(action)

        self.rewards.append(reward)

        self.next_states.append(next_state)

        self.dones.append(done)

        self.log_probs.append(log_prob)

        self.values.append(value)

    def size(self):

        return len(self.states)

    def clear(self):

        self.states = []

        self.actions = []

        self.rewards = []

        self.next_states = []

        self.dones = []

        self.log_probs = []

        self.values = []

    def get_tensors(self, device):

        states = torch.FloatTensor(
            self.states
        ).to(device)

        actions = torch.LongTensor(
            self.actions
        ).to(device)

        rewards = torch.FloatTensor(
            self.rewards
        ).to(device)

        next_states = torch.FloatTensor(
            self.next_states
        ).to(device)

        dones = torch.FloatTensor(
            self.dones
        ).to(device)

        log_probs = torch.FloatTensor(
            self.log_probs
        ).to(device)

        values = torch.FloatTensor(
            self.values
        ).to(device)

        return (

            states,
            actions,
            rewards,
            next_states,
            dones,
            log_probs,
            values

        )

    def get_batches(

        self,

        batch_size

    ):

        indices = list(

            range(

                self.size()

            )

        )

        random.shuffle(

            indices

        )

        for start in range(

            0,

            self.size(),

            batch_size

        ):

            yield indices[

                start:

                start + batch_size

            ]


if __name__ == "__main__":

    device = torch.device("cpu")

    memory = PPOMemory()

    for i in range(10):

        memory.store(

            state=[0.0] * 12,

            action=i % 4,

            reward=1.0,

            next_state=[1.0] * 12,

            done=False,

            log_prob=-0.5,

            value=0.8

        )

    print()

    print("=" * 60)

    print("Stored :", memory.size())

    tensors = memory.get_tensors(device)

    print()

    print("State Shape :", tensors[0].shape)

    print("Action Shape :", tensors[1].shape)

    print("Reward Shape :", tensors[2].shape)

    print()

    print("Mini Batches")

    for batch in memory.get_batches(4):

        print(batch)

    print("=" * 60)