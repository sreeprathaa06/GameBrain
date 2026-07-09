"""
=====================================================
GameBrain
DQN Training
=====================================================
"""

import pygame
import os
import sys

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            ".."
        )
    )
)

from environments.snake_env import SnakeEnv
from rl.common.logger import TrainingLogger
from .agent import DQNAgent


# =====================================================
# SETTINGS
# =====================================================

EPISODES = 500
TARGET_UPDATE = 5

# 0 = Fastest
# 30 = Fast
# 60 = Normal
# 100 = Slow
TRAIN_SPEED = 60


# =====================================================
# TRAIN
# =====================================================

def train(
    env_class=SnakeEnv,
    state_size=12,
    action_size=4,
    game_id="snake",
    callback=None,
    render_callback=None,
    pause_event=None,
    stop_event=None,
    get_delay=None,
    lr=0.001,
    gamma=0.99,
    batch_size=64,
    episodes=500
):
    import time

    env = env_class(render=(render_callback is None), render_callback=render_callback)

    agent = DQNAgent(
        state_size=state_size,
        action_size=action_size,
        learning_rate=lr,
        gamma=gamma,
        batch_size=batch_size
    )

    logger = TrainingLogger(game_id=game_id)

    print("\n" + "=" * 60)
    print("🧠 GameBrain DQN Training Started")
    print("=" * 60 + "\n")

    best_reward = float("-inf")
    start_time = time.time()

    for episode in range(episodes):

        # Check stop
        if stop_event and stop_event.is_set():
            break

        state = env.reset()

        done = False

        total_reward = 0

        loss = 0

        while not done:
            # Check stop inside game loop
            if stop_event and stop_event.is_set():
                break

            # Check pause
            while pause_event and pause_event.is_set():
                if stop_event and stop_event.is_set():
                    break
                time.sleep(0.1)

            action = agent.select_action(state)

            next_state, reward, done, info = env.step(action)

            # Apply training delay
            delay = get_delay() if get_delay is not None else TRAIN_SPEED
            if delay > 0:
                time.sleep(delay / 1000.0)

            agent.remember(
                state,
                action,
                reward,
                next_state,
                done
            )

            train_loss = agent.train_step()

            if train_loss is not None:
                loss = train_loss

            state = next_state

            total_reward += reward

        if stop_event and stop_event.is_set():
            break

        # -------------------------------
        # Update Target Network
        # -------------------------------

        if (episode + 1) % TARGET_UPDATE == 0:
            agent.update_target_network()

        # -------------------------------
        # Logger
        # -------------------------------

        logger.log(
            episode=episode + 1,
            reward=total_reward,
            loss=loss,
            epsilon=agent.current_epsilon()
        )

        # -------------------------------
        # Save Best Model
        # -------------------------------

        metadata = {
            "best_reward": max(best_reward, total_reward),
            "episode": episode + 1,
            "learning_rate": lr
        }

        if total_reward > best_reward:

            best_reward = total_reward

            agent.save_model(f"best_dqn_model_{game_id}.pth", metadata=metadata)

            print(
                f"🏆 New Best Reward : {best_reward:.2f}"
            )

        # -------------------------------
        # Progress
        # -------------------------------

        progress = (episode + 1) / episodes

        print(
            f"[{episode+1}/{episodes}] "
            f"Reward={total_reward:.2f} | "
            f"Best={best_reward:.2f} | "
            f"Loss={loss:.6f} | "
            f"Epsilon={agent.current_epsilon():.4f}"
        )

        # -------------------------------
        # Send Live Data To UI
        # -------------------------------

        if callback is not None:

            callback(
                episode=episode + 1,
                total_episodes=episodes,
                progress=progress,
                reward=total_reward,
                best_reward=best_reward,
                loss=loss,
                epsilon=agent.current_epsilon()
            )

    # =================================================
    # Save Final Model
    # =================================================

    end_time = time.time()
    duration = end_time - start_time

    metadata = {
        "best_reward": best_reward,
        "episode": episodes,
        "learning_rate": lr
    }
    agent.save_model(f"gamebrain_dqn_{game_id}.pth", metadata=metadata)

    # Save to Leaderboard records
    try:
        from app.utils.leaderboard_manager import LeaderboardManager
        LeaderboardManager(game_id).update_training_records(best_reward, duration)
        LeaderboardManager(game_id).check_training_achievements(episodes)
    except Exception as e:
        print("Error saving to leaderboard from train:", e)

    env.close()

    print("\n" + "=" * 60)
    print("✅ Training Finished Successfully")
    print("=" * 60)
    print(
        f"Training Log Saved : {logger.get_log_file()}"
    )

    return True


# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":

    train()