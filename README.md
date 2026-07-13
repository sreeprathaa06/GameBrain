# 🧠 GameBrain

GameBrain is an interactive framework for training and visualizing Reinforcement Learning (RL) agents. Build, train, and test intelligent models on a variety of environments directly from an intuitive Graphical User Interface.

## 🚀 Features

- **Intuitive UI:** A clean, dark-mode desktop interface built with `customtkinter`.
- **Live AI Training:** Train Deep Q-Network (DQN) models with real-time feedback.
- **Visual Analytics:** View real-time matplotlib graphs tracking Rewards, Losses, Epsilon (Exploration Rate), and Training Speeds.
- **Multiple Environments:** Comes with built-in environments like Snake and Flappy Bird. 
- **Leaderboard & Dashboard:** Keep track of your highest AI scores, longest survival times, and compare them against human play. Earn achievements.
- **Human vs AI:** Challenge the trained AI models yourself directly through the UI.
- **Data Export:** Export training metrics to CSV or plot graphs as PNG/PDF.

## 🛠️ Technology Stack

- **Python 3**
- **PyTorch:** Backend for Reinforcement Learning models (DQN, PPO).
- **CustomTkinter:** For modern desktop UI components.
- **Matplotlib & Pandas:** Data tracking and live visualizations.
- **Pygame:** Used for rendering select complex game environments.

## 📦 Getting Started

### Prerequisites

Ensure you have Python installed, then install the necessary dependencies:

```bash
pip install -r requirements.txt
```

*(Optional)* If you plan on training heavily, ensure you have a CUDA-compatible GPU and the appropriate PyTorch build installed.

### Running the App

To launch the GameBrain interface, run:

```bash
python game_launcher.py
```
*(Or the main entry point defined for your setup, typically `main.py` or `game_launcher.py`)*

## 🎮 How to Use

1. **Setup User:** Create a local profile to store your AI models and leaderboards.
2. **Train:** Navigate to the **AI Training** center, adjust the training speed, and watch the agent learn from scratch!
3. **Play:** Go to the **Play** section to either play manually or pit yourself against your newly trained model.
4. **Analyze:** Check the **Dashboard** and **Leaderboard** to review historical metrics and performance.

## 📝 License
This project is for educational purposes.