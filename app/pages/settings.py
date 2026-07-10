import os
import customtkinter as ctk
from app.utils.icon_loader import get_icon
from tkinter import filedialog, messagebox
from app.utils.settings_manager import SettingsManager

class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.settings = SettingsManager()

        self.main_container = self
        header = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(40, 20))
        
        settings_icon = get_icon("settings_color", size=(28, 28))
        ctk.CTkLabel(
            header,
            text="" if settings_icon else "⚙ ",
            image=settings_icon
        ).pack(side="left", padx=(0, 5))
        
        title = ctk.CTkLabel(
            header,
            text="GameBrain Settings",
            font=("Arial", 30, "bold")
        )
        title.pack(side="left")

        # Scrollable container for forms
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=30, pady=10)

        # 1. UI Appearance Section
        self.create_appearance_card()

        # 2. Simulation & Hyperparameters Section
        self.create_sim_card()

        # 3. Environment & Directories Section
        self.create_env_card()

    def create_appearance_card(self):
        card = ctk.CTkFrame(self.scroll, fg_color=("gray95", "#202020"), corner_radius=15, border_width=1, border_color=("gray85", "#303030"))
        card.pack(fill="x", pady=10, padx=5)

        palette_icon = get_icon("palette_color", size=(20, 20))
        header_ui = ctk.CTkFrame(card, fg_color="transparent")
        header_ui.pack(fill="x", padx=20, pady=(15, 10))
        ctk.CTkLabel(header_ui, text="" if palette_icon else "🎨 ", image=palette_icon).pack(side="left", padx=(0, 5))
        ctk.CTkLabel(header_ui, text="UI Appearance & Aesthetics", font=("Arial", 18, "bold"), text_color=("#005B96", "cyan")).pack(side="left")

        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=(5, 15))

        # Theme
        ctk.CTkLabel(form, text="Theme Mode:", font=("Arial", 13)).grid(row=0, column=0, sticky="w", pady=8)
        self.theme_menu = ctk.CTkOptionMenu(
            form,
            values=["dark", "light"],
            command=self.change_theme
        )
        self.theme_menu.grid(row=0, column=1, sticky="w", padx=20, pady=8)
        self.theme_menu.set(self.settings.get("theme", "dark"))

    def create_sim_card(self):
        card = ctk.CTkFrame(self.scroll, fg_color=("gray95", "#202020"), corner_radius=15, border_width=1, border_color=("gray85", "#303030"))
        card.pack(fill="x", pady=10, padx=5)

        game_icon = get_icon("game_color", size=(20, 20))
        header_sim = ctk.CTkFrame(card, fg_color="transparent")
        header_sim.pack(fill="x", padx=20, pady=(15, 10))
        ctk.CTkLabel(header_sim, text="" if game_icon else "🎮 ", image=game_icon).pack(side="left", padx=(0, 5))
        ctk.CTkLabel(header_sim, text="Simulation & Training Parameters", font=("Arial", 18, "bold"), text_color=("#005B96", "cyan")).pack(side="left")

        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=(5, 15))

        # Game FPS Slider
        ctk.CTkLabel(form, text="Human Play Speed (FPS):", font=("Arial", 13)).grid(row=0, column=0, sticky="w", pady=10)
        self.fps_slider = ctk.CTkSlider(
            form,
            from_=5,
            to=30,
            number_of_steps=25,
            command=self.update_fps
        )
        self.fps_slider.grid(row=0, column=1, sticky="w", padx=20, pady=10)
        self.fps_slider.set(self.settings.get("fps", 10))
        self.fps_val_lbl = ctk.CTkLabel(form, text=f"{int(self.fps_slider.get())} FPS", font=("Arial", 12, "bold"))
        self.fps_val_lbl.grid(row=0, column=2, sticky="w", pady=10)

        # Graph Refresh Rate
        ctk.CTkLabel(form, text="Graph Update Period (Episodes):", font=("Arial", 13)).grid(row=1, column=0, sticky="w", pady=10)
        self.graph_rate_menu = ctk.CTkOptionMenu(
            form,
            values=["1", "5", "10", "20", "50"],
            command=self.update_graph_rate
        )
        self.graph_rate_menu.grid(row=1, column=1, sticky="w", padx=20, pady=10)
        self.graph_rate_menu.set(str(self.settings.get("graph_refresh_rate", 1)))

    def create_env_card(self):
        card = ctk.CTkFrame(self.scroll, fg_color=("gray95", "#202020"), corner_radius=15, border_width=1, border_color=("gray85", "#303030"))
        card.pack(fill="x", pady=10, padx=5)

        hw_icon = get_icon("settings_color", size=(20, 20))
        header_hw = ctk.CTkFrame(card, fg_color="transparent")
        header_hw.pack(fill="x", padx=20, pady=(15, 10))
        ctk.CTkLabel(header_hw, text="" if hw_icon else "⚙ ", image=hw_icon).pack(side="left", padx=(0, 5))
        ctk.CTkLabel(header_hw, text="Hardware & Directories", font=("Arial", 18, "bold"), text_color=("#005B96", "cyan")).pack(side="left")

        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=(5, 15))

        # Model Dir
        ctk.CTkLabel(form, text="Model Save Directory:", font=("Arial", 13)).grid(row=0, column=0, sticky="w", pady=10)
        self.dir_entry = ctk.CTkEntry(form, width=250)
        self.dir_entry.grid(row=0, column=1, sticky="w", padx=20, pady=10)
        self.dir_entry.insert(0, self.settings.get("model_dir", "saved_models"))
        
        dir_btn = ctk.CTkButton(
            form,
            text="📁 Browse",
            width=80,
            command=self.browse_model_dir
        )
        dir_btn.grid(row=0, column=2, sticky="w", pady=10)

        # GPU Toggle
        ctk.CTkLabel(form, text="Enable CUDA acceleration (GPU):", font=("Arial", 13)).grid(row=1, column=0, sticky="w", pady=10)
        self.gpu_switch = ctk.CTkSwitch(
            form,
            text="Use GPU",
            command=self.toggle_gpu
        )
        self.gpu_switch.grid(row=1, column=1, sticky="w", padx=20, pady=10)
        if self.settings.get("gpu_toggle", True):
            self.gpu_switch.select()
        else:
            self.gpu_switch.deselect()

    def change_theme(self, choice):
        self.settings.set("theme", choice)
        ctk.set_appearance_mode(choice)



    def update_fps(self, value):
        fps = int(value)
        self.fps_val_lbl.configure(text=f"{fps} FPS")
        self.settings.set("fps", fps)

    def update_graph_rate(self, choice):
        self.settings.set("graph_refresh_rate", int(choice))

    def browse_model_dir(self):
        folder = filedialog.askdirectory(title="Select Model Storage Directory")
        if folder:
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, folder)
            self.settings.set("model_dir", folder)

    def toggle_gpu(self):
        val = self.gpu_switch.get() == 1
        self.settings.set("gpu_toggle", val)