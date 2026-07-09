import os
import json
from datetime import datetime

class LeaderboardManager:
    _instances = {}

    DEFAULT_DATA = {
        "highest_human_score": 0,
        "highest_ai_score": 0,
        "longest_survival_steps": 0,
        "most_apples_single_game": 0,
        "best_training_reward": 0.0,
        "fastest_training_time_sec": 0.0,
        "recent_sessions": [],
        "achievements": {
            "first_steps": {"unlocked": False, "title": "First Steps", "desc": "Train for at least 10 episodes"},
            "deep_learner": {"unlocked": False, "title": "Deep Learner", "desc": "Train for at least 500 episodes"},
            "apple_gobbler": {"unlocked": False, "title": "High Scorer", "desc": "Get a high score in Human Mode"},
            "ai_overlord": {"unlocked": False, "title": "AI Overlord", "desc": "AI reaches high score"},
            "beat_the_machine": {"unlocked": False, "title": "Beat the Machine", "desc": "Win against the AI in Human vs AI mode"}
        }
    }

    def __new__(cls, game_id="snake"):
        if game_id not in cls._instances:
            instance = super(LeaderboardManager, cls).__new__(cls)
            instance.game_id = game_id
            instance.leaderboard_file = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "..",
                    "logs",
                    f"leaderboard_{game_id}.json"
                )
            )
            instance.load()
            cls._instances[game_id] = instance
        return cls._instances[game_id]

    def load(self):
        os.makedirs(os.path.dirname(self.leaderboard_file), exist_ok=True)
        if not os.path.exists(self.leaderboard_file):
            self.data = self.DEFAULT_DATA.copy()
            self.save()
        else:
            try:
                with open(self.leaderboard_file, "r") as f:
                    self.data = json.load(f)
                if "achievements" not in self.data:
                    self.data["achievements"] = self.DEFAULT_DATA["achievements"].copy()
            except Exception as e:
                print(f"Error loading leaderboard for {self.game_id}: {e}")
                self.data = self.DEFAULT_DATA.copy()

    def save(self):
        try:
            with open(self.leaderboard_file, "w") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Error saving leaderboard: {e}")

    def update_score(self, mode, score, survival_steps=0, is_winner=False):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        session = {
            "mode": mode,
            "score": score,
            "survival_steps": survival_steps,
            "date": timestamp
        }
        self.data["recent_sessions"].insert(0, session)
        self.data["recent_sessions"] = self.data["recent_sessions"][:30]

        if mode == "Human":
            if score > self.data["highest_human_score"]:
                self.data["highest_human_score"] = score
            if score >= 10:
                self.unlock_achievement("apple_gobbler")
        elif mode == "AI":
            if score > self.data["highest_ai_score"]:
                self.data["highest_ai_score"] = score
            if score >= 30:
                self.unlock_achievement("ai_overlord")
        elif mode == "Human vs AI":
            if is_winner:
                self.unlock_achievement("beat_the_machine")

        if survival_steps > self.data["longest_survival_steps"]:
            self.data["longest_survival_steps"] = survival_steps

        if score > self.data["most_apples_single_game"]:
            self.data["most_apples_single_game"] = score

        self.save()

    def update_training_records(self, best_reward, time_taken_sec=None):
        if best_reward > self.data["best_training_reward"]:
            self.data["best_training_reward"] = round(best_reward, 2)
        if time_taken_sec is not None:
            if self.data["fastest_training_time_sec"] == 0 or time_taken_sec < self.data["fastest_training_time_sec"]:
                self.data["fastest_training_time_sec"] = round(time_taken_sec, 2)
        self.save()

    def check_training_achievements(self, episodes):
        if episodes >= 10:
            self.unlock_achievement("first_steps")
        if episodes >= 500:
            self.unlock_achievement("deep_learner")

    def unlock_achievement(self, ach_id):
        if ach_id in self.data["achievements"] and not self.data["achievements"][ach_id]["unlocked"]:
            self.data["achievements"][ach_id]["unlocked"] = True
            self.save()
            print(f"🏆 ACHIEVEMENT UNLOCKED: {self.data['achievements'][ach_id]['title']}")

    def get_data(self):
        return self.data

    @classmethod
    def get_training_progress(cls, game_id, target=1000):
        log_file = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "..", "training_logs", f"training_log_{game_id}.csv"
        ))
        if not os.path.exists(log_file):
            return 0.0
            
        try:
            with open(log_file, "r") as f:
                lines = sum(1 for _ in f) - 1 # exclude header
            if lines < 0: lines = 0
            
            percentage = (lines / target) * 100
            return min(100.0, round(percentage, 1))
        except:
            return 0.0
