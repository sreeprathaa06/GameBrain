"""
=========================================================
GameBrain

Main Application

Author : Team GameBrain
=========================================================
"""

import os
import sys
import customtkinter as ctk

# -------------------------------------------------------
# Project Root
# -------------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# -------------------------------------------------------
# Theme
# -------------------------------------------------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# -------------------------------------------------------
# Import Pages
# -------------------------------------------------------

from widgets.sidebar import Sidebar
from utils.settings_manager import SettingsManager

from pages.home import HomePage
from pages.play import PlayPage
from pages.academy import AcademyPage
from pages.dashboard import DashboardPage
from pages.leaderboard import LeaderboardPage
from pages.settings import SettingsPage
from pages.ai_training import AITrainingPage
from pages.game_launcher import GameLauncher


class GameBrain(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("🎮 GameBrain")

        self.geometry("1450x850")

        self.minsize(1250, 750)
        self.after(0, lambda: self.state('zoomed'))

        self.configure(fg_color=("gray95", "#141414"))

        # ===========================================
        # Sidebar
        # ===========================================

        self.sidebar = Sidebar(
            self,
            self.show_page
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        # ===========================================
        # Main Container
        # ===========================================

        self.main_container = ctk.CTkFrame(
            self,
            fg_color=("gray90", "#1B1B1B"),
            corner_radius=0
        )

        self.main_container.pack(
            side="right",
            fill="both",
            expand=True
        )

        # ===========================================
        # Header
        # ===========================================

        self.header = ctk.CTkFrame(
            self.main_container,
            height=70,
            fg_color=("gray85", "#202020"),
            corner_radius=0
        )

        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        self.title_label = ctk.CTkLabel(
            self.header,
            text="GameBrain",
            font=("Arial", 28, "bold")
        )

        self.title_label.pack(
            side="left",
            padx=25,
            pady=15
        )

        self.status_label = ctk.CTkLabel(
            self.header,
            text="Ready",
            text_color="lightgreen",
            font=("Arial", 16)
        )

        self.status_label.pack(
            side="right",
            padx=25
        )

        # ===========================================
        # Page Container
        # ===========================================

        self.page_container = ctk.CTkFrame(
            self.main_container,
            fg_color=("gray90", "#1B1B1B")
        )

        self.page_container.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        # ===========================================
        # Pages
        # ===========================================

        self.pages = {

            "home": HomePage(self.page_container),

            "play": PlayPage(self.page_container),

            "academy": AcademyPage(self.page_container),

            "dashboard": DashboardPage(self.page_container),

            "leaderboard": LeaderboardPage(self.page_container),

            "settings": SettingsPage(self.page_container),

            "ai_training": AITrainingPage(self.page_container)

        }

        self.current_page = None

        # Connect launcher to application
        GameLauncher.set_app(self)

        self.show_page("home")

    # ===================================================
    # Show Page
    # ===================================================

    def show_page(self, page):

        if self.current_page:

            self.current_page.pack_forget()

        self.current_page = self.pages[page]

        self.current_page.pack(
            fill="both",
            expand=True
        )

        # Refresh Dashboard automatically
        if page == "dashboard":

            if hasattr(self.current_page, "refresh_dashboard"):

                self.current_page.refresh_dashboard()

        titles = {

            "home": "🏠 Home",

            "play": "🎮 Play Games",

            "academy": "🧠 AI Academy",

            "dashboard": "📊 Dashboard",

            "leaderboard": "🏆 Leaderboard",

            "settings": "⚙ Settings",

            "ai_training": "🧠 AI Training Dashboard"

        }

        self.title_label.configure(
            text=titles.get(page, "GameBrain")
        )

        self.status_label.configure(
            text="Ready",
            text_color="lightgreen"
        )


# =======================================================
# Main
# =======================================================

if __name__ == "__main__":

    app = GameBrain()

    app.mainloop()