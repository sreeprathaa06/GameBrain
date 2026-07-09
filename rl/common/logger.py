"""
=========================================================
GameBrain Logger

Stores training information into a CSV file.

Author : Team GameBrain
=========================================================
"""

import csv
import os


class TrainingLogger:

    def __init__(self, game_id="snake"):

        # Project Root
        self.project_root = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                ".."
            )
        )

        from app.utils.settings_manager import SettingsManager
        username = SettingsManager().get("username", "Player1")

        # Logs Folder
        self.logs_folder = os.path.join(
            self.project_root,
            "training_logs",
            username
        )

        os.makedirs(
            self.logs_folder,
            exist_ok=True
        )

        self.log_file = os.path.join(
            self.logs_folder,
            f"training_log_{game_id}.csv"
        )

        if not os.path.exists(self.log_file):

            with open(self.log_file, "w", newline="") as file:

                writer = csv.writer(file)

                writer.writerow([
                    "Episode",
                    "Reward",
                    "Loss",
                    "Epsilon"
                ])

    def log(self, episode, reward, loss, epsilon):

        with open(self.log_file, "a", newline="") as file:

            writer = csv.writer(file)

            writer.writerow([
                episode,
                reward,
                loss,
                epsilon
            ])

    def get_log_file(self):

        return self.log_file


if __name__ == "__main__":

    logger = TrainingLogger()

    logger.log(
        episode=1,
        reward=25,
        loss=0.54,
        epsilon=0.95
    )

    print("Logger Working Successfully!")
    print(logger.get_log_file())