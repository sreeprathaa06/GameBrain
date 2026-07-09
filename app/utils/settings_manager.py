import os
import json

class SettingsManager:
    _instance = None
    SETTINGS_FILE = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "configs",
            "app_settings.json"
        )
    )

    DEFAULT_SETTINGS = {
        "theme": "dark",
        "accent_color": "blue",
        "training_speed": 30, # default delay in ms
        "fps": 10,
        "graph_refresh_rate": 1,
        "game_speed": "Normal",
        "model_dir": "saved_models",
        "gpu_toggle": True,
        "active_model": "best_dqn_model.pth",
        "active_game": "snake",
        "username": "",
        "age": "",
        "experience": "Beginner"
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance.load()
        return cls._instance

    def load(self):
        os.makedirs(os.path.dirname(self.SETTINGS_FILE), exist_ok=True)
        if not os.path.exists(self.SETTINGS_FILE):
            self.settings = self.DEFAULT_SETTINGS.copy()
            self.save()
        else:
            try:
                with open(self.SETTINGS_FILE, "r") as f:
                    self.settings = json.load(f)
                # Ensure all default keys exist
                for k, v in self.DEFAULT_SETTINGS.items():
                    if k not in self.settings:
                        self.settings[k] = v
            except Exception as e:
                print(f"Error loading settings: {e}")
                self.settings = self.DEFAULT_SETTINGS.copy()

    def save(self):
        try:
            with open(self.SETTINGS_FILE, "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key, default=None):
        return self.settings.get(key, default if default is not None else self.DEFAULT_SETTINGS.get(key))

    def set(self, key, value):
        self.settings[key] = value
        self.save()
