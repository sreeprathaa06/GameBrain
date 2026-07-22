import time
import collections
import customtkinter as ctk
from app.utils.icon_loader import get_icon
import numpy as np
import torch
import pygame

from app.widgets.game_viewport import GameViewport
from app.widgets.pygame_viewport import PygameViewport
from app.utils.settings_manager import SettingsManager
from app.utils.leaderboard_manager import LeaderboardManager
from environments.snake_env import SnakeEnv
from environments.ping_pong_env import PingPongEnv
from environments.flappy_bird_env import FlappyBirdEnv
from environments.chess_env import ChessEnv
from controllers.human_controller import HumanController
from rl.dqn.agent import DQNAgent

GAME_REGISTRY = {
    "snake": {
        "name": "Snake AI Arena",
        "icon": "snake_color",
        "title_color": "#10B981", # Green
        "desc": "Deep Q-Learning RL Environment",
        "algo": "DQN Network",
        "actions": "4 discrete directions",
        "env_class": SnakeEnv,
        "is_pygame": False,
        "state_size": 12,
        "action_size": 4
    },
    "ping_pong": {
        "name": "Ping Pong Duel",
        "icon": "ping_pong_color",
        "title_color": "#F43F5E", # Red/Pink
        "desc": "Fast-paced physics paddle game",
        "algo": "DQN Network",
        "actions": "2 continuous/discrete",
        "env_class": PingPongEnv,
        "is_pygame": True,
        "state_size": 6,
        "action_size": 3
    },
    "flappy_bird": {
        "name": "Flappy Bird Clone",
        "icon": "flappy_bird_color",
        "title_color": "#FBBF24", # Yellow
        "desc": "Gravity-defying bird survival",
        "algo": "DQN Network",
        "actions": "Jump / Do Nothing",
        "env_class": FlappyBirdEnv,
        "is_pygame": True,
        "state_size": 4,
        "action_size": 2
    }
}

class PlayPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=("gray90", "#1B1B1B"))
        self.settings = SettingsManager()
        self.current_view = None
        self.previews = []
        self.preview_tick_id = None

        self.menu_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.menu_frame.pack(fill="both", expand=True)

        self.scroll_canvas = ctk.CTkScrollableFrame(self.menu_frame, fg_color="transparent")
        self.scroll_canvas.pack(fill="both", expand=True, padx=20, pady=20)

        self.build_menu_view()

    def build_menu_view(self):
        header = ctk.CTkFrame(self.scroll_canvas, fg_color="transparent")
        header.pack(pady=(20, 5))
        game_icon = get_icon("game_color", size=(28, 28))
        ctk.CTkLabel(header, text="" if game_icon else "🎮 ", image=game_icon).pack(side="left", padx=(0, 5))
        title = ctk.CTkLabel(
            header,
            text="Choose Play Mode",
            font=("Arial", 34, "bold")
        )
        title.pack(side="left")

        subtitle = ctk.CTkLabel(
            self.scroll_canvas,
            text="Launch responsive training or classic play viewports",
            font=("Arial", 16),
            text_color=("gray40", "gray70")
        )
        subtitle.pack(pady=(0, 25))

        for game_id, info in GAME_REGISTRY.items():
            card = ctk.CTkFrame(
                self.scroll_canvas,
                corner_radius=20,
                fg_color=("gray85", "#202020"),
                border_width=1,
                border_color=("gray70", "#303030")
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
            
            ctk.CTkLabel(
                title_frame,
                text=info["name"],
                font=("Arial", 28, "bold"),
                text_color=info.get("title_color", "white")
            ).pack(side="left")

            ctk.CTkLabel(
                left,
                text=info["desc"],
                font=("Arial", 15),
                text_color=("gray40", "gray70")
            ).pack(anchor="w", pady=(5, 20))

            stats = ctk.CTkFrame(left, fg_color="transparent")
            stats.pack(anchor="w")
            self.stat_pill(stats, "Algorithm", info["algo"])
            self.stat_pill(stats, "Actions", info["actions"])

            preview_frame = ctk.CTkFrame(card, fg_color="transparent")
            preview_frame.pack(side="left", expand=True, padx=10, pady=10)

            accent = self.settings.get("accent_color", "blue")
            if info["is_pygame"]:
                viewport = PygameViewport(preview_frame, width=200, height=200)
                env = info["env_class"](render=True, render_callback=viewport.draw_surface)
            else:
                viewport = GameViewport(preview_frame, grid_width=20, grid_height=20, cell_size=12, accent_color=accent)
                env = info["env_class"]()

            viewport.pack()
            self.previews.append({"env": env, "viewport": viewport, "is_pygame": info["is_pygame"], "game_id": game_id})

            right = ctk.CTkFrame(card, fg_color="transparent")
            right.pack(side="right", padx=25, pady=20)

            self.btn(right, " Human Play", "#10B981", lambda gid=game_id: self.show_view("human", gid), "game_color")
            self.btn(right, " Human vs AI", "#8B5CF6", lambda gid=game_id: self.show_view("human_vs_ai", gid), "robot_color")
            self.btn(right, " Train Models", "#F97316", lambda gid=game_id: self.goto_training(gid), "brain_color")

        self.start_preview_loop()

    def stat_pill(self, parent, title, value):
        frame = ctk.CTkFrame(parent, fg_color="#2E2E2E", corner_radius=10, border_width=1, border_color="#3E3E3E")
        frame.pack(side="left", padx=6)
        ctk.CTkLabel(frame, text=title, font=("Arial", 11), text_color=("gray40", "gray70")).pack(padx=12, pady=(6, 0))
        ctk.CTkLabel(frame, text=value, font=("Arial", 13, "bold"), text_color=("#005B96", "cyan")).pack(padx=12, pady=(0, 6))

    def btn(self, parent, text, color, command, icon_name=None):
        icon = get_icon(icon_name, size=(18, 18)) if icon_name else None
        ctk.CTkButton(
            parent,
            text=text,
            image=icon,
            width=180,
            height=45,
            fg_color=color,
            hover_color=color,
            corner_radius=12,
            font=("Arial", 14, "bold"),
            command=command
        ).pack(pady=6)

    def show_view(self, mode, game_id):
        self.stop_preview_loop()
        self.settings.set("active_game", game_id)
        
        self.menu_frame.pack_forget()

        if self.current_view:
            self.current_view.destroy()

        if mode == "human":
            self.current_view = HumanPlayView(self, game_id, self.show_menu)
        elif mode == "ai":
            self.current_view = AIPlayView(self, game_id, self.show_menu)
        elif mode == "human_vs_ai":
            self.current_view = HumanVsAIPlayView(self, game_id, self.show_menu)

        self.current_view.pack(fill="both", expand=True)

    def show_menu(self):
        if self.current_view:
            self.current_view.destroy()
            self.current_view = None
        self.menu_frame.pack(fill="both", expand=True)
        self.start_preview_loop()

    def start_preview_loop(self):
        if self.preview_tick_id is not None:
            self.after_cancel(self.preview_tick_id)
        self.menu_tick()
        
    def stop_preview_loop(self):
        if self.preview_tick_id is not None:
            self.after_cancel(self.preview_tick_id)
            self.preview_tick_id = None

    def menu_tick(self):
        if self.current_view is not None:
            return
            
        import random
        
        for p in self.previews:
            env = p["env"]
            viewport = p["viewport"]
            is_pygame = p["is_pygame"]
            game_id = p.get("game_id", "")
            
            # Simple heuristic "bots" to simulate video gameplay
            action = 0
            if game_id == "snake":
                try:
                    hx, hy = env.snake.head()
                    fx, fy = env.food.get_position()
                    if hx < fx and env.snake.direction != (-1, 0): action = 3 # Right
                    elif hx > fx and env.snake.direction != (1, 0): action = 2 # Left
                    elif hy < fy and env.snake.direction != (0, -1): action = 1 # Down
                    elif hy > fy and env.snake.direction != (0, 1): action = 0 # Up
                    else: action = random.choice([0, 1, 2, 3])
                except:
                    action = random.choice([0, 1, 2, 3])
            elif game_id == "ping_pong":
                try:
                    if env.paddle_y + env.paddle_h/2 < env.ball_y: action = 2 # Down
                    elif env.paddle_y + env.paddle_h/2 > env.ball_y: action = 1 # Up
                except:
                    pass
            elif game_id == "flappy_bird":
                try:
                    # Flap if dropping below middle
                    if env.bird_y > env.height / 2: action = 1
                except:
                    pass
            
            try:
                _, _, done, _ = env.step(action)
                if done:
                    env.reset()
                
                if is_pygame:
                    env.render()
                else:
                    viewport.draw_game(env.snake.get_body(), env.food.get_position(), env.score)
            except Exception:
                pass
                
        self.preview_tick_id = self.after(50, self.menu_tick)

    def goto_training(self, game_id):
        self.settings.set("active_game", game_id)
        app = self.winfo_toplevel()
        if hasattr(app, "show_page"):
            app.show_page("ai_training")
            
# Helper functions for handling viewports
def create_viewport(parent, is_pygame, accent_color):
    if is_pygame:
        viewport = PygameViewport(parent, width=400, height=400)
    else:
        viewport = GameViewport(parent, grid_width=20, grid_height=20, cell_size=22, accent_color=accent_color)
    return viewport

class HumanPlayView(ctk.CTkFrame):
    def __init__(self, parent, game_id, exit_callback):
        super().__init__(parent, fg_color="transparent")
        self.exit_callback = exit_callback
        self.settings = SettingsManager()
        self.game_id = game_id
        self.leaderboard = LeaderboardManager(game_id)
        self.game_info = GAME_REGISTRY[game_id]
        self.is_pygame = self.game_info["is_pygame"]
        
        self.running = False
        self.paused = False
        self.score = 0
        self.survival_steps = 0
        self.start_time = 0
        self.action_queue = collections.deque()

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        game_panel = ctk.CTkFrame(self, fg_color=("gray85", "#202020"), corner_radius=15, border_width=1, border_color=("gray70", "#303030"))
        game_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)

        accent = self.settings.get("accent_color", "blue")
        self.viewport = create_viewport(game_panel, self.is_pygame, accent)
        self.viewport.pack(expand=True, pady=15)

        # Init Env
        if self.is_pygame:
            self.env = self.game_info["env_class"](render=True, render_callback=self.viewport.draw_surface)
        else:
            self.env = self.game_info["env_class"]()

        self.controller = HumanController()

        control_panel = ctk.CTkFrame(self, fg_color=("gray85", "#202020"), corner_radius=15, border_width=1, border_color=("gray70", "#303030"))
        control_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)

        ctk.CTkLabel(control_panel, text="Game Controller", font=("Arial", 18, "bold"), text_color=("#005B96", "cyan")).pack(pady=15)

        stats_frame = ctk.CTkFrame(control_panel, fg_color="#282828", corner_radius=10)
        stats_frame.pack(fill="x", padx=15, pady=5)

        self.score_lbl = self.add_stat_row(stats_frame, "Score", "0")
        self.high_score_lbl = self.add_stat_row(stats_frame, "High Score", str(self.leaderboard.get_data().get("highest_human_score", 0)))
        self.steps_lbl = self.add_stat_row(stats_frame, "Time Alive", "0s")

        play_btn_icon = get_icon("play_btn", size=(16, 16))
        self.start_btn = ctk.CTkButton(control_panel, text=" Start Game (P)", image=play_btn_icon, fg_color=("#059669", "#10B981"), height=40, font=("Arial", 13, "bold"), command=self.toggle_play)
        self.start_btn.pack(fill="x", padx=15, pady=8)

        refresh_icon = get_icon("refresh_color", size=(16, 16))
        ctk.CTkButton(control_panel, text=" Restart (R)", image=refresh_icon, fg_color=("#1D4ED8", "#1E3A8A"), height=38, command=self.restart).pack(fill="x", padx=15, pady=4)
        close_icon = get_icon("close", size=(16, 16))
        ctk.CTkButton(control_panel, text=" Exit to Menu (ESC)", image=close_icon, fg_color=("#B91C1C", "#D32F2F"), height=38, command=self.exit).pack(fill="x", padx=15, pady=4)

        self.bind_events()
        
    def draw_current_state(self, overlay_text=None):
        if self.is_pygame:
            self.env.render()
            if overlay_text:
                self.viewport.configure(text=overlay_text, text_color=("#B91C1C", "red"), font=("Arial", 24, "bold"), compound="center")
            else:
                self.viewport.configure(text="")
        else:
            self.viewport.draw_game(self.env.snake.get_body(), self.env.food.get_position(), self.env.score, overlay_text=overlay_text)

    def add_stat_row(self, parent, title, initial_val):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=4)
        ctk.CTkLabel(row, text=title, font=("Arial", 12), text_color=("gray40", "gray75")).pack(side="left")
        lbl = ctk.CTkLabel(row, text=initial_val, font=("Arial", 14, "bold"), text_color=("#005B96", "cyan"))
        lbl.pack(side="right")
        return lbl

    def bind_events(self):
        self.winfo_toplevel().bind_all("<KeyPress>", self.on_key_press)
        self.winfo_toplevel().bind_all("<KeyRelease>", self.on_key_release)

    def unbind_events(self):
        self.winfo_toplevel().unbind_all("<KeyPress>")
        self.winfo_toplevel().unbind_all("<KeyRelease>")

    def on_key_press(self, event):
        key = event.keysym.lower()
        
        if self.game_info["name"] == "Ping Pong Duel":
            if key in ("w", "up"):
                self.controller.action = 1
            elif key in ("s", "down"):
                self.controller.action = 2
        elif self.game_info["name"] == "Flappy Bird Clone":
            if key in ("w", "up", "space"):
                self.controller.action = 1
        else: # Snake
            if key in ("up", "w"):
                self.action_queue.append(0)
            elif key in ("down", "s"):
                self.action_queue.append(1)
            elif key in ("left", "a"):
                self.action_queue.append(2)
            elif key in ("right", "d"):
                self.action_queue.append(3)

        if key == "p" or (key == "space" and self.game_info["name"] != "Flappy Bird Clone"):
            self.toggle_play()
        elif key == "r":
            self.restart()
        elif key == "escape":
            self.exit()
            
    def on_key_release(self, event):
        key = event.keysym.lower()
        if self.game_info["name"] in ("Ping Pong Duel", "Flappy Bird Clone"):
            if key in ("w", "s", "up", "down", "space"):
                self.controller.action = 0

    def toggle_play(self):
        if not self.running:
            self.running = True
            self.paused = False
            self.start_time = time.time() - self.survival_steps
            self.start_btn.configure(text="⏸ Pause (P)", fg_color=("#EA580C", "#F57C00"))
            self.focus_set()
            self.game_tick()
        else:
            self.paused = not self.paused
            if self.paused:
                self.start_btn.configure(text=" Resume (P)", image=get_icon("play_btn", size=(16, 16)), fg_color=("#059669", "#10B981"))
                self.draw_current_state("GAME PAUSED")
            else:
                self.start_btn.configure(text=" Pause (P)", image=get_icon("pause", size=(16, 16)), fg_color=("#EA580C", "#F57C00"))
                self.start_time = time.time() - self.survival_steps
                self.focus_set()
                self.game_tick()

    def restart(self):
        self.env.reset()
        self.controller.action = 3 if not self.is_pygame else 0
        self.action_queue.clear()
        self.score = 0
        self.survival_steps = 0
        self.start_time = time.time()
        self.score_lbl.configure(text="0")
        self.steps_lbl.configure(text="0s")
        self.draw_current_state()
        
        if not self.running:
            self.running = True
            self.paused = False
            self.start_btn.configure(text=" Pause (P)", image=get_icon("pause", size=(16, 16)), fg_color=("#EA580C", "#F57C00"))
            self.focus_set()
            self.game_tick()
        elif self.paused:
            self.paused = False
            self.start_btn.configure(text=" Pause (P)", image=get_icon("pause", size=(16, 16)), fg_color=("#EA580C", "#F57C00"))
            self.focus_set()
            self.game_tick()

    def game_tick(self):
        if not self.running or self.paused:
            return

        if self.game_info["name"] == "Snake AI Arena" and self.action_queue:
            self.controller.action = self.action_queue.popleft()

        action = self.controller.get_action()
        # Ping Pong & Flappy Bird don't have 4 actions typically mapped this way, 
        # but their step functions handle the ints passed.
        _, _, done, score = self.env.step(action)
        self.survival_steps += 1
        self.score = score

        self.draw_current_state()
        
        self.score_lbl.configure(text=str(self.score))
        
        sec_alive = int(time.time() - self.start_time)
        self.steps_lbl.configure(text=f"{sec_alive}s")

        if done:
            self.running = False
            self.start_btn.configure(text=" Start Game (P)", image=get_icon("play_btn", size=(16, 16)), fg_color=("#059669", "#10B981"))
            
            self.leaderboard.update_score("Human", self.score, self.survival_steps)
            self.high_score_lbl.configure(text=str(self.leaderboard.get_data().get("highest_human_score", 0)))
            
            self.draw_current_state(f"GAME OVER\nScore: {self.score}")
            return

        if self.game_info["name"] == "🎾 Ping Pong Duel":
            delay_ms = 16 # ~60fps
        elif self.game_info["name"] == "🦅 Flappy Bird Clone":
            delay_ms = 33 # ~30fps
        else:
            base_fps = 10 if self.is_pygame else 6
            dynamic_fps = min(30, base_fps + (self.score // 3))
            delay_ms = int(1000 / dynamic_fps)
        self.after(delay_ms, self.game_tick)

    def exit(self):
        self.running = False
        self.unbind_events()
        self.exit_callback()


class AIPlayView(ctk.CTkFrame):
    def __init__(self, parent, game_id, exit_callback):
        super().__init__(parent, fg_color="transparent")
        self.exit_callback = exit_callback
        self.settings = SettingsManager()
        self.game_id = game_id
        self.leaderboard = LeaderboardManager(game_id)
        self.game_info = GAME_REGISTRY[game_id]
        self.is_pygame = self.game_info["is_pygame"]

        self.running = False
        self.paused = False
        self.survival_steps = 0
        self.decision_times = collections.deque(maxlen=100)

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        game_panel = ctk.CTkFrame(self, fg_color=("gray85", "#202020"), corner_radius=15, border_width=1, border_color=("gray70", "#303030"))
        game_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)

        accent = self.settings.get("accent_color", "blue")
        self.viewport = create_viewport(game_panel, self.is_pygame, accent)
        self.viewport.pack(expand=True, pady=15)

        if self.is_pygame:
            self.env = self.game_info["env_class"](render=True, render_callback=self.viewport.draw_surface)
        else:
            self.env = self.game_info["env_class"]()

        self.agent = DQNAgent(state_size=self.game_info["state_size"], action_size=self.game_info["action_size"])
        active_model = f"best_dqn_model_{game_id}.pth"
        self.agent.load_model(active_model)

        control_panel = ctk.CTkFrame(self, fg_color=("gray85", "#202020"), corner_radius=15, border_width=1, border_color=("gray70", "#303030"))
        control_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)

        ctk.CTkLabel(control_panel, text="Neural Network Agent", font=("Arial", 18, "bold"), text_color=("#005B96", "cyan")).pack(pady=(15, 2))
        
        # Add Training Progress Bar
        progress = self.leaderboard.get_training_progress(self.game_id)
        prog_frame = ctk.CTkFrame(control_panel, fg_color="transparent")
        prog_frame.pack(fill="x", padx=15, pady=(0, 10))
        prog_bar = ctk.CTkProgressBar(prog_frame, progress_color="cyan", height=6)
        prog_bar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        prog_bar.set(progress / 100.0)
        ctk.CTkLabel(prog_frame, text=f"{progress}% Trained", font=("Arial", 10), text_color=("gray30", "gray60")).pack(side="right")

        stats_frame = ctk.CTkFrame(control_panel, fg_color="#282828", corner_radius=10)
        stats_frame.pack(fill="x", padx=15, pady=5)

        self.score_lbl = self.add_stat_row(stats_frame, "Current Score", "0")
        self.steps_lbl = self.add_stat_row(stats_frame, "Decision Cycles", "0")
        self.latency_lbl = self.add_stat_row(stats_frame, "Avg Latency", "0.0 ms")
        self.direction_lbl = self.add_stat_row(stats_frame, "Predicted Action", "None")

        q_frame = ctk.CTkFrame(control_panel, fg_color="#282828", corner_radius=10)
        q_frame.pack(fill="x", padx=15, pady=8)
        
        ctk.CTkLabel(q_frame, text="Normalized Action Confidence", font=("Arial", 12, "bold")).pack(pady=6)

        self.q_bars = {}
        for act in range(min(4, self.game_info["action_size"])):
            act_str = f"Action {act}"
            row = ctk.CTkFrame(q_frame, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=3)
            ctk.CTkLabel(row, text=act_str, font=("Arial", 11), width=50, anchor="w").pack(side="left")
            
            bar = ctk.CTkProgressBar(row, width=125)
            bar.pack(side="left", padx=5)
            bar.set(0.0)

            lbl = ctk.CTkLabel(row, text="0.0%", font=("Arial", 10, "bold"), width=40)
            lbl.pack(side="right")
            self.q_bars[act] = (bar, lbl)

        play_btn_icon = get_icon("play_btn", size=(16, 16))
        self.start_btn = ctk.CTkButton(control_panel, text=" Run Autopilot", image=play_btn_icon, fg_color=("#059669", "#10B981"), height=40, font=("Arial", 13, "bold"), command=self.toggle_play)
        self.start_btn.pack(fill="x", padx=15, pady=8)

        refresh_icon = get_icon("refresh_color", size=(16, 16))
        ctk.CTkButton(control_panel, text=" Restart Environment", image=refresh_icon, fg_color=("#1D4ED8", "#1E3A8A"), height=38, command=self.restart).pack(fill="x", padx=15, pady=4)
        close_icon = get_icon("close", size=(16, 16))
        ctk.CTkButton(control_panel, text=" Close", image=close_icon, fg_color=("#B91C1C", "#D32F2F"), height=38, command=self.exit).pack(fill="x", padx=15, pady=4)

    def draw_current_state(self, overlay_text=None, ai_info=None):
        if self.is_pygame:
            self.env.render()
            if overlay_text:
                self.viewport.configure(text=overlay_text, text_color=("#B91C1C", "red"), font=("Arial", 24, "bold"), compound="center")
            else:
                self.viewport.configure(text="")
        else:
            self.viewport.draw_game(self.env.snake.get_body(), self.env.food.get_position(), self.env.score, overlay_text=overlay_text, ai_info=ai_info)

    def add_stat_row(self, parent, title, initial_val):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=4)
        ctk.CTkLabel(row, text=title, font=("Arial", 12), text_color=("gray40", "gray75")).pack(side="left")
        lbl = ctk.CTkLabel(row, text=initial_val, font=("Arial", 13, "bold"), text_color=("#005B96", "cyan"))
        lbl.pack(side="right")
        return lbl

    def toggle_play(self):
        if not self.running:
            self.running = True
            self.paused = False
            self.start_btn.configure(text="⏸ Pause Autopilot", fg_color=("#EA580C", "#F57C00"))
            self.game_tick()
        else:
            self.paused = not self.paused
            if self.paused:
                self.start_btn.configure(text=" Resume Autopilot", image=get_icon("play_btn", size=(16, 16)), fg_color=("#059669", "#10B981"))
                self.draw_current_state("AUTOPILOT PAUSED")
            else:
                self.start_btn.configure(text=" Pause Autopilot", image=get_icon("pause", size=(16, 16)), fg_color=("#EA580C", "#F57C00"))
                self.game_tick()

    def restart(self):
        self.env.reset()
        self.survival_steps = 0
        self.decision_times.clear()
        self.score_lbl.configure(text="0")
        self.steps_lbl.configure(text="0")
        self.latency_lbl.configure(text="0.0 ms")
        self.direction_lbl.configure(text="None")
        for bar, lbl in self.q_bars.values():
            bar.set(0.0)
            lbl.configure(text="0.0%")
        
        self.draw_current_state()

        if not self.running:
            self.running = True
            self.paused = False
            self.start_btn.configure(text=" Pause Autopilot", image=get_icon("pause", size=(16, 16)), fg_color=("#EA580C", "#F57C00"))
            self.game_tick()
        elif self.paused:
            self.paused = False
            self.start_btn.configure(text=" Pause Autopilot", image=get_icon("pause", size=(16, 16)), fg_color=("#EA580C", "#F57C00"))
            self.game_tick()

    def predict_action(self, state):
        start = time.perf_counter()
        
        state_t = torch.FloatTensor(state).unsqueeze(0).to(self.agent.device)
        self.agent.model.eval()
        with torch.no_grad():
            q_values = self.agent.model(state_t).squeeze().cpu().numpy()
            if q_values.ndim == 0:
                q_values = np.array([q_values])
        
        decision_time = time.perf_counter() - start
        self.decision_times.append(decision_time)

        action = int(np.argmax(q_values))
        exp_q = np.exp(q_values - np.max(q_values))
        probs = exp_q / np.sum(exp_q)

        return action, q_values, probs

    def game_tick(self):
        if not self.running or self.paused:
            return

        state = self.env.get_state()
        action, q_vals, probs = self.predict_action(state)

        next_state, _, done, score = self.env.step(action)
        self.survival_steps += 1

        ai_info = {
            "action": str(action),
            "confidence": probs[action] * 100
        }
        self.draw_current_state(ai_info=ai_info)

        self.score_lbl.configure(text=str(score))
        self.steps_lbl.configure(text=str(self.survival_steps))
        
        avg_lat = sum(self.decision_times) / len(self.decision_times) * 1000 if self.decision_times else 0
        self.latency_lbl.configure(text=f"{avg_lat:.2f} ms")
        self.direction_lbl.configure(text=str(action))

        for idx, (bar, lbl) in self.q_bars.items():
            if idx < len(probs):
                conf = probs[idx]
                bar.set(conf)
                lbl.configure(text=f"{conf*100:.1f}%")

        if done:
            self.running = False
            self.start_btn.configure(text=" Run Autopilot", image=get_icon("play_btn", size=(16, 16)), fg_color=("#059669", "#10B981"))
            self.leaderboard.update_score("AI", score, self.survival_steps)
            self.draw_current_state(f"AI DIED\nScore: {score}")
            return

        fps = self.settings.get("fps", 12)
        delay_ms = int(1000 / fps)
        self.after(delay_ms, self.game_tick)

    def exit(self):
        self.running = False
        self.exit_callback()


class HumanVsAIPlayView(ctk.CTkFrame):
    def __init__(self, parent, game_id, exit_callback):
        super().__init__(parent, fg_color="transparent")
        self.exit_callback = exit_callback
        self.settings = SettingsManager()
        self.game_id = game_id
        self.leaderboard = LeaderboardManager(game_id)
        self.game_info = GAME_REGISTRY[game_id]
        self.is_pygame = self.game_info["is_pygame"]

        self.running = False
        self.paused = False
        self.survival_steps = 0
        self.h_is_done = False
        self.ai_is_done = False
        self.h_action_queue = collections.deque()

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure(2, weight=3)
        self.grid_rowconfigure(0, weight=1)

        h_panel = ctk.CTkFrame(self, fg_color=("gray85", "#202020"), corner_radius=15, border_width=1, border_color=("gray70", "#303030"))
        h_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=10)
        ctk.CTkLabel(h_panel, text="👤 HUMAN COMPANION", font=("Arial", 16, "bold"), text_color=("#059669", "#10B981")).pack(pady=10)
        
        self.h_viewport = create_viewport(h_panel, self.is_pygame, "green")
        self.h_viewport.pack(expand=True, pady=10)

        ai_panel = ctk.CTkFrame(self, fg_color=("gray85", "#202020"), corner_radius=15, border_width=1, border_color=("gray70", "#303030"))
        ai_panel.grid(row=0, column=2, sticky="nsew", padx=(5, 0), pady=10)
        robot_icon = get_icon("robot_color", size=(20, 20))
        header_robot = ctk.CTkFrame(ai_panel, fg_color="transparent")
        header_robot.pack(pady=(10, 2))
        ctk.CTkLabel(header_robot, text="" if robot_icon else "🤖 ", image=robot_icon).pack(side="left", padx=(0, 5))
        ctk.CTkLabel(header_robot, text="AI AUTOPILOT", font=("Arial", 16, "bold"), text_color=("#2563EB", "#3B82F6")).pack(side="left")
        
        # Add Training Progress Bar for AI
        progress = self.leaderboard.get_training_progress(self.game_id)
        prog_frame = ctk.CTkFrame(ai_panel, fg_color="transparent")
        prog_frame.pack(fill="x", padx=20, pady=(0, 10))
        prog_bar = ctk.CTkProgressBar(prog_frame, progress_color="#3B82F6", height=6)
        prog_bar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        prog_bar.set(progress / 100.0)
        ctk.CTkLabel(prog_frame, text=f"{progress}% Trained", font=("Arial", 10), text_color=("gray30", "gray60")).pack(side="right")

        self.ai_viewport = create_viewport(ai_panel, self.is_pygame, "blue")
        self.ai_viewport.pack(expand=True, pady=10)

        if self.is_pygame:
            self.h_env = self.game_info["env_class"](render=True, render_callback=self.h_viewport.draw_surface)
            self.ai_env = self.game_info["env_class"](render=True, render_callback=self.ai_viewport.draw_surface)
        else:
            self.h_env = self.game_info["env_class"]()
            self.ai_env = self.game_info["env_class"]()

        self.h_controller = HumanController()
        self.ai_agent = DQNAgent(state_size=self.game_info["state_size"], action_size=self.game_info["action_size"])
        active_model = f"best_dqn_model_{game_id}.pth"
        self.ai_agent.load_model(active_model)

        if not self.is_pygame:
            self.shared_food = self.h_env.food.get_position()
            self.ai_env.food.position = self.shared_food

        center_panel = ctk.CTkFrame(self, fg_color="#252525", corner_radius=15, border_width=1, border_color="#3C3C3C")
        center_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(center_panel, text="VERSUS DASHBOARD", font=("Arial", 16, "bold"), text_color=("#005B96", "cyan")).pack(pady=15)

        sb_frame = ctk.CTkFrame(center_panel, fg_color="#303030", corner_radius=10)
        sb_frame.pack(fill="x", padx=15, pady=5)
        
        h_score_row = ctk.CTkFrame(sb_frame, fg_color="transparent")
        h_score_row.pack(fill="x", padx=15, pady=6)
        ctk.CTkLabel(h_score_row, text="Human:", font=("Arial", 13, "bold"), text_color=("#059669", "#10B981")).pack(side="left")
        self.h_score_lbl = ctk.CTkLabel(h_score_row, text="0", font=("Arial", 16, "bold"))
        self.h_score_lbl.pack(side="right")

        ai_score_row = ctk.CTkFrame(sb_frame, fg_color="transparent")
        ai_score_row.pack(fill="x", padx=15, pady=6)
        ctk.CTkLabel(ai_score_row, text="AI Bot:", font=("Arial", 13, "bold"), text_color=("#2563EB", "#3B82F6")).pack(side="left")
        self.ai_score_lbl = ctk.CTkLabel(ai_score_row, text="0", font=("Arial", 16, "bold"))
        self.ai_score_lbl.pack(side="right")

        rocket_icon = get_icon("rocket_color", size=(16, 16))
        self.start_btn = ctk.CTkButton(center_panel, text=" Duel Game (P)", image=rocket_icon, fg_color=("#BE123C", "#E11D48"), height=40, font=("Arial", 13, "bold"), command=self.toggle_play)
        self.start_btn.pack(fill="x", padx=15, pady=12)

        refresh_icon = get_icon("refresh_color", size=(16, 16))
        ctk.CTkButton(center_panel, text=" Restart Match", image=refresh_icon, fg_color=("#1D4ED8", "#1E3A8A"), height=38, command=self.restart).pack(fill="x", padx=15, pady=4)
        close_icon = get_icon("close", size=(16, 16))
        ctk.CTkButton(center_panel, text=" Exit Duel", image=close_icon, fg_color=("#B91C1C", "#D32F2F"), height=38, command=self.exit).pack(fill="x", padx=15, pady=4)

        self.bind_events()

    def bind_events(self):
        self.winfo_toplevel().bind_all("<KeyPress>", self.on_key_press)
        self.winfo_toplevel().bind_all("<KeyRelease>", self.on_key_release)

    def unbind_events(self):
        self.winfo_toplevel().unbind_all("<KeyPress>")
        self.winfo_toplevel().unbind_all("<KeyRelease>")

    def on_key_press(self, event):
        key = event.keysym.lower()
        
        if self.game_info["name"] == "Ping Pong Duel":
            if key in ("w", "up"):
                self.h_controller.action = 1
            elif key in ("s", "down"):
                self.h_controller.action = 2
        elif self.game_info["name"] == "Flappy Bird Clone":
            if key in ("w", "up", "space"):
                self.h_controller.action = 1
        else: # Snake
            if key in ("up", "w"):
                self.h_action_queue.append(0)
            elif key in ("down", "s"):
                self.h_action_queue.append(1)
            elif key in ("left", "a"):
                self.h_action_queue.append(2)
            elif key in ("right", "d"):
                self.h_action_queue.append(3)

        if key == "p" or (key == "space" and self.game_info["name"] != "Flappy Bird Clone"):
            self.toggle_play()
            
    def on_key_release(self, event):
        key = event.keysym.lower()
        if self.game_info["name"] in ("Ping Pong Duel", "Flappy Bird Clone"):
            if key in ("w", "s", "up", "down", "space"):
                self.h_controller.action = 0

    def draw_current_states(self, h_overlay=None, ai_overlay=None):
        if self.is_pygame:
            self.h_env.render()
            if h_overlay:
                self.h_viewport.configure(text=h_overlay, text_color=("#B91C1C", "red"), font=("Arial", 24, "bold"), compound="center")
            else:
                self.h_viewport.configure(text="")
                
            self.ai_env.render()
            if ai_overlay:
                self.ai_viewport.configure(text=ai_overlay, text_color=("#B91C1C", "red"), font=("Arial", 24, "bold"), compound="center")
            else:
                self.ai_viewport.configure(text="")
        else:
            self.h_viewport.draw_game(self.h_env.snake.get_body(), self.h_env.food.get_position(), self.h_env.score, overlay_text=h_overlay)
            self.ai_viewport.draw_game(self.ai_env.snake.get_body(), self.ai_env.food.get_position(), self.ai_env.score, overlay_text=ai_overlay)

    def toggle_play(self):
        if not self.running:
            self.running = True
            self.paused = False
            self.start_btn.configure(text="⏸ Pause Duel", fg_color=("#EA580C", "#F57C00"))
            self.focus_set()
            self.game_tick()
        else:
            self.paused = not self.paused
            if self.paused:
                self.start_btn.configure(text=" Resume Duel", image=get_icon("play_btn", size=(16, 16)), fg_color=("#059669", "#10B981"))
                self.draw_current_states("MATCH PAUSED", "MATCH PAUSED")
            else:
                self.start_btn.configure(text=" Pause Duel", image=get_icon("pause", size=(16, 16)), fg_color=("#EA580C", "#F57C00"))
                self.focus_set()
                self.game_tick()

    def restart(self):
        self.h_env.reset()
        self.ai_env.reset()
        self.h_controller.action = 3 if not self.is_pygame else 0
        self.h_action_queue.clear()
        self.survival_steps = 0
        self.h_is_done = False
        self.ai_is_done = False

        if not self.is_pygame:
            self.shared_food = self.h_env.food.get_position()
            self.ai_env.food.position = self.shared_food

        self.h_score_lbl.configure(text="0")
        self.ai_score_lbl.configure(text="0")

        self.draw_current_states()

        if not self.running:
            self.running = True
            self.paused = False
            self.start_btn.configure(text=" Pause Duel", image=get_icon("pause", size=(16, 16)), fg_color=("#EA580C", "#F57C00"))
            self.focus_set()
            self.game_tick()
        elif self.paused:
            self.paused = False
            self.start_btn.configure(text=" Pause Duel", image=get_icon("pause", size=(16, 16)), fg_color=("#EA580C", "#F57C00"))
            self.focus_set()
            self.game_tick()



    def game_tick(self):
        if not self.running or self.paused:
            return

        if self.game_info["name"] == "Snake AI Arena" and self.h_action_queue:
            self.h_controller.action = self.h_action_queue.popleft()

        h_action = self.h_controller.get_action()

        if not self.ai_is_done:
            ai_state = self.ai_env.get_state()
            ai_action = self.ai_agent.predict(ai_state)

        h_old_score = self.h_env.score if not self.is_pygame else 0
        ai_old_score = self.ai_env.score if not self.is_pygame else 0

        if not self.h_is_done:
            _, _, h_done, h_score = self.h_env.step(h_action)
            self.h_is_done = h_done
        else:
            h_score = self.h_env.score

        if not self.ai_is_done:
            _, _, ai_done, ai_score = self.ai_env.step(ai_action)
            self.ai_is_done = ai_done
        else:
            ai_score = self.ai_env.score

        self.survival_steps += 1

        if not self.is_pygame:
            h_eaten = not self.h_is_done and (h_score > h_old_score)
            ai_eaten = not self.ai_is_done and (ai_score > ai_old_score)

            if h_eaten or ai_eaten:
                bodies = []
                if not self.h_is_done: bodies.extend(self.h_env.snake.get_body())
                if not self.ai_is_done: bodies.extend(self.ai_env.snake.get_body())
                self.h_env.food.spawn(bodies)
                self.shared_food = self.h_env.food.get_position()
                self.ai_env.food.position = self.shared_food
            
            h_score = self.h_env.score
            ai_score = self.ai_env.score

        h_overlay = "DEAD" if self.h_is_done else None
        ai_overlay = "DEAD" if self.ai_is_done else None
        self.draw_current_states(h_overlay, ai_overlay)

        self.h_score_lbl.configure(text=str(h_score))
        self.ai_score_lbl.configure(text=str(ai_score))

        if self.h_is_done and self.ai_is_done:
            self.running = False
            self.start_btn.configure(text=" Duel Game (P)", fg_color=("#BE123C", "#E11D48"))

            if self.h_is_done and self.ai_is_done:
                winner = "Double Knockout!"
                result = "It's a Tie!"
                if h_score > ai_score:
                    winner = "Human Wins on High Score!"
                    result = "Human Wins!"
                elif ai_score > h_score:
                    winner = "AI Wins on High Score!"
                    result = "AI Wins!"

            h_won = (result == "Human Wins!")
            self.leaderboard.update_score("Human vs AI", h_score, self.survival_steps, is_winner=h_won)

            self.draw_current_states(f"DUEL OVER\n{winner}", f"DUEL OVER\n{winner}")
            return

        if self.game_info["name"] == "Ping Pong Duel":
            delay_ms = 16 # ~60fps
        elif self.game_info["name"] == "Flappy Bird Clone":
            delay_ms = 33 # ~30fps
        else:
            base_fps = 10 if self.is_pygame else 6
            highest_score = max(h_score, ai_score)
            dynamic_fps = min(30, base_fps + (highest_score // 3))
            delay_ms = int(1000 / dynamic_fps)
        self.after(delay_ms, self.game_tick)

    def exit(self):
        self.running = False
        self.unbind_events()
        self.exit_callback()