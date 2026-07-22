import sys
import os
sys.path.append(os.path.abspath('.'))
from environments.flappy_bird_env import FlappyBirdEnv
from rl.dqn.agent import DQNAgent
import torch
import numpy as np
from app.utils.settings_manager import SettingsManager

def predict_action(ai_agent, state):
    state_t = torch.FloatTensor(state).unsqueeze(0).to(ai_agent.device)
    ai_agent.model.eval()
    with torch.no_grad():
        q_values = ai_agent.model(state_t).squeeze().cpu().numpy()
        if q_values.ndim == 0:
            q_values = np.array([q_values])
    return int(np.argmax(q_values)), q_values

def main():
    username = SettingsManager().get("username", "Player1")
    game_id = "flappy_bird"
    
    ai_env = FlappyBirdEnv()
    ai_agent = DQNAgent(state_size=4, action_size=2)
    active_model = f"best_dqn_model_{game_id}.pth"
    ai_agent.load_model(active_model)
    
    state = ai_env.reset()
    for i in range(100):
        action, q_vals = predict_action(ai_agent, state)
        next_state, reward, done, score = ai_env.step(action)
        print(f"Step {i}: state={state}, action={action}, q_vals={q_vals}, done={done}")
        state = next_state
        if done:
            break

if __name__ == "__main__":
    main()
