"""
target_network.py
-----------------

Maintains the Target Network used in DQN.

The Target Network is a copy of the main network.

It is updated periodically to stabilize learning.
"""

import torch


class TargetNetwork:

    def __init__(self, model):

        self.target_model = model

    def update(self, main_model):

        self.target_model.load_state_dict(
            main_model.state_dict()
        )

        print("Target Network Updated Successfully!")

    def predict(self, state):

        with torch.no_grad():

            return self.target_model(state)




if __name__ == "__main__":

    import torch

    from dqn_model import DQN

    model = DQN(12, 4)

    target = TargetNetwork(model)

    target.update(model)

    sample = torch.rand(1, 12)

    output = target.predict(sample)

    print(output)