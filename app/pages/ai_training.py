import os
import time
import threading
import collections
import customtkinter as ctk
from app.utils.icon_loader import get_icon
import numpy as np
import pandas as pd
import torch
from tkinter import filedialog, messagebox

# Matplotlib embedding
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from rl.dqn.train import train
from rl.dqn.agent import DQNAgent
from app.widgets.game_viewport import GameViewport
from app.widgets.pygame_viewport import PygameViewport
from app.utils.settings_manager import SettingsManager
from app.utils.leaderboard_manager import LeaderboardManager
from app.pages.play import GAME_REGISTRY

class AITrainingPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#1B1B1B")

        self.settings = SettingsManager()
        self.game_id = self.settings.get("active_game", "snake")
        self.leaderboard = LeaderboardManager(self.game_id)

        # Threading control events
        self.training = False
        self.pause_event = threading.Event()
        self.stop_event = threading.Event()
        self.train_delay_ms = 30 # default step delay in ms

        # Performance stats variables
        self.start_time = 0
        self.episode_steps = 0
        self.step_times = collections.deque(maxlen=100)
        self.best_reward = -99999.0
        self.episodes_run = 0

        # Plot lists
        self.episodes_list = []
        self.rewards_list = []
        self.losses_list = []
        self.epsilons_list = []
        self.speeds_list = []

        # Replay logging
        self.best_episode_steps = [] # stores (body, food, score)
        self.current_episode_steps = []
        
        self.game_info = GAME_REGISTRY["snake"]
        self.game_id = "snake"
        self.current_username = self.settings.get("username", "Player1")
        
        self.build_ui()
        self.update_active_game()

    def on_show(self):
        new_username = self.settings.get("username", "Player1")
        new_game_id = self.settings.get("active_game", "snake")
        
        if self.current_username != new_username or self.game_id != new_game_id:
            if self.training:
                self.stop_training()
                
            self.current_username = new_username
            self.game_id = new_game_id
            
            # Clear stored data
            self.episodes_list.clear()
            self.rewards_list.clear()
            self.losses_list.clear()
            self.epsilons_list.clear()
            self.speeds_list.clear()
            self.best_episode_steps.clear()
            self.best_reward = -99999.0
            
            # Clear plots
            self.ax_reward.clear(); self.style_axes(self.ax_reward, "Episode", "Score / Reward")
            self.ax_loss.clear(); self.style_axes(self.ax_loss, "Episode", "MSE Loss")
            self.ax_epsilon.clear(); self.style_axes(self.ax_epsilon, "Episode", "Epsilon Value")
            self.ax_speed.clear(); self.style_axes(self.ax_speed, "Episode", "Speed (steps/sec)")
            
            self.canvas_reward.draw_idle()
            self.canvas_loss.draw_idle()
            self.canvas_epsilon.draw_idle()
            self.canvas_speed.draw_idle()

            # Reset HUD labels
            self.ep_lbl.configure(text="0 / 500")
            self.rew_lbl.configure(text="0.0")
            self.best_rew_lbl.configure(text="0.0")
            self.loss_lbl.configure(text="0.000")
            self.eps_lbl.configure(text="1.00")
            self.speed_lbl.configure(text="0 steps/s")
            self.mem_lbl.configure(text="0 MB")
            self.time_lbl.configure(text="0s")
            
            self.log_txt.delete("1.0", "end")
            
            self.update_active_game()

    def update_active_game(self):
        self.game_id = self.settings.get("active_game", "snake")
        if self.game_id not in GAME_REGISTRY:
            self.game_id = "snake"
        self.game_info = GAME_REGISTRY[self.game_id]
        self.leaderboard = LeaderboardManager(self.game_id)
        
        # update UI
        if hasattr(self, 'title_lbl'):
            username = self.settings.get("username", "Player1")
            self.title_lbl.configure(text=f"{username}'s AI Center - {self.game_info['name']}")
            
        if hasattr(self, 'game_icon_lbl'):
            if "icon" in self.game_info:
                g_icon = get_icon(self.game_info["icon"], size=(24, 24))
                if g_icon:
                    self.game_icon_lbl.configure(image=g_icon)
        
        active_model = f"best_dqn_model_{self.game_id}.pth"
        if hasattr(self, 'model_lbl'):
            self.model_lbl.configure(text=active_model)

        if hasattr(self, 'vp_card'):
            # Clear old viewport
            for widget in self.vp_card.winfo_children():
                widget.destroy()

            is_pygame = self.game_info["is_pygame"]
            accent = self.settings.get("accent_color", "blue")
            if is_pygame:
                self.viewport = PygameViewport(self.vp_card, width=400, height=400)
            else:
                self.viewport = GameViewport(self.vp_card, grid_width=20, grid_height=20, cell_size=15, accent_color=accent)
            self.viewport.pack(expand=True, pady=10)

    def build_ui(self):
        # 1. Header Frame
        header = ctk.CTkFrame(self, fg_color="#202020", corner_radius=12, height=65, border_width=1, border_color="#303030")
        header.pack(fill="x", padx=15, pady=(10, 5))
        header.pack_propagate(False)

        # Left title
        brain_icon = get_icon("brain_color", size=(24, 24))
        ctk.CTkLabel(header, text="" if brain_icon else "🧠 ", image=brain_icon).pack(side="left", padx=(10, 5))
        
        self.game_icon_lbl = ctk.CTkLabel(header, text="")
        self.game_icon_lbl.pack(side="left", padx=(0, 5))

        self.title_lbl = ctk.CTkLabel(header, text="Training Control Center", font=("Arial", 18, "bold"), text_color="cyan")
        self.title_lbl.pack(side="left", padx=(0, 20))

        # Right status markers
        self.device_lbl = self.status_marker(header, "Device", "CUDA" if torch.cuda.is_available() else "CPU")
        self.model_lbl = self.status_marker(header, "Active weights", self.settings.get("active_model", "best_dqn_model.pth"))
        self.status_lbl = self.status_marker(header, "Status", "Idle", color="orange")

        # 2. Main content split (Middle)
        mid_layout = ctk.CTkFrame(self, fg_color="transparent")
        mid_layout.pack(fill="both", expand=True, padx=15, pady=5)

        # Left side: Viewport & Controls
        left_side = ctk.CTkFrame(mid_layout, fg_color="transparent")
        left_side.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # Viewport frame
        self.vp_card = ctk.CTkFrame(left_side, fg_color="#202020", corner_radius=12, border_width=1, border_color="#303030")
        self.vp_card.pack(fill="both", expand=True, pady=(0, 6))

        accent = self.settings.get("accent_color", "blue")
        self.viewport = GameViewport(self.vp_card, grid_width=20, grid_height=20, cell_size=15, accent_color=accent)
        self.viewport.pack(expand=True, pady=10)

        # Statistics HUD Frame
        hud = ctk.CTkFrame(left_side, fg_color="#202020", corner_radius=12, border_width=1, border_color="#303030")
        hud.pack(fill="x", pady=6)

        self.ep_lbl = self.hud_cell(hud, "Episode", "0 / 500", 0, 0)
        self.rew_lbl = self.hud_cell(hud, "Reward", "0.0", 0, 1)
        self.best_rew_lbl = self.hud_cell(hud, "Best Reward", "0.0", 0, 2)
        self.loss_lbl = self.hud_cell(hud, "Loss", "0.000", 0, 3)
        self.eps_lbl = self.hud_cell(hud, "Epsilon", "1.00", 1, 0)
        self.speed_lbl = self.hud_cell(hud, "Train Speed", "0 steps/s", 1, 1)
        self.mem_lbl = self.hud_cell(hud, "RAM Usage", "0 MB", 1, 2)
        self.time_lbl = self.hud_cell(hud, "Elapsed Time", "0s", 1, 3)

        hud.grid_columnconfigure((0,1,2,3), weight=1)

        # Right side: Interactive log feed & buttons card
        right_side = ctk.CTkFrame(mid_layout, fg_color="#202020", corner_radius=12, border_width=1, border_color="#303030", width=340)
        right_side.pack(side="right", fill="both", padx=(8, 0))
        right_side.pack_propagate(False)

        # Log feed
        ctk.CTkLabel(right_side, text="Live Training Logs", font=("Arial", 14, "bold")).pack(pady=8)
        self.log_txt = ctk.CTkTextbox(right_side, height=180, fg_color="#181818", border_width=1, border_color="#303030")
        self.log_txt.pack(fill="both", expand=True, padx=12, pady=4)

        # Training Controls
        ctrls_title = ctk.CTkLabel(right_side, text="Trainer Dashboard Controls", font=("Arial", 12, "bold"), text_color="gray70")
        ctrls_title.pack(pady=(12, 4))

        # Speed slider
        slider_row = ctk.CTkFrame(right_side, fg_color="transparent")
        slider_row.pack(fill="x", padx=15, pady=4)
        ctk.CTkLabel(slider_row, text="Step Delay:", font=("Arial", 11)).pack(side="left")
        self.slider_val_lbl = ctk.CTkLabel(slider_row, text="30ms", font=("Arial", 11, "bold"), text_color="cyan")
        self.slider_val_lbl.pack(side="right")
        self.speed_slider = ctk.CTkSlider(right_side, from_=0, to=150, command=self.change_speed)
        self.speed_slider.pack(fill="x", padx=15, pady=(0, 10))
        self.speed_slider.set(self.train_delay_ms)

        # Buttons Grid
        btn_grid = ctk.CTkFrame(right_side, fg_color="transparent")
        btn_grid.pack(fill="x", padx=10, pady=5)

        rocket_icon = get_icon("rocket", size=(16, 16))
        self.start_btn = ctk.CTkButton(btn_grid, text=" Train", image=rocket_icon, fg_color="#10B981", width=95, command=self.start_training)
        self.start_btn.grid(row=0, column=0, padx=4, pady=4)

        pause_icon = get_icon("pause", size=(16, 16))
        self.pause_btn = ctk.CTkButton(btn_grid, text=" Pause", image=pause_icon, fg_color="#F57C00", width=95, state="disabled", command=self.toggle_pause)
        self.pause_btn.grid(row=0, column=1, padx=4, pady=4)

        stop_icon = get_icon("stop", size=(16, 16))
        self.stop_btn = ctk.CTkButton(btn_grid, text=" Stop", image=stop_icon, fg_color="#D32F2F", width=95, state="disabled", command=self.stop_training)
        self.stop_btn.grid(row=0, column=2, padx=4, pady=4)

        refresh_icon = get_icon("refresh_color", size=(16, 16))
        self.reset_btn = ctk.CTkButton(btn_grid, text=" Reset", image=refresh_icon, fg_color="#1E3A8A", width=95, command=self.reset_training)
        self.reset_btn.grid(row=1, column=0, padx=4, pady=4)

        csv_icon = get_icon("csv", size=(16, 16))
        self.export_csv_btn = ctk.CTkButton(btn_grid, text=" CSV", image=csv_icon, fg_color="#0D9488", width=95, command=self.export_csv)
        self.export_csv_btn.grid(row=1, column=1, padx=4, pady=4)

        image_icon = get_icon("image", size=(16, 16))
        self.export_graph_btn = ctk.CTkButton(btn_grid, text=" Export Plot", image=image_icon, fg_color="#7B1FA2", width=95, command=self.export_graph)
        self.export_graph_btn.grid(row=1, column=2, padx=4, pady=4)

        play_btn_icon = get_icon("play_btn", size=(16, 16))
        self.play_best_btn = ctk.CTkButton(right_side, text=" Play Best AI Model", image=play_btn_icon, fg_color="#2563EB", command=self.play_best_ai)
        self.play_best_btn.pack(fill="x", padx=12, pady=4)

        video_icon = get_icon("video", size=(16, 16))
        self.replay_best_btn = ctk.CTkButton(right_side, text=" Replay Best Episode", image=video_icon, fg_color="#5B21B6", command=self.replay_best_episode)
        self.replay_best_btn.pack(fill="x", padx=12, pady=(4, 15))

        btn_grid.grid_columnconfigure((0,1,2), weight=1)

        # 3. Bottom Frame: tabbed matplotlib plots
        plots_card = ctk.CTkFrame(self, fg_color="#202020", corner_radius=12, border_width=1, border_color="#303030", height=240)
        plots_card.pack(fill="x", padx=15, pady=(5, 10))
        plots_card.pack_propagate(False)

        self.plot_tabs = ctk.CTkTabview(plots_card, fg_color="transparent")
        self.plot_tabs.pack(fill="both", expand=True, padx=10, pady=5)

        self.tab_reward = self.plot_tabs.add("Rewards & Moving Avg")
        self.tab_loss = self.plot_tabs.add("Model Loss")
        self.tab_epsilon = self.plot_tabs.add("Exploration Rate")
        self.tab_speed = self.plot_tabs.add("Training Performance")

        self.build_matplotlib_plots()

    def status_marker(self, parent, title, val, color="lightgreen"):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(side="right", padx=15, pady=10)
        ctk.CTkLabel(frame, text=title, font=("Arial", 11), text_color="gray70").pack(side="left", padx=4)
        lbl = ctk.CTkLabel(frame, text=val, font=("Arial", 13, "bold"), text_color=color)
        lbl.pack(side="left", padx=4)
        return lbl

    def hud_cell(self, parent, title, initial_val, r, c):
        cell = ctk.CTkFrame(parent, fg_color="transparent")
        cell.grid(row=r, column=c, padx=10, pady=4, sticky="w")
        ctk.CTkLabel(cell, text=title, font=("Arial", 11), text_color="gray60").pack(anchor="w")
        lbl = ctk.CTkLabel(cell, text=initial_val, font=("Arial", 14, "bold"), text_color="#FFFFFF")
        lbl.pack(anchor="w")
        return lbl

    def build_matplotlib_plots(self):
        # Setup Reward plot
        self.fig_reward = Figure(figsize=(8, 2.0), dpi=100, facecolor='#202020')
        self.ax_reward = self.fig_reward.add_subplot(111)
        self.style_axes(self.ax_reward, "Episode", "Score / Reward")
        self.canvas_reward = FigureCanvasTkAgg(self.fig_reward, master=self.tab_reward)
        self.canvas_reward.get_tk_widget().pack(fill="both", expand=True)

        # Setup Loss plot
        self.fig_loss = Figure(figsize=(8, 2.0), dpi=100, facecolor='#202020')
        self.ax_loss = self.fig_loss.add_subplot(111)
        self.style_axes(self.ax_loss, "Episode", "MSE Loss")
        self.canvas_loss = FigureCanvasTkAgg(self.fig_loss, master=self.tab_loss)
        self.canvas_loss.get_tk_widget().pack(fill="both", expand=True)

        # Setup Epsilon plot
        self.fig_epsilon = Figure(figsize=(8, 2.0), dpi=100, facecolor='#202020')
        self.ax_epsilon = self.fig_epsilon.add_subplot(111)
        self.style_axes(self.ax_epsilon, "Episode", "Epsilon Value")
        self.canvas_epsilon = FigureCanvasTkAgg(self.fig_epsilon, master=self.tab_epsilon)
        self.canvas_epsilon.get_tk_widget().pack(fill="both", expand=True)

        # Setup Speed plot
        self.fig_speed = Figure(figsize=(8, 2.0), dpi=100, facecolor='#202020')
        self.ax_speed = self.fig_speed.add_subplot(111)
        self.style_axes(self.ax_speed, "Episode", "Speed (steps/sec)")
        self.canvas_speed = FigureCanvasTkAgg(self.fig_speed, master=self.tab_speed)
        self.canvas_speed.get_tk_widget().pack(fill="both", expand=True)

    def style_axes(self, ax, xl, yl):
        ax.set_facecolor('#202020')
        ax.tick_params(colors='#CCCCCC', labelsize=8)
        ax.xaxis.label.set_color('#CCCCCC')
        ax.xaxis.label.set_size(9)
        ax.yaxis.label.set_color('#CCCCCC')
        ax.yaxis.label.set_size(9)
        ax.spines['bottom'].set_color('#3A3A3A')
        ax.spines['left'].set_color('#3A3A3A')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    # Controls Logic
    def change_speed(self, val):
        self.train_delay_ms = int(val)
        self.slider_val_lbl.configure(text=f"{self.train_delay_ms}ms")

    def start_training(self):
        if self.training:
            return
        
        self.update_active_game()
        
        self.training = True
        self.pause_event.clear()
        self.stop_event.clear()

        # Update button statuses
        self.start_btn.configure(state="disabled")
        self.pause_btn.configure(state="normal", text=" Pause", image=get_icon("pause", size=(16, 16)))
        self.stop_btn.configure(state="normal")
        self.status_lbl.configure(text="Training", text_color="orange")

        self.log_txt.insert("end", "🚀 Initiating DQN training loop...\n")

        self.start_time = time.time()

        # Gather hyperparams from settings/academy config entries (fallback to default)
        try:
            from app.pages.academy import AcademyPage
            # If configurations exist in settings/managers, load them
            lr = 0.001
            gamma = 0.99
            batch_size = 64
        except:
            lr, gamma, batch_size = 0.001, 0.99, 64

        threading.Thread(
            target=self.run_train_wrapper,
            args=(lr, gamma, batch_size),
            daemon=True
        ).start()

    def toggle_pause(self):
        if not self.training:
            return
        if self.pause_event.is_set():
            self.pause_event.clear()
            self.pause_btn.configure(text=" Pause", image=get_icon("pause", size=(16, 16)), fg_color="#F57C00")
            self.status_lbl.configure(text="Training", text_color="orange")
            self.log_txt.insert("end", "▶ Resumed training thread.\n")
        else:
            self.pause_event.set()
            self.pause_btn.configure(text=" Resume", image=get_icon("play_btn", size=(16, 16)), fg_color="#10B981")
            self.status_lbl.configure(text="Paused", text_color="yellow")
            self.log_txt.insert("end", "⏸ Paused training thread.\n")

    def stop_training(self):
        if not self.training:
            return
        self.stop_event.set()
        self.pause_event.clear()
        self.log_txt.insert("end", "⛔ Stop signal sent. Wrapping up...\n")

    def reset_training(self):
        if self.training:
            messagebox.showwarning("Warning", "Cannot reset while training is active.")
            return

        confirm = messagebox.askyesno("Reset AI", f"Are you sure you want to completely wipe {self.settings.get('username', 'Player1')}'s {self.game_info['name']} AI? This cannot be undone.")
        if not confirm:
            return

        username = self.settings.get("username", "Player1")
        model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "saved_models", username, f"best_dqn_model_{self.game_id}.pth"))
        meta_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "saved_models", username, f"best_dqn_model_{self.game_id}.json"))
        log_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "..", "training_logs", username, f"training_log_{self.game_id}.csv"
        ))
        leaderboard_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "saved_models", username, f"leaderboard_{self.game_id}.json"))
        
        try:
            if os.path.exists(model_path):
                os.remove(model_path)
            if os.path.exists(meta_path):
                os.remove(meta_path)
            if os.path.exists(log_path):
                os.remove(log_path)
            if os.path.exists(leaderboard_path):
                os.remove(leaderboard_path)
            self.log_txt.insert("end", f"🗑️ Wiped {username}'s AI model and logs for {self.game_info['name']} (0% Trained).\n")
        except Exception as e:
            self.log_txt.insert("end", f"❌ Error deleting model: {e}\n")
        self.episodes_list.clear()
        self.rewards_list.clear()
        self.losses_list.clear()
        self.epsilons_list.clear()
        self.speeds_list.clear()
        self.best_episode_steps.clear()
        
        # Clear plots
        self.ax_reward.clear(); self.style_axes(self.ax_reward, "Episode", "Score / Reward")
        self.ax_loss.clear(); self.style_axes(self.ax_loss, "Episode", "MSE Loss")
        self.ax_epsilon.clear(); self.style_axes(self.ax_epsilon, "Episode", "Epsilon Value")
        self.ax_speed.clear(); self.style_axes(self.ax_speed, "Episode", "Speed (steps/sec)")
        
        self.canvas_reward.draw_idle()
        self.canvas_loss.draw_idle()
        self.canvas_epsilon.draw_idle()
        self.canvas_speed.draw_idle()

        self.ep_lbl.configure(text="0 / 500")
        self.rew_lbl.configure(text="0.0")
        self.best_rew_lbl.configure(text="0.0")
        self.loss_lbl.configure(text="0.000")
        self.eps_lbl.configure(text="1.00")
        self.speed_lbl.configure(text="0 steps/s")
        self.mem_lbl.configure(text="0 MB")
        self.time_lbl.configure(text="0s")
        
        self.viewport.draw_empty("TRAINER RESET")
        self.log_txt.delete("1.0", "end")

    def run_train_wrapper(self, lr, gamma, batch_size):
        try:
            train(
                env_class=self.game_info["env_class"],
                state_size=self.game_info["state_size"],
                action_size=self.game_info["action_size"],
                game_id=self.game_id,
                callback=self.update_training_metrics,
                render_callback=self.step_render_callback if self.game_info["is_pygame"] else self.step_render_callback_snake,
                pause_event=self.pause_event,
                stop_event=self.stop_event,
                get_delay=lambda: self.train_delay_ms,
                lr=lr,
                gamma=gamma,
                batch_size=batch_size,
                episodes=500
            )
            self.after(0, lambda: self.training_ended("✅ Complete", "lightgreen"))
        except Exception as e:
            import traceback
            err = traceback.format_exc()
            print(err)
            self.after(0, lambda: self.training_ended("❌ Failed", "red", err))

    def step_render_callback_snake(self, snake_body, food_position, score):
        # Log to replay viewer if compiling the current best
        self.current_episode_steps.append((list(snake_body), food_position, score))

        # Perform live canvas draws only if delay is > 5 ms (CPU/UI pacing)
        if self.train_delay_ms >= 5:
            # Timing tracking
            self.episode_steps += 1
            now = time.perf_counter()
            if hasattr(self, "_last_step_time"):
                self.step_times.append(now - self._last_step_time)
            self._last_step_time = now

            self.after(0, lambda: self.viewport.draw_game(snake_body, food_position, score))
            
    def step_render_callback(self, surface):
        if self.train_delay_ms >= 5:
            self.episode_steps += 1
            now = time.perf_counter()
            if hasattr(self, "_last_step_time"):
                self.step_times.append(now - self._last_step_time)
            self._last_step_time = now

            snap = surface.copy()
            self.after(0, lambda: self.viewport.draw_surface(snap))

    def update_training_metrics(self, episode, total_episodes, progress, reward, best_reward, loss, epsilon):
        self.episodes_run = episode
        
        # Calculate training speed
        speed = 0
        if self.step_times:
            speed = 1.0 / (sum(self.step_times) / len(self.step_times))

        # Check memory
        try:
            import psutil
            mem = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
        except:
            mem = 0.0

        # Save lists
        self.episodes_list.append(episode)
        self.rewards_list.append(reward)
        self.losses_list.append(loss)
        self.epsilons_list.append(epsilon)
        self.speeds_list.append(speed)

        # Log check for best episode replay save
        if reward > self.best_reward:
            self.best_reward = reward
            self.best_episode_steps = self.current_episode_steps.copy()
            self.after(0, lambda: self.log_txt.insert("end", f"✨ New best episode: Ep {episode} | Score: {reward:.1f} saved to replay cache!\n"))
        self.current_episode_steps.clear()

        # Update HUD labels
        self.after(0, lambda: self.ep_lbl.configure(text=f"{episode} / {total_episodes}"))
        self.after(0, lambda: self.rew_lbl.configure(text=f"{reward:.1f}"))
        self.after(0, lambda: self.best_rew_lbl.configure(text=f"{best_reward:.1f}"))
        self.after(0, lambda: self.loss_lbl.configure(text=f"{loss:.4f}"))
        self.after(0, lambda: self.eps_lbl.configure(text=f"{epsilon:.3f}"))
        self.after(0, lambda: self.speed_lbl.configure(text=f"{speed:.1f} steps/s"))
        self.after(0, lambda: self.mem_lbl.configure(text=f"{mem:.1f} MB"))
        
        elapsed = int(time.time() - self.start_time)
        self.after(0, lambda: self.time_lbl.configure(text=f"{elapsed}s"))

        # Log row append
        self.after(0, lambda: self.log_txt.insert("end", f"Ep {episode} | Reward: {reward:.1f} | Loss: {loss:.4f} | Epsilon: {epsilon:.3f}\n"))
        self.after(0, self.log_txt.see, "end")

        # Live Graph Updates
        refresh_rate = self.settings.get("graph_refresh_rate", 1)
        if episode % refresh_rate == 0:
            self.after(0, self.redraw_plots)

    def redraw_plots(self):
        # 1. Rewards
        self.ax_reward.clear()
        self.style_axes(self.ax_reward, "Episode", "Score / Reward")
        self.ax_reward.plot(self.episodes_list, self.rewards_list, color='#10B981', linewidth=2)
        self.canvas_reward.draw_idle()

        # 2. Loss
        self.ax_loss.clear()
        self.style_axes(self.ax_loss, "Episode", "MSE Loss")
        self.ax_loss.plot(self.episodes_list, self.losses_list, color='#EF4444')
        self.canvas_loss.draw_idle()

        # 3. Epsilon
        self.ax_epsilon.clear()
        self.style_axes(self.ax_epsilon, "Episode", "Epsilon Value")
        self.ax_epsilon.plot(self.episodes_list, self.epsilons_list, color='#A855F7')
        self.canvas_epsilon.draw_idle()

        # 4. Performance Speed
        self.ax_speed.clear()
        self.style_axes(self.ax_speed, "Episode", "Speed (steps/sec)")
        self.ax_speed.plot(self.episodes_list, self.speeds_list, color='#F57C00')
        self.canvas_speed.draw_idle()

    def training_ended(self, message, color, error_msg=None):
        self.training = False
        self.status_lbl.configure(text=message, text_color=color)
        
        self.start_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled", text=" Pause", image=get_icon("pause", size=(16, 16)))
        self.stop_btn.configure(state="disabled")

        if error_msg:
            self.log_txt.insert("end", f"\n❌ TRAINING EXCEPTION DETECTED:\n{error_msg}\n")
        else:
            self.log_txt.insert("end", f"\n🎉 Training ended successfully. Final models written to directory.\n")
        self.log_txt.see("end")

        # Final redraw
        self.redraw_plots()

        # Refresh dashboard model marker
        self.settings.load()
        active = f"best_dqn_model_{self.game_id}.pth"
        self.model_lbl.configure(text=active)

    def export_csv(self):
        if not self.episodes_list:
            messagebox.showinfo("Export CSV", "No training data logged to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Export Training Metrics"
        )
        if not file_path:
            return

        try:
            df = pd.DataFrame({
                "Episode": self.episodes_list,
                "Reward": self.rewards_list,
                "Loss": self.losses_list,
                "Epsilon": self.epsilons_list,
                "Speed_steps_sec": self.speeds_list
            })
            df.to_csv(file_path, index=False)
            messagebox.showinfo("Success", f"CSV metrics exported to: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not write CSV: {e}")

    def export_graph(self):
        if not self.episodes_list:
            messagebox.showinfo("Export Plot", "No data to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Images", "*.png"), ("PDF Documents", "*.pdf")],
            title="Export Performance Plot"
        )
        if not file_path:
            return

        try:
            # Export the active visible plot figure
            active_tab = self.plot_tabs.get()
            if active_tab == "Rewards & Moving Avg":
                self.fig_reward.savefig(file_path, bbox_inches='tight')
            elif active_tab == "Model Loss":
                self.fig_loss.savefig(file_path, bbox_inches='tight')
            elif active_tab == "Exploration Rate":
                self.fig_epsilon.savefig(file_path, bbox_inches='tight')
            elif active_tab == "Training Performance":
                self.fig_speed.savefig(file_path, bbox_inches='tight')

            messagebox.showinfo("Success", f"Plot successfully saved to: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save graph: {e}")

    def play_best_ai(self):
        # Seamlessly switch to PlayPage and load the AI view
        app = self.winfo_toplevel()
        if hasattr(app, "show_page"):
            app.show_page("play")
            play_page = app.pages["play"]
            play_page.show_view("ai", self.game_id)

    def replay_best_episode(self):
        if not self.best_episode_steps:
            messagebox.showinfo("Replay Best", "No best episode recorded yet in this session.")
            return

        if self.training:
            messagebox.showwarning("Warning", "Cannot run replay while model training is active.")
            return

        self.log_txt.insert("end", f"🎬 Running replay of best episode ({len(self.best_episode_steps)} steps)...\n")
        self.log_txt.see("end")

        # Disable buttons during playback
        self.replay_best_btn.configure(state="disabled")
        
        # Sequentially draw frames using recursive after callbacks
        self.play_replay_step(0)

    def play_replay_step(self, step_idx):
        if self.game_info["is_pygame"]:
            self.log_txt.insert("end", "Replay not fully supported for PyGame Envs yet.\n")
            self.replay_best_btn.configure(state="normal")
            return
            
        if step_idx >= len(self.best_episode_steps):
            self.viewport.draw_game(self.best_episode_steps[-1][0], self.best_episode_steps[-1][1], self.best_episode_steps[-1][2], overlay_text="REPLAY ENDED")
            self.replay_best_btn.configure(state="normal")
            return

        body, food, score = self.best_episode_steps[step_idx]
        self.viewport.draw_game(body, food, score)

        # 60ms step playback interval
        self.after(60, lambda: self.play_replay_step(step_idx + 1))