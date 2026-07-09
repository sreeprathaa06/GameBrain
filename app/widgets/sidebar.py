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

        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(pady=(25, 40))

        ctk.CTkLabel(
            title_frame,
            text="🎮 ",
            font=("Arial", 24, "bold"),
            text_color="#00E5FF"
        ).pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text="GameBrain",
            font=("Arial", 24, "bold"),
            text_color="white"
        ).pack(side="left")

        menu_items = [
            ("🏠", " Home", "home", "#4ADE80"),
            ("🎮", " Play Games", "play", "#60A5FA"),
            ("🧠", " AI Academy", "academy", "#F472B6"),
            ("📊", " Dashboard", "dashboard", "#FBBF24"),
            ("🏆", " Leaderboard", "leaderboard", "#FB923C"),
            ("⚙", " Settings", "settings", "#94A3B8")
        ]

        self.buttons = {}
        self.active_page = "home"

        for emoji, text, page, color in menu_items:
            btn = ctk.CTkFrame(self, fg_color="transparent", height=40, width=180, corner_radius=8)
            btn.pack_propagate(False)
            btn.pack(pady=8)
            
            lbl_e = ctk.CTkLabel(btn, text=emoji, font=("Arial", 18), text_color=color)
            lbl_e.pack(side="left", padx=(15, 5))
            
            lbl_t = ctk.CTkLabel(btn, text=text, font=("Arial", 16, "bold"), text_color="white")
            lbl_t.pack(side="left")
            
            self.buttons[page] = btn

            # Hover effects and click
            def on_enter(e, p=page):
                if self.active_page != p:
                    self.buttons[p].configure(fg_color="#2A2A2A")
                    
            def on_leave(e, p=page):
                if self.active_page != p:
                    self.buttons[p].configure(fg_color="transparent")
                    
            def on_click(e, p=page):
                self.set_active(p)
                self.callback(p)
            
            for w in (btn, lbl_e, lbl_t):
                w.bind("<Enter>", on_enter)
                w.bind("<Leave>", on_leave)
                w.bind("<Button-1>", on_click)
                w.configure(cursor="hand2")

        # Set initial active state
        self.set_active("home")

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

    def set_active(self, page):
        self.active_page = page
        for p, btn in self.buttons.items():
            if p == page:
                btn.configure(fg_color="#1F6AA5")
            else:
                btn.configure(fg_color="transparent")