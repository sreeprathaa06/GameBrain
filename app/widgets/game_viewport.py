import customtkinter as ctk

class GameViewport(ctk.CTkFrame):
    def __init__(self, parent, grid_width=20, grid_height=20, cell_size=20, accent_color="blue", **kwargs):
        super().__init__(parent, fg_color="#181818", corner_radius=15, border_width=1, border_color="#303030", **kwargs)

        self.grid_width = grid_width
        self.grid_height = grid_height
        self.cell_size = cell_size
        self.accent_color = accent_color

        # Dimensions
        self.width = grid_width * cell_size
        self.height = grid_height * cell_size

        # Canvas
        self.canvas = ctk.CTkCanvas(
            self,
            width=self.width,
            height=self.height,
            bg="#181818",
            highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=10, expand=True)

        self.draw_empty()

    def set_accent_color(self, color):
        self.accent_color = color

    def draw_empty(self, message="NO ACTIVE GAME"):
        self.canvas.delete("all")
        self.draw_grid()
        self.canvas.create_text(
            self.width // 2,
            self.height // 2,
            text=message,
            fill="#555555",
            font=("Arial", 16, "bold")
        )

    def draw_grid(self):
        # Draw subtle grid lines
        for i in range(self.grid_width + 1):
            x = i * self.cell_size
            self.canvas.create_line(x, 0, x, self.height, fill="#232323", width=1)
        for j in range(self.grid_height + 1):
            y = j * self.cell_size
            self.canvas.create_line(0, y, self.width, y, fill="#232323", width=1)

    def draw_game(self, snake_body, food_position, score=0, overlay_text=None, ai_info=None):
        self.canvas.delete("all")
        self.draw_grid()

        # Accent colors mapping
        theme_colors = {
            "blue": {"head": "#00F0FF", "body": "#1D4ED8", "border": "#3B82F6"},
            "purple": {"head": "#E087FF", "body": "#6D28D9", "border": "#8B5CF6"},
            "cyan": {"head": "#00F5D4", "body": "#0F766E", "border": "#14B8A6"},
            "orange": {"head": "#FFB703", "body": "#C2410C", "border": "#F97316"},
            "green": {"head": "#39FF14", "body": "#047857", "border": "#10B981"}
        }
        
        colors = theme_colors.get(self.accent_color, theme_colors["blue"])

        # Draw Food (glowy neon red)
        fx, fy = food_position
        x0 = fx * self.cell_size + 2
        y0 = fy * self.cell_size + 2
        x1 = (fx + 1) * self.cell_size - 2
        y1 = (fy + 1) * self.cell_size - 2
        
        # Food Shadow/Glow
        self.canvas.create_oval(x0-1, y0-1, x1+1, y1+1, fill="#E11D48", outline="#F43F5E", width=1)
        self.canvas.create_oval(x0+2, y0+2, x1-2, y1-2, fill="#FDA4AF", outline="")

        # Draw Snake
        for idx, (bx, by) in enumerate(snake_body):
            x0 = bx * self.cell_size + 1
            y0 = by * self.cell_size + 1
            x1 = (bx + 1) * self.cell_size - 1
            y1 = (by + 1) * self.cell_size - 1

            if idx == 0:
                # Snake Head
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=colors["head"], outline="#FFFFFF", width=1.5)
                # Small Eyes
                self.canvas.create_oval(x0+3, y0+3, x0+6, y0+6, fill="#000000", outline="")
                self.canvas.create_oval(x1-6, y0+3, x1-3, y0+6, fill="#000000", outline="")
            else:
                # Body segment with slight rounding feel
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=colors["body"], outline=colors["border"], width=1)

        # Draw Score Display inside Canvas (subtle top right)
        self.canvas.create_text(
            self.width - 45,
            20,
            text=f"SCORE: {score}",
            fill="#FFFFFF",
            font=("Arial", 11, "bold")
        )

        # Display AI stats if in AI Mode
        if ai_info:
            action_text = f"Action: {ai_info.get('action', '')}"
            conf_text = f"Conf: {ai_info.get('confidence', 0.0):.1f}%"
            self.canvas.create_text(
                55,
                20,
                text=f"{action_text} | {conf_text}",
                fill="#00FFCC",
                font=("Arial", 10, "bold")
            )

        # Draw Overlay Text
        if overlay_text:
            # Semi-transparent overlay
            self.canvas.create_rectangle(
                0, 0, self.width, self.height,
                fill="#000000", stipple="gray50" if hasattr(self.canvas, "stipple") else "",
                outline=""
            )
            # Recreate background box for readable text
            self.canvas.create_rectangle(
                self.width // 2 - 120, self.height // 2 - 45,
                self.width // 2 + 120, self.height // 2 + 45,
                fill="#1E1E1E", outline=colors["border"], width=2
            )
            self.canvas.create_text(
                self.width // 2,
                self.height // 2,
                text=overlay_text,
                fill="#FFFFFF",
                font=("Arial", 18, "bold"),
                justify="center"
            )
