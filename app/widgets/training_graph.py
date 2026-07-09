"""
=========================================================
GameBrain

Live Training Graph

=========================================================
"""

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class TrainingGraph(ctk.CTkFrame):

    def __init__(self, parent):

        super().__init__(parent)

        self.rewards = []
        self.losses = []

        # -----------------------------
        # Figure
        # -----------------------------

        self.figure = Figure(
            figsize=(8, 3.8),
            dpi=100
        )

        self.ax = self.figure.add_subplot(111)

        self.ax.set_title("Training Progress")
        self.ax.set_xlabel("Episode")
        self.ax.set_ylabel("Value")

        self.ax.grid(True)

        self.reward_line, = self.ax.plot(
            [],
            [],
            color="green",
            linewidth=2,
            label="Reward"
        )

        self.loss_line, = self.ax.plot(
            [],
            [],
            color="red",
            linewidth=2,
            label="Loss"
        )

        self.ax.legend()

        self.canvas = FigureCanvasTkAgg(
            self.figure,
            master=self
        )

        self.canvas.draw()

        self.canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

    # ===================================================

    def update_graph(self, reward, loss):

        self.rewards.append(reward)
        self.losses.append(loss)

        episodes = list(range(1, len(self.rewards) + 1))

        self.reward_line.set_data(
            episodes,
            self.rewards
        )

        self.loss_line.set_data(
            episodes,
            self.losses
        )

        self.ax.relim()
        self.ax.autoscale_view()

        self.canvas.draw_idle()

    # ===================================================

    def reset(self):

        self.rewards.clear()
        self.losses.clear()

        self.reward_line.set_data([], [])
        self.loss_line.set_data([], [])

        self.ax.relim()
        self.ax.autoscale_view()

        self.canvas.draw_idle()