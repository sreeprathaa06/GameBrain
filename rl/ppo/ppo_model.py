"""
=========================================================
GameBrain

PPO Model

Combines Actor and Critic networks.

=========================================================
"""

import torch
import os

from actor import Actor
from critic import Critic


class PPOModel:

    def __init__(

        self,

        state_size,

        action_size,

        device=None

    ):

        if device is None:

            device = torch.device(

                "cuda"

                if torch.cuda.is_available()

                else "cpu"

            )

        self.device = device

        self.actor = Actor(

            state_size,

            action_size

        ).to(device)

        self.critic = Critic(

            state_size

        ).to(device)

    def act(

        self,

        state

    ):

        state = torch.FloatTensor(

            state

        ).unsqueeze(0).to(self.device)

        with torch.no_grad():

            probs = self.actor(state)

        distribution = torch.distributions.Categorical(

            probs

        )

        action = distribution.sample()

        log_prob = distribution.log_prob(action)

        return (

            action.item(),

            log_prob.item()

        )

    def evaluate(

        self,

        state

    ):

        state = torch.FloatTensor(

            state

        ).unsqueeze(0).to(self.device)

        with torch.no_grad():

            value = self.critic(state)

        return value.item()

    def save(

        self,

        folder="saved_models",

        actor_name="ppo_actor.pth",

        critic_name="ppo_critic.pth"

    ):

        os.makedirs(

            folder,

            exist_ok=True

        )

        torch.save(

            self.actor.state_dict(),

            os.path.join(

                folder,

                actor_name

            )

        )

        torch.save(

            self.critic.state_dict(),

            os.path.join(

                folder,

                critic_name

            )

        )

        print("Models Saved Successfully!")

    def load(

        self,

        folder="saved_models",

        actor_name="ppo_actor.pth",

        critic_name="ppo_critic.pth"

    ):

        self.actor.load_state_dict(

            torch.load(

                os.path.join(

                    folder,

                    actor_name

                ),

                map_location=self.device

            )

        )

        self.critic.load_state_dict(

            torch.load(

                os.path.join(

                    folder,

                    critic_name

                ),

                map_location=self.device

            )

        )

        print("Models Loaded Successfully!")


if __name__ == "__main__":

    model = PPOModel(

        state_size=12,

        action_size=4

    )

    dummy_state = [0] * 12

    action, log_prob = model.act(

        dummy_state

    )

    value = model.evaluate(

        dummy_state

    )

    print()

    print("=" * 60)

    print("Selected Action :", action)

    print("Log Probability :", log_prob)

    print("State Value :", value)

    print("=" * 60)

    model.save()

    model.load()