import customtkinter as ctk
from utils.settings_manager import SettingsManager
from utils.leaderboard_manager import LeaderboardManager

class HomePage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.settings_mgr = SettingsManager()
        
        # We will hold references to our main UI containers
        self.main_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        self.initialize_state()

    def clear_container(self):
        for child in self.main_container.winfo_children():
            child.destroy()

    def initialize_state(self):
        username = self.settings_mgr.get("username", "")
        if not username:
            self.show_state_a()
        else:
            self.show_state_b(username)

    # ==========================================
    # STATE A: Onboarding (New User)
    # ==========================================
    def show_state_a(self):
        self.clear_container()
        
        # Clean Hero
        hero = ctk.CTkFrame(self.main_container, fg_color=("gray95", "#1E1E1E"), corner_radius=15, border_width=1, border_color=("gray85", "#2E2E2E"))
        hero.pack(fill="x", padx=40, pady=(40, 20))
        
        ctk.CTkLabel(
            hero, 
            text="Welcome to GameBrain", 
            font=("Arial", 40, "bold"),
            text_color=("#005B96", "cyan")
        ).pack(pady=(50, 15))
        
        ctk.CTkLabel(
            hero, 
            text="The ultimate AI sandbox for visualizing, training, and dueling Reinforcement Learning models.", 
            font=("Arial", 18),
            text_color=("gray20", "gray70")
        ).pack(pady=(0, 40))

        # Onboarding Form (Centered)
        form_container = ctk.CTkFrame(self.main_container, fg_color=("gray90", "#222222"), corner_radius=15, border_width=1, border_color=("gray80", "#333333"), width=600)
        form_container.pack(pady=20, padx=40)
        
        ctk.CTkLabel(form_container, text="👤 Tell us about yourself to get started", font=("Arial", 22, "bold"), text_color="cyan").pack(pady=(30, 20))
        
        form_grid = ctk.CTkFrame(form_container, fg_color="transparent")
        form_grid.pack(pady=10)
        
        # Name
        ctk.CTkLabel(form_grid, text="Name:", font=("Arial", 15, "bold")).grid(row=0, column=0, sticky="e", padx=15, pady=15)
        name_entry = ctk.CTkEntry(form_grid, width=280, font=("Arial", 15), height=35)
        name_entry.grid(row=0, column=1, padx=15, pady=15)
        name_entry.insert(0, self.settings_mgr.get("username", ""))
        
        # Age
        ctk.CTkLabel(form_grid, text="Age:", font=("Arial", 15, "bold")).grid(row=1, column=0, sticky="e", padx=15, pady=15)
        age_entry = ctk.CTkEntry(form_grid, width=280, font=("Arial", 15), height=35)
        age_entry.grid(row=1, column=1, padx=15, pady=15)
        age_entry.insert(0, self.settings_mgr.get("age", ""))
        
        # Experience
        ctk.CTkLabel(form_grid, text="AI Experience:", font=("Arial", 15, "bold")).grid(row=2, column=0, sticky="e", padx=15, pady=15)
        exp_combo = ctk.CTkComboBox(form_grid, values=["Beginner", "Intermediate", "Expert"], width=280, font=("Arial", 15), height=35)
        exp_combo.grid(row=2, column=1, padx=15, pady=15)
        exp_combo.set(self.settings_mgr.get("experience", "Beginner"))
        
        def save_profile():
            name = name_entry.get().strip()
            age = age_entry.get().strip()
            exp = exp_combo.get()
            
            if name:
                self.settings_mgr.set("username", name)
                self.settings_mgr.set("age", age)
                self.settings_mgr.set("experience", exp)
                self.show_state_b(name)
                
        ctk.CTkButton(form_container, text="Save & Enter Sandbox ➔", font=("Arial", 16, "bold"), fg_color="#10B981", hover_color="#059669", height=50, width=250, command=save_profile).pack(pady=(25, 35))

    # ==========================================
    # STATE B: Main Dashboard (Onboarded User)
    # ==========================================
    def show_state_b(self, username):
        self.clear_container()
        
        # Personalized Hero
        hero = ctk.CTkFrame(self.main_container, fg_color=("gray95", "#1E1E1E"), corner_radius=15, border_width=1, border_color=("gray85", "#2E2E2E"))
        hero.pack(fill="x", padx=40, pady=(40, 20))
        
        ctk.CTkLabel(
            hero, 
            text=f"Hey {username}! Welcome back.", 
            font=("Arial", 38, "bold"),
            text_color=("#005B96", "cyan")
        ).pack(pady=(45, 10))
        
        ctk.CTkLabel(
            hero, 
            text="Let's build, train, and duel some Reinforcement Learning models.", 
            font=("Arial", 18),
            text_color=("gray20", "gray70")
        ).pack(pady=(0, 45))
        
        # Model Readiness Section
        readiness_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        readiness_frame.pack(fill="x", padx=40, pady=10)
        
        ctk.CTkLabel(readiness_frame, text="🧠 Model Readiness", font=("Arial", 24, "bold"), text_color=("gray20", "gray80")).pack(anchor="w", pady=(0, 15))
        
        models_grid = ctk.CTkFrame(readiness_frame, fg_color=("gray90", "#222222"), corner_radius=15, border_width=1, border_color=("gray80", "#333333"))
        models_grid.pack(fill="x")
        
        games = [
            ("🐍 Snake", "snake", "#10B981"),
            ("🐦 Flappy Bird", "flappy_bird", "#F57C00"),
            ("🏓 Ping Pong", "ping_pong", "#3B82F6")
        ]
        
        for name, g_id, color in games:
            row = ctk.CTkFrame(models_grid, fg_color="transparent")
            row.pack(fill="x", padx=30, pady=15)
            
            ctk.CTkLabel(row, text=name, font=("Arial", 18, "bold"), width=160, anchor="w").pack(side="left")
            
            progress = LeaderboardManager.get_training_progress(g_id)
            
            bar = ctk.CTkProgressBar(row, progress_color=color, height=14)
            bar.pack(side="left", fill="x", expand=True, padx=20)
            bar.set(progress / 100.0)
            
            ctk.CTkLabel(row, text=f"{progress}% Trained", font=("Arial", 16, "bold"), width=120, anchor="e").pack(side="right")
            
        # Button row for Edit Profile and Sign Out
        btn_row = ctk.CTkFrame(readiness_frame, fg_color="transparent")
        btn_row.pack(anchor="e", pady=(10, 0))

        edit_btn = ctk.CTkButton(
            btn_row, 
            text="✏️ Edit Profile Details", 
            font=("Arial", 13, "bold"), 
            fg_color="transparent", 
            text_color="gray50", 
            hover_color="#303030", 
            width=150, 
            height=30, 
            command=self.show_state_a
        )
        edit_btn.pack(side="left", padx=5)

        def sign_out():
            self.settings_mgr.set("username", "")
            self.settings_mgr.set("age", "")
            self.show_state_a()

        signout_btn = ctk.CTkButton(
            btn_row, 
            text="🚪 Sign Out", 
            font=("Arial", 13, "bold"), 
            fg_color="transparent", 
            text_color="#E11D48", 
            hover_color="#303030", 
            width=100, 
            height=30, 
            command=sign_out
        )
        signout_btn.pack(side="left", padx=5)

        # Quick Actions (At the very bottom)
        actions = ctk.CTkFrame(self.main_container, fg_color="transparent")
        actions.pack(fill="x", padx=40, pady=10)
        
        ctk.CTkLabel(actions, text="Quick Actions", font=("Arial", 22, "bold"), text_color=("gray20", "gray80")).pack(pady=(5, 10))
        
        btn_frame = ctk.CTkFrame(actions, fg_color="transparent")
        btn_frame.pack()
        
        app = self.winfo_toplevel()
        
        def nav(page):
            if hasattr(app, "show_page"):
                app.show_page(page)
                
        ctk.CTkButton(btn_frame, text="🚀 Start Training", fg_color="#F97316", font=("Arial", 16, "bold"), height=50, width=180, command=lambda: nav("ai_training")).pack(side="left", padx=15)
        ctk.CTkButton(btn_frame, text="📊 View Dashboard", fg_color="#8B5CF6", font=("Arial", 16, "bold"), height=50, width=180, command=lambda: nav("dashboard")).pack(side="left", padx=15)
        ctk.CTkButton(btn_frame, text="🎮 Play Games", fg_color="#10B981", font=("Arial", 16, "bold"), height=50, width=180, command=lambda: nav("play")).pack(side="left", padx=15)