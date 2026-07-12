"""
=========================================================
GameBrain

Dashboard
=========================================================
"""

import os
import pandas as pd
import customtkinter as ctk
from app.utils.icon_loader import get_icon
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from app.utils.settings_manager import SettingsManager
from app.pages.play import GAME_REGISTRY

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, game_id, back_callback):
        super().__init__(parent, fg_color="transparent")
        
        self.game_id = game_id
        self.back_callback = back_callback
        
        self.best_reward = 0
        self.total_episodes = 0
        self.average_reward = 0
        self.last_loss = 0
        self.df = None
        self.canvas_widget = None
        
        self.load_training_data()
        self.create_ui()

    def load_training_data(self):
        username = SettingsManager().get("username", "Player1")
        log_file = os.path.join("training_logs", username, f"training_log_{self.game_id}.csv")

        self.best_reward = 0
        self.total_episodes = 0
        self.average_reward = 0
        self.last_loss = 0
        self.df = None

        if not os.path.exists(log_file):
            return

        try:
            df = pd.read_csv(log_file)
            if len(df) == 0:
                return

            self.df = df
            self.total_episodes = len(df)
            self.best_reward = round(df["Reward"].max(), 2)
            self.average_reward = round(df["Reward"].mean(), 2)
            self.last_loss = round(df["Loss"].iloc[-1], 5)
        except Exception as e:
            print(e)

    def refresh_dashboard(self):
        self.load_training_data()

        self.episode_value.configure(text=str(self.total_episodes))
        self.best_reward_value.configure(text=str(self.best_reward))
        self.average_reward_value.configure(text=str(self.average_reward))
        self.loss_value.configure(text=str(self.last_loss))

        username = SettingsManager().get("username", "Player1")
        model = os.path.join("saved_models", username, f"best_dqn_model_{self.game_id}.pth")

        if os.path.exists(model):
            self.status_label.configure(text="✅ Trained Model Available", text_color=("#006400", "lightgreen"))
        else:
            close_icon = get_icon("close", size=(16, 16))
            self.status_label.configure(text=" No Trained Model", image=close_icon, text_color=("#8B0000", "red"))
            
        self.update_graphs()

    def update_graphs(self):
        if self.canvas_widget:
            self.canvas_widget.destroy()
            self.canvas_widget = None

        if self.df is None or len(self.df) == 0:
            lbl = ctk.CTkLabel(self.graph_container, text="No training data available to display graphs.", text_color=("gray30", "gray70"))
            lbl.pack(expand=True)
            self.canvas_widget = lbl
            return

        fig = Figure(figsize=(10, 4), dpi=100, facecolor='none')
        
        ax1 = fig.add_subplot(121)
        ax1.plot(self.df["Episode"], self.df["Reward"], color="#10B981", linewidth=2)
        
        ax1.set_title("Reward Progression", color="white", pad=15)
        ax1.set_xlabel("Episode", color="gray")
        ax1.set_ylabel("Reward", color="gray")
        ax1.tick_params(colors="gray")
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)

        ax2 = fig.add_subplot(122)
        ax2.plot(self.df["Episode"], self.df["Loss"], color="#EF4444", linewidth=2)
        ax2.set_title("Loss Minimization", color="white", pad=15)
        ax2.set_xlabel("Episode", color="gray")
        ax2.set_ylabel("Loss", color="gray")
        ax2.tick_params(colors="gray")
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_container)
        canvas.draw()
        
        self.canvas_widget = canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

    def create_card(self, parent, title, value):
        frame = ctk.CTkFrame(
            parent,
            width=220,
            height=120,
            fg_color=("gray90", "#202020"),
            corner_radius=10,
            border_width=1,
            border_color=("gray85", "#303030")
        )
        frame.pack_propagate(False)

        ctk.CTkLabel(
            frame,
            text=title,
            font=("Arial", 16, "bold"),
            text_color=("gray40", "gray70")
        ).pack(pady=(20, 5))

        value_label = ctk.CTkLabel(
            frame,
            text=str(value),
            font=("Arial", 28, "bold"),
            text_color=("#005B96", "cyan")
        )
        value_label.pack()

        if title == "Episodes":
            self.episode_value = value_label
        elif title == "Best Reward":
            self.best_reward_value = value_label
        elif title == "Average Reward":
            self.average_reward_value = value_label
        elif title == "Latest Loss":
            self.loss_value = value_label

        return frame

    def create_ui(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=25)
        
        back_btn = ctk.CTkButton(
            header_frame, 
            text="⬅ Back to Menu", 
            width=140, 
            fg_color="#303030", 
            hover_color="#404040",
            command=self.back_callback
        )
        back_btn.pack(side="left")

        game_info = GAME_REGISTRY.get(self.game_id, GAME_REGISTRY["snake"])
        
        if "icon" in game_info:
            game_img = get_icon(game_info["icon"], size=(32, 32))
            if game_img:
                ctk.CTkLabel(header_frame, text="", image=game_img).pack(side="left", padx=(10, 5))
                
        self.title_lbl = ctk.CTkLabel(
            header_frame,
            text=f"📊 AI Training Dashboard - {game_info['name']}",
            font=("Arial", 30, "bold")
        )
        self.title_lbl.pack(side="left", padx=(5, 20))

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=10)

        self.create_card(top, "Episodes", self.total_episodes).pack(side="left", padx=15)
        self.create_card(top, "Best Reward", self.best_reward).pack(side="left", padx=15)
        self.create_card(top, "Average Reward", self.average_reward).pack(side="left", padx=15)
        self.create_card(top, "Latest Loss", self.last_loss).pack(side="left", padx=15)

        bottom = ctk.CTkFrame(self, fg_color=("gray95", "#202020"), corner_radius=15, border_width=1, border_color=("gray85", "#303030"))
        bottom.pack(fill="both", expand=True, padx=35, pady=20)

        header = ctk.CTkFrame(bottom, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(header, text="Historical Performance", font=("Arial", 20, "bold")).pack(side="left")
        self.status_label = ctk.CTkLabel(header, text="", font=("Arial", 16, "bold"))
        self.status_label.pack(side="right")

        self.graph_container = ctk.CTkFrame(bottom, fg_color="transparent")
        self.graph_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.refresh_dashboard()

class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#1B1B1B")
        self.settings = SettingsManager()
        self.current_view = None

        self.menu_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.menu_frame.pack(fill="both", expand=True)

        self.scroll_canvas = ctk.CTkScrollableFrame(self.menu_frame, fg_color="transparent")
        self.scroll_canvas.pack(fill="both", expand=True, padx=20, pady=20)

        self.build_menu_view()

    def on_show(self):
        # Reset to the menu view so that if they select a game again, it loads data for the current user
        self.show_menu()

    def build_menu_view(self):
        header_choose = ctk.CTkFrame(self.scroll_canvas, fg_color="transparent")
        header_choose.pack(pady=(20, 5))
        dashboard_icon_title = get_icon("dashboard_color", size=(28, 28))
        ctk.CTkLabel(header_choose, text="" if dashboard_icon_title else "📊 ", image=dashboard_icon_title).pack(side="left", padx=(0, 5))
        title = ctk.CTkLabel(
            header_choose,
            text="Choose Dashboard",
            font=("Arial", 34, "bold")
        )
        title.pack(side="left")

        subtitle = ctk.CTkLabel(
            self.scroll_canvas,
            text="Select a game to view its AI training performance metrics",
            font=("Arial", 16),
            text_color="gray70"
        )
        subtitle.pack(pady=(0, 25))

        for game_id, info in GAME_REGISTRY.items():
            card = ctk.CTkFrame(
                self.scroll_canvas,
                corner_radius=20,
                fg_color="#202020",
                border_width=1,
                border_color="#303030"
            )
            card.pack(fill="x", padx=35, pady=15)

            left = ctk.CTkFrame(card, fg_color="transparent")
            left.pack(side="left", padx=25, pady=20)

            title_frame = ctk.CTkFrame(left, fg_color="transparent")
            title_frame.pack(anchor="w")
            
            if "icon" in info:
                game_img = get_icon(info["icon"], size=(28, 28))
                if game_img:
                    ctk.CTkLabel(title_frame, text="", image=game_img).pack(side="left", padx=(0, 10))
            
            first_word, rest_of_title = info["name"].split(" ", 1)
            
            ctk.CTkLabel(
                title_frame,
                text=first_word + " ",
                font=("Arial", 28, "bold"),
                text_color=info.get("title_color", "white")
            ).pack(side="left")

            ctk.CTkLabel(
                title_frame,
                text=rest_of_title,
                font=("Arial", 28, "bold"),
                text_color="white"
            ).pack(side="left")

            ctk.CTkLabel(
                left,
                text=info["desc"],
                font=("Arial", 15),
                text_color="gray70"
            ).pack(anchor="w", pady=(5, 0))

            right = ctk.CTkFrame(card, fg_color="transparent")
            right.pack(side="right", padx=25, pady=20)

            dashboard_icon = get_icon("dashboard_color", size=(20, 20))
            ctk.CTkButton(
                right,
                text=" View Dashboard",
                image=dashboard_icon,
                width=180,
                height=45,
                fg_color="#10B981",
                hover_color="#059669",
                corner_radius=12,
                font=("Arial", 14, "bold"),
                command=lambda gid=game_id: self.show_view(gid)
            ).pack(pady=6)

    def show_view(self, game_id):
        self.settings.set("active_game", game_id)
        
        self.menu_frame.pack_forget()

        if self.current_view:
            self.current_view.destroy()

        self.current_view = DashboardView(self, game_id, self.show_menu)
        self.current_view.pack(fill="both", expand=True)

    def show_menu(self):
        if self.current_view:
            self.current_view.destroy()
            self.current_view = None
        self.menu_frame.pack(fill="both", expand=True)