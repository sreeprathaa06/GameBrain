import sys
import os

# Append project root
sys.path.append(r"c:\Users\User\Desktop\GameBrain2")

from app.utils.settings_manager import SettingsManager
from app.utils.leaderboard_manager import LeaderboardManager

# Simulate what home.py does
settings = SettingsManager()
settings.set("username", "TestUserFresh")

print("Username is now:", settings.get("username"))

progress = LeaderboardManager.get_training_progress("snake")
print("Progress for snake:", progress)

progress_flappy = LeaderboardManager.get_training_progress("flappy_bird")
print("Progress for flappy_bird:", progress_flappy)
