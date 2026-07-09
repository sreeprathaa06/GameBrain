import customtkinter as ctk
from app.utils.leaderboard_manager import LeaderboardManager
from app.utils.settings_manager import SettingsManager
from app.pages.play import GAME_REGISTRY

class LeaderboardView(ctk.CTkFrame):
    def __init__(self, parent, game_id, back_callback):
        super().__init__(parent, fg_color="transparent")
        self.game_id = game_id
        self.back_callback = back_callback
        self.manager = LeaderboardManager(game_id)

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))
        
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
        title = ctk.CTkLabel(
            header_frame,
            text=f"🏆 Hall of Fame - {game_info['name']}",
            font=("Arial", 30, "bold")
        )
        title.pack(side="left", padx=20)

        self.tabs = ctk.CTkTabview(self, fg_color=("gray95", "#202020"), corner_radius=15)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=10)

        self.scores_tab = self.tabs.add("📊 High Records")
        self.ach_tab = self.tabs.add("🏆 Achievements & Badges")
        self.recent_tab = self.tabs.add("⏱ Recent History")

        self.build_scores_tab()
        self.build_ach_tab()
        self.build_recent_tab()

    def build_scores_tab(self):
        data = self.manager.get_data()

        grid = ctk.CTkFrame(self.scores_tab, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=15, pady=15)

        cards = [
            ("👤 Highest Human Score", str(data.get("highest_human_score", 0)), ("#005B96", "cyan")),
            ("🤖 Highest AI Score", str(data.get("highest_ai_score", 0)), ("purple", "#B39DDB")),
            ("📈 Best Training Reward", f"{data.get('best_training_reward', 0.0):.2f}", ("#006400", "green")),
            ("⏱ Fastest Training (500 ep)", f"{data.get('fastest_training_time_sec', 0.0):.1f}s" if data.get('fastest_training_time_sec', 0.0) > 0 else "N/A", ("#D97706", "orange")),
            ("🐍 Longest Survival", f"{data.get('longest_survival_steps', 0)} steps", ("#1E3A8A", "blue")),
            ("🍎 Total Apples/Score Harvested", str(data.get("most_apples_single_game", 0)), ("#005B96", "cyan"))
        ]

        for i, (title, value, color) in enumerate(cards):
            row = i // 3
            col = i % 3

            card = ctk.CTkFrame(grid, fg_color=("gray90", "#282828"), border_width=1, border_color=("gray85", "#3A3A3A"), corner_radius=12)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            ctk.CTkLabel(card, text=title, font=("Arial", 14, "bold"), text_color=("gray30", "gray80")).pack(pady=(15, 5), padx=10)
            ctk.CTkLabel(card, text=value, font=("Arial", 26, "bold"), text_color=color).pack(pady=(0, 15), padx=10)

        for r in range(2):
            grid.rowconfigure(r, weight=1)
        for c in range(3):
            grid.columnconfigure(c, weight=1)

    def build_ach_tab(self):
        data = self.manager.get_data()
        achs = data.get("achievements", {})

        scroll = ctk.CTkScrollableFrame(self.ach_tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=15)

        for ach_id, item in achs.items():
            unlocked = item.get("unlocked", False)
            title = item.get("title", "Locked Achievement")
            desc = item.get("desc", "")

            color = ("#059669", "#10B981") if unlocked else ("gray50", "#4B5563")
            bg = ("white", "#2A2A2A") if unlocked else ("gray95", "#232323")
            border = ("#059669", "#10B981") if unlocked else ("gray85", "#3A3A3A")

            item_frame = ctk.CTkFrame(scroll, fg_color=bg, border_width=1, border_color=border, corner_radius=10)
            item_frame.pack(fill="x", pady=6, padx=5)

            badge = ctk.CTkLabel(
                item_frame,
                text=" 🏆 " if unlocked else " 🔒 ",
                font=("Arial", 22),
                text_color=color
            )
            badge.pack(side="left", padx=15, pady=10)

            details = ctk.CTkFrame(item_frame, fg_color="transparent")
            details.pack(side="left", fill="both", expand=True, pady=8)

            lbl_title = ctk.CTkLabel(details, text=title, font=("Arial", 14, "bold"), text_color=("black", "#FFFFFF") if unlocked else ("gray40", "gray60"))
            lbl_title.pack(anchor="w")

            lbl_desc = ctk.CTkLabel(details, text=desc, font=("Arial", 12), text_color=("gray40", "gray70") if unlocked else ("gray60", "gray50"))
            lbl_desc.pack(anchor="w")

            status = ctk.CTkLabel(
                item_frame,
                text="UNLOCKED" if unlocked else "LOCKED",
                font=("Arial", 10, "bold"),
                text_color=color,
                width=80
            )
            status.pack(side="right", padx=15)

    def build_recent_tab(self):
        data = self.manager.get_data()
        sessions = data.get("recent_sessions", [])

        scroll = ctk.CTkScrollableFrame(self.recent_tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=15)

        if not sessions:
            lbl = ctk.CTkLabel(scroll, text="No recent gaming sessions logged yet.", font=("Arial", 14), text_color=("gray40", "gray50"))
            lbl.pack(pady=40)
            return

        header = ctk.CTkFrame(scroll, fg_color=("gray85", "#2A2A2A"), height=35)
        header.pack(fill="x", pady=2)
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="Mode", font=("Arial", 12, "bold"), width=150, anchor="w").pack(side="left", padx=15)
        ctk.CTkLabel(header, text="Score", font=("Arial", 12, "bold"), width=150, anchor="center").pack(side="left", padx=15)
        ctk.CTkLabel(header, text="Steps Survived", font=("Arial", 12, "bold"), width=120, anchor="center").pack(side="left", padx=15)
        ctk.CTkLabel(header, text="Date & Time", font=("Arial", 12, "bold"), width=150, anchor="e").pack(side="right", padx=15)

        for s in sessions:
            row = ctk.CTkFrame(scroll, fg_color=("gray95", "#232323"), height=38)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            mode = s.get("mode", "Human")
            icon = "👤" if mode == "Human" else "🤖" if mode == "AI" else "⚔"
            
            ctk.CTkLabel(row, text=f"{icon} {mode}", font=("Arial", 12), width=150, anchor="w").pack(side="left", padx=15)
            ctk.CTkLabel(row, text=str(s.get("score", 0)), font=("Arial", 12, "bold"), text_color=("#D97706", "orange"), width=150, anchor="center").pack(side="left", padx=15)
            ctk.CTkLabel(row, text=str(s.get("survival_steps", 0)), font=("Arial", 12), width=120, anchor="center").pack(side="left", padx=15)
            ctk.CTkLabel(row, text=s.get("date", "N/A"), font=("Arial", 11), text_color=("gray40", "gray60"), width=150, anchor="e").pack(side="right", padx=15)

    def refresh_leaderboard(self):
        self.manager.load()
        for child in self.scores_tab.winfo_children(): child.destroy()
        for child in self.ach_tab.winfo_children(): child.destroy()
        for child in self.recent_tab.winfo_children(): child.destroy()
        self.build_scores_tab()
        self.build_ach_tab()
        self.build_recent_tab()


class LeaderboardPage(ctk.CTkFrame):
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
        title = ctk.CTkLabel(
            self.scroll_canvas,
            text="🏆 Choose Leaderboard",
            font=("Arial", 34, "bold")
        )
        title.pack(pady=(20, 5))

        subtitle = ctk.CTkLabel(
            self.scroll_canvas,
            text="Select a game to view its high scores, history, and achievements",
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
            
            emoji, rest_of_title = info["name"].split(" ", 1)
            
            ctk.CTkLabel(
                title_frame,
                text=emoji + " ",
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

            ctk.CTkButton(
                right,
                text="🏅 View Leaderboard",
                width=180,
                height=45,
                fg_color="#D97706",
                hover_color="#B45309",
                corner_radius=12,
                font=("Arial", 14, "bold"),
                command=lambda gid=game_id: self.show_view(gid)
            ).pack(pady=6)

    def show_view(self, game_id):
        self.settings.set("active_game", game_id)
        
        self.menu_frame.pack_forget()

        if self.current_view:
            self.current_view.destroy()

        self.current_view = LeaderboardView(self, game_id, self.show_menu)
        self.current_view.pack(fill="both", expand=True)

    def show_menu(self):
        if self.current_view:
            self.current_view.destroy()
            self.current_view = None
        self.menu_frame.pack(fill="both", expand=True)