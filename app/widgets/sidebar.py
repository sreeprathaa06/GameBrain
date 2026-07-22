"""
=========================================================
GameBrain

Sidebar Widget

Author : Team GameBrain
=========================================================
"""

import customtkinter as ctk
from app.utils.icon_loader import get_icon

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

        # Title Logo
        title_icon = get_icon("app_icon", size=(32, 32))
        self.title_label = ctk.CTkLabel(
            title_frame,
            text="" if title_icon else "🎮 ",
            image=title_icon,
            font=("Arial", 24, "bold"),
            text_color=("#007B8F", "#00E5FF")
        ).pack(side="left", padx=(0, 5))

        ctk.CTkLabel(
            title_frame,
            text="GameBrain",
            font=("Arial", 24, "bold"),
            text_color=("black", "white")
        ).pack(side="left")

        menu_items = [
            ("home_color", " Home", "home", "#4ADE80"),
            ("game_color", " Play Games", "play", "#60A5FA"),
            ("brain_color", " AI Academy", "academy", "#F472B6"),
            ("dashboard_color", " Dashboard", "dashboard", "#FBBF24"),
            ("trophy_color", " Leaderboard", "leaderboard", "#FB923C"),
            ("settings_color", " Settings", "settings", "#94A3B8")
        ]

        self.buttons = {}
        self.active_page = "home"

        for icon_name, text, page, color in menu_items:
            btn = ctk.CTkFrame(self, fg_color="transparent", height=40, width=180, corner_radius=8)
            btn.pack_propagate(False)
            btn.pack(pady=8)
            
            icon_img = get_icon(icon_name, size=(24, 24))
            lbl_e = ctk.CTkLabel(btn, text="" if icon_img else icon_name, image=icon_img, text_color=color)
            lbl_e.pack(side="left", padx=(15, 5))
            
            lbl_t = ctk.CTkLabel(btn, text=text, font=("Arial", 16, "bold"), text_color=("black", "white"))
            lbl_t.pack(side="left")
            
            self.buttons[page] = btn

            # Hover effects and click
            def on_enter(e, p=page):
                if self.active_page != p:
                    self.buttons[p].configure(fg_color=("gray80", "#2A2A2A"))
                    
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

        exit_icon = get_icon("close", size=(20, 20))
        exit_btn = ctk.CTkButton(
            self,
            text=" Exit",
            image=exit_icon,
            fg_color=("#991B1B", "#B22222"),
            hover_color="#8B0000",
            command=self.master.destroy
        )
        exit_btn.pack(pady=20)

    def set_active(self, page):
        self.active_page = page
        for p, btn in self.buttons.items():
            if p == page:
                btn.configure(fg_color=("#1E40AF", "#1F6AA5"))
            else:
                btn.configure(fg_color="transparent")