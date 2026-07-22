import customtkinter as ctk
from app.utils.icon_loader import get_icon
from app.utils.settings_manager import SettingsManager
from app.utils.leaderboard_manager import LeaderboardManager

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

    def on_show(self):
        self.initialize_state()

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
        ).pack(pady=(30, 10))
        
        ctk.CTkLabel(
            hero, 
            text="Please select a profile or create a new one to continue.", 
            font=("Arial", 18),
            text_color=("gray20", "gray70")
        ).pack(pady=(0, 30))

        # Split into two columns for New vs Existing
        columns_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        columns_frame.pack(fill="both", expand=True, padx=40, pady=10)
        columns_frame.grid_columnconfigure((0, 1), weight=1)

        # ---- Existing User Card ----
        existing_card = ctk.CTkFrame(columns_frame, fg_color=("gray90", "#222222"), corner_radius=15, border_width=1, border_color=("gray80", "#333333"))
        existing_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(existing_card, text="🔑 Existing User", font=("Arial", 22, "bold"), text_color=("#059669", "#10B981")).pack(pady=(25, 15))
        
        # Scan for existing users in saved_models directory
        import os
        saved_models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "saved_models"))
        existing_users = []
        if os.path.exists(saved_models_dir):
            existing_users = [d for d in os.listdir(saved_models_dir) if os.path.isdir(os.path.join(saved_models_dir, d))]
        
        if not existing_users:
            existing_users = ["No existing users found"]
            
        user_combo = ctk.CTkComboBox(existing_card, values=existing_users, width=220, font=("Arial", 15), height=35)
        user_combo.pack(pady=15)
        
        login_pass_entry = ctk.CTkEntry(existing_card, placeholder_text="Enter password...", show="*", width=220, font=("Arial", 15), height=35)
        login_pass_entry.pack(pady=(0, 15))
        
        def login_existing():
            name = user_combo.get().strip()
            password = login_pass_entry.get()
            if not name or name == "No existing users found":
                from tkinter import messagebox
                messagebox.showwarning("Invalid Selection", "Please select a valid user.")
                return
            
            # Ensure the typed name actually exists in the system
            if not os.path.exists(os.path.join(saved_models_dir, name)):
                from tkinter import messagebox
                messagebox.showerror("User Not Found", f"The user '{name}' does not exist. Please create a New User instead.")
                return

            # Check password
            auth_file = os.path.join(saved_models_dir, name, "auth.json")
            if os.path.exists(auth_file):
                try:
                    import json, hashlib
                    with open(auth_file, "r") as f:
                        auth_data = json.load(f)
                    
                    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
                    if hashed_pw != auth_data.get("password_hash"):
                        from tkinter import messagebox
                        messagebox.showerror("Authentication Failed", "Incorrect password.")
                        return
                except Exception as e:
                    print(f"Auth error: {e}")

            self.settings_mgr.set("username", name)
            app = self.winfo_toplevel()
            if hasattr(app, "toggle_sidebar"):
                app.toggle_sidebar(True)
            self.show_state_b(name)

        ctk.CTkButton(existing_card, text="Log In ➔", font=("Arial", 16, "bold"), fg_color=("#059669", "#10B981"), hover_color="#059669", height=40, width=180, command=login_existing).pack(pady=(15, 5))

        def forgot_password():
            name = user_combo.get().strip()
            if not name or name == "No existing users found":
                from tkinter import messagebox
                messagebox.showwarning("Select User", "Please select a user first.")
                return
            
            auth_file = os.path.join(saved_models_dir, name, "auth.json")
            if not os.path.exists(auth_file):
                from tkinter import messagebox
                messagebox.showinfo("No Password", f"'{name}' does not have a password set.")
                return
                
            # Create a nice custom top-level dialog
            dialog = ctk.CTkToplevel()
            dialog.title("Reset Password")
            dialog.geometry("450x280")
            dialog.attributes("-topmost", True)
            dialog.resizable(False, False)
            
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() - 450) // 2
            y = (dialog.winfo_screenheight() - 280) // 2
            dialog.geometry(f"+{x}+{y}")
            
            ctk.CTkLabel(dialog, text=f"Reset Password for '{name}'", font=("Arial", 22, "bold"), text_color=("#005B96", "cyan")).pack(pady=(25, 10))
            ctk.CTkLabel(dialog, text="Please enter your new password below:", font=("Arial", 14)).pack(pady=(0, 15))
            
            pwd_entry = ctk.CTkEntry(dialog, show="*", width=300, height=40, font=("Arial", 15), placeholder_text="New Password...")
            pwd_entry.pack(pady=10)
            
            def submit():
                new_pass = pwd_entry.get()
                if new_pass:
                    try:
                        import json, hashlib
                        hashed_pw = hashlib.sha256(new_pass.encode()).hexdigest()
                        with open(auth_file, "w") as f:
                            json.dump({"password_hash": hashed_pw}, f)
                        from tkinter import messagebox
                        messagebox.showinfo("Success", "Password reset successfully! You can now log in.")
                        dialog.destroy()
                    except Exception as e:
                        from tkinter import messagebox
                        messagebox.showerror("Error", f"Failed to reset password: {e}")
                else:
                    from tkinter import messagebox
                    messagebox.showwarning("Missing", "Please enter a password.")

            ctk.CTkButton(dialog, text="Reset Password", font=("Arial", 16, "bold"), fg_color=("#2563EB", "#3B82F6"), height=45, width=200, command=submit).pack(pady=20)

        forgot_btn = ctk.CTkButton(existing_card, text="Forgot Password?", font=("Arial", 12, "underline"), text_color=("#2563EB", "#3B82F6"), fg_color="transparent", hover_color=("gray85", "#333333"), height=20, command=forgot_password)
        forgot_btn.pack(pady=(0, 15))

        # ---- New User Card ----
        new_card = ctk.CTkFrame(columns_frame, fg_color=("gray90", "#222222"), corner_radius=15, border_width=1, border_color=("gray80", "#333333"))
        new_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        ctk.CTkLabel(new_card, text="✨ New User", font=("Arial", 22, "bold"), text_color=("#005B96", "cyan")).pack(pady=(25, 15))
        
        name_entry = ctk.CTkEntry(new_card, placeholder_text="Enter new username...", width=220, font=("Arial", 15), height=35)
        name_entry.pack(pady=15)
        
        new_pass_entry = ctk.CTkEntry(new_card, placeholder_text="Create password...", show="*", width=220, font=("Arial", 15), height=35)
        new_pass_entry.pack(pady=(0, 15))
        
        def create_new():
            name = name_entry.get().strip()
            password = new_pass_entry.get()
            if not name or not password:
                from tkinter import messagebox
                messagebox.showwarning("Missing Info", "Please enter both username and password.")
                return
            
            user_dir = os.path.join(saved_models_dir, name)
            
            # Validation for duplicate using exact file system check
            if os.path.exists(user_dir):
                from tkinter import messagebox
                messagebox.showerror("Already Exists", f"The username '{name}' already exists! Please log in instead, or choose a different name.")
                return
                
            # Actually create the directory right now so they are registered!
            os.makedirs(user_dir, exist_ok=True)
            
            # Save password
            import json, hashlib
            hashed_pw = hashlib.sha256(password.encode()).hexdigest()
            with open(os.path.join(user_dir, "auth.json"), "w") as f:
                json.dump({"password_hash": hashed_pw}, f)
            
            self.settings_mgr.set("username", name)
            app = self.winfo_toplevel()
            if hasattr(app, "toggle_sidebar"):
                app.toggle_sidebar(True)
            self.show_state_b(name)

        ctk.CTkButton(new_card, text="Create & Enter ➔", font=("Arial", 16, "bold"), fg_color=("#2563EB", "#3B82F6"), hover_color="#2563EB", height=40, width=180, command=create_new).pack(pady=(15, 25))

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
        
        header_readiness = ctk.CTkFrame(readiness_frame, fg_color="transparent")
        header_readiness.pack(anchor="w", pady=(0, 15))
        brain_icon = get_icon("brain_color", size=(28, 28))
        ctk.CTkLabel(header_readiness, text="" if brain_icon else "🧠 ", image=brain_icon).pack(side="left", padx=(0, 5))
        ctk.CTkLabel(header_readiness, text="Model Readiness", font=("Arial", 24, "bold"), text_color=("gray20", "gray80")).pack(side="left")
        
        models_grid = ctk.CTkFrame(readiness_frame, fg_color=("gray90", "#222222"), corner_radius=15, border_width=1, border_color=("gray80", "#333333"))
        models_grid.pack(fill="x")
        
        games = [
            ("🐉 Snake", "snake", "#10B981"),
            ("🦅 Flappy Bird", "flappy_bird", "#F57C00"),
            ("🎾 Ping Pong", "ping_pong", "#3B82F6")
        ]
        
        for name, g_id, color in games:
            row = ctk.CTkFrame(models_grid, fg_color="transparent")
            row.pack(fill="x", padx=30, pady=15)
            
            title_frame = ctk.CTkFrame(row, fg_color="transparent", width=160, height=30)
            title_frame.pack_propagate(False) # Keep width fixed for alignment
            title_frame.pack(side="left")
            
            emoji, rest_of_title = name.split(" ", 1)
            
            ctk.CTkLabel(
                title_frame,
                text=emoji + " ",
                font=("Arial", 18, "bold"),
                text_color=color
            ).pack(side="left")

            ctk.CTkLabel(
                title_frame,
                text=rest_of_title,
                font=("Arial", 18, "bold"),
                text_color=("black", "white")
            ).pack(side="left")
            
            progress = LeaderboardManager.get_training_progress(g_id)
            
            bar = ctk.CTkProgressBar(row, progress_color=color, height=14)
            bar.pack(side="left", fill="x", expand=True, padx=20)
            bar.set(progress / 100.0)
            
            ctk.CTkLabel(row, text=f"{progress}% Trained", font=("Arial", 16, "bold"), width=120, anchor="e").pack(side="right")
            
        # Button row for Sign Out
        btn_row = ctk.CTkFrame(readiness_frame, fg_color="transparent")
        btn_row.pack(anchor="e", pady=(10, 0))
        def sign_out():
            self.settings_mgr.set("username", "")
            self.settings_mgr.set("age", "")
            app = self.winfo_toplevel()
            if hasattr(app, "toggle_sidebar"):
                app.toggle_sidebar(False)
            self.show_state_a()

        signout_btn = ctk.CTkButton(
            btn_row, 
            text="🚪 Sign Out", 
            font=("Arial", 13, "bold"), 
            fg_color="transparent", 
            text_color=("#BE123C", "#E11D48"), 
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
                
        rocket_icon = get_icon("rocket_color", size=(20, 20))
        ctk.CTkButton(btn_frame, text=" Start Training", image=rocket_icon, fg_color="#F97316", font=("Arial", 16, "bold"), height=50, width=180, command=lambda: nav("ai_training")).pack(side="left", padx=15)
        
        dashboard_icon = get_icon("dashboard_color", size=(20, 20))
        ctk.CTkButton(btn_frame, text=" View Dashboard", image=dashboard_icon, fg_color="#8B5CF6", font=("Arial", 16, "bold"), height=50, width=180, command=lambda: nav("dashboard")).pack(side="left", padx=15)
        game_icon = get_icon("game_color", size=(20, 20))
        ctk.CTkButton(btn_frame, text=" Play Games", image=game_icon, fg_color=("#059669", "#10B981"), font=("Arial", 16, "bold"), height=50, width=180, command=lambda: nav("play")).pack(side="left", padx=15)