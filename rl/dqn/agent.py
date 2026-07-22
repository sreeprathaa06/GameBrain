"""
=========================================================
GameBrain RL Engine
DQN Agent
=========================================================
"""

import os
import random
import numpy as np

import torch
import torch.optim as optim

from .dqn_model import DQN
from .replay_buffer import ReplayBuffer
from .epsilon_greedy import EpsilonGreedy
from .loss import DQNLoss
from .target_network import TargetNetwork


class DQNAgent:

    def __init__(
        self,
        state_size,
        action_size,
        learning_rate=0.001,
        gamma=0.99,
        memory_size=100000,
        batch_size=64,
    ):

        print("=" * 60)
        print("Initializing DQN Agent")
        print("=" * 60)

        # Device
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        print("Device :", self.device)

        # Params
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = gamma
        self.batch_size = batch_size

        # Networks
        self.model = DQN(state_size, action_size).to(self.device)
        self.target_model = DQN(state_size, action_size).to(self.device)
        self.target_model.load_state_dict(self.model.state_dict())

        self.target_network = TargetNetwork(self.target_model)

        # Memory
        self.memory = ReplayBuffer(capacity=memory_size)

        # Exploration
        self.strategy = EpsilonGreedy()

        # Loss
        self.loss_function = DQNLoss(gamma=self.gamma)

        # Optimizer
        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=learning_rate
        )

        # Save folder based on user profile
        from app.utils.settings_manager import SettingsManager
        username = SettingsManager().get("username", "Player1")
        self.model_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "saved_models", username))
        os.makedirs(self.model_folder, exist_ok=True)

        print("Agent Ready")
        print("=" * 60)

    # =====================================================
    # Action (Training)
    # =====================================================

    def select_action(self, state):

        return self.strategy.choose_action(
            model=self.model,
            state=state,
            action_size=self.action_size,
            device=self.device
        )

    # =====================================================
    # Prediction (Evaluation)
    # =====================================================

    def predict(self, state):

        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)

        self.model.eval()

        with torch.no_grad():
            q_values = self.model(state)

        self.model.train()

        return torch.argmax(q_values).item()

    # =====================================================
    # Store Memory
    # =====================================================

    def remember(self, state, action, reward, next_state, done):

        self.memory.push(state, action, reward, next_state, done)

    # =====================================================
    # Train Check
    # =====================================================

    def can_train(self):

        return len(self.memory) >= self.batch_size

    # =====================================================
    # Sample Batch
    # =====================================================

    def sample_memory(self):

        batch = self.memory.sample(self.batch_size)

        states, actions, rewards, next_states, dones = zip(*batch)

        return (
            torch.FloatTensor(np.array(states)).to(self.device),
            torch.LongTensor(actions).to(self.device),
            torch.FloatTensor(rewards).to(self.device),
            torch.FloatTensor(np.array(next_states)).to(self.device),
            torch.FloatTensor(dones).to(self.device),
        )

    # =====================================================
    # Train Step
    # =====================================================

    def train_step(self):

        if not self.can_train():
            return None

        states, actions, rewards, next_states, dones = self.sample_memory()

        loss = self.loss_function.compute_loss(
            self.model,
            self.target_model,
            states,
            actions,
            rewards,
            next_states,
            dones
        )

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return loss.item()

    # =====================================================
    # Target Update
    # =====================================================

    def update_target_network(self):

        self.target_model.load_state_dict(self.model.state_dict())

    # =====================================================
    # Save / Load
    # =====================================================

    def save_model(self, filename="dqn_model.pth", metadata=None):

        path = os.path.join(self.model_folder, filename)
        torch.save(self.model.state_dict(), path)

        print("Model saved:", path)
        
        # Save JSON metadata alongside .pth file
        try:
            meta_path = os.path.splitext(path)[0] + ".json"
            from datetime import datetime
            import json
            
            meta_data = {
                "filename": filename,
                "training_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "best_reward": round(metadata.get("best_reward", 0.0), 2) if metadata else 0.0,
                "episode": metadata.get("episode", 0) if metadata else 0,
                "model_size_kb": round(os.path.getsize(path) / 1024, 2),
                "state_size": self.state_size,
                "action_size": self.action_size,
                "learning_rate": metadata.get("learning_rate", 0.001) if metadata else 0.001,
                "gamma": self.gamma,
                "batch_size": self.batch_size
            }
            with open(meta_path, "w") as f:
                json.dump(meta_data, f, indent=4)
            print("Metadata saved:", meta_path)
        except Exception as e:
            print("Error saving metadata:", e)

    def load_model(self, filename="dqn_model.pth"):

        path = os.path.join(self.model_folder, filename)

        if not os.path.exists(path):
            print("Model not found!")
            return

        self.model.load_state_dict(torch.load(path, map_location=self.device))
        self.target_model.load_state_dict(self.model.state_dict())

        print("Model loaded:", path)

    # =====================================================
    # Info
    # =====================================================

    def current_epsilon(self):

        return self.strategy.get_epsilon()

    def memory_size(self):

        return len(self.memory)