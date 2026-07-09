"""
=========================================================
GameBrain

Sidebar Widget

Author : Team GameBrain
=========================================================
"""

import customtkinter as ctk


class Sidebar(ctk.CTkFrame):

    def __init__(self, parent, callback):

        super().__init__(
            parent,
            width=220,
            corner_radius=0
        )

        self.callback = callback

        self.pack_propagate(False)

        self.create_widgets()

    def create_widgets(self):

        title = ctk.CTkLabel(
            self,
            text="🎮 GameBrain",
            font=("Arial", 24, "bold")
        )

        title.pack(pady=(25, 40))

        menu_items = [

            ("🏠 Home", "home"),

            ("🎮 Play Games", "play"),

            ("🧠 AI Academy", "academy"),

            ("📊 Dashboard", "dashboard"),

            ("🏆 Leaderboard", "leaderboard"),

            ("⚙ Settings", "settings")

        ]

        for text, page in menu_items:

            btn = ctk.CTkButton(

                self,

                text=text,

                width=180,

                height=40,

                font=("Arial", 16),

                command=lambda p=page: self.callback(p)

            )

            btn.pack(pady=8)

        ctk.CTkLabel(
            self,
            text="",
        ).pack(expand=True)

        exit_btn = ctk.CTkButton(

            self,

            text="❌ Exit",

            fg_color="#B22222",

            hover_color="#8B0000",

            command=self.master.destroy

        )

        exit_btn.pack(pady=20)