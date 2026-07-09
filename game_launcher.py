"""
=========================================================
GameBrain

Game Launcher

=========================================================
"""

import threading
from tkinter import messagebox

from play_modes.human_play import HumanPlay
from play_modes.ai_play import AIPlay


class GameLauncher:

    app = None

    @classmethod
    def set_app(cls, app):
        cls.app = app

    # ----------------------------------------

    @staticmethod
    def launch_snake_human():

        threading.Thread(
            target=HumanPlay().run,
            daemon=True
        ).start()

    # ----------------------------------------

    @staticmethod
    def launch_snake_ai():

        threading.Thread(
            target=AIPlay().run,
            daemon=True
        ).start()

    # ----------------------------------------

    @classmethod
    def launch_snake_training(cls):

        if cls.app:

            cls.app.show_page("ai_training")

    # ----------------------------------------

    @staticmethod
    def launch_human_vs_ai():

        messagebox.showinfo(

            "GameBrain",

            "🚧 Human vs AI Coming Soon"

        )