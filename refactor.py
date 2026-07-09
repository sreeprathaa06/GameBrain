import os

play_path = "app/pages/play.py"
with open(play_path, "r", encoding="utf-8") as f:
    play_content = f.read()

# Add imports for envs
imports = """
from environments.snake_env import SnakeEnv
from environments.ping_pong_env import PingPongEnv
from environments.flappy_bird_env import FlappyBirdEnv
from environments.chess_env import ChessEnv

def get_env_class(name):
    if name == "Ping Pong": return PingPongEnv
    elif name == "Flappy Bird": return FlappyBirdEnv
    elif name == "Chess": return ChessEnv
    return SnakeEnv
"""
play_content = play_content.replace("from environments.snake_env import SnakeEnv", imports)

# Add game selection to PlayPage
game_sel = """        self.selected_game = "Snake"
        self.game_selector = ctk.CTkOptionMenu(
            self.menu_frame,
            values=["Snake", "Ping Pong", "Flappy Bird", "Chess"],
            command=self.change_game,
            font=("Arial", 16)
        )
        self.game_selector.pack(pady=10)
"""
play_content = play_content.replace('title.pack(pady=(20, 5))', 'title.pack(pady=(20, 5))\n' + game_sel)

change_game_func = """
    def change_game(self, choice):
        self.selected_game = choice
"""
play_content = play_content.replace('    def build_menu_view(self):', change_game_func + '\n    def build_menu_view(self):')

# Pass game choice to views
play_content = play_content.replace('self.show_view("human")', 'self.show_view("human", self.selected_game)')
play_content = play_content.replace('self.show_view("human_vs_ai")', 'self.show_view("human_vs_ai", self.selected_game)')

# Update show_view
play_content = play_content.replace('def show_view(self, view_type):', 'def show_view(self, view_type, game="Snake"):')
play_content = play_content.replace('self.current_view = HumanPlayView(self, self.back_to_menu)', 'self.current_view = HumanPlayView(self, self.back_to_menu, game)')
play_content = play_content.replace('self.current_view = HumanVsAIView(self, self.back_to_menu)', 'self.current_view = HumanVsAIView(self, self.back_to_menu, game)')

# Update views init
play_content = play_content.replace('def __init__(self, parent, exit_callback):', 'def __init__(self, parent, exit_callback, game="Snake"):')
play_content = play_content.replace('self.env = SnakeEnv()', 'self.env = get_env_class(game)()')
play_content = play_content.replace('self.h_env = SnakeEnv()', 'self.h_env = get_env_class(game)()')
play_content = play_content.replace('self.ai_env = SnakeEnv()', 'self.ai_env = get_env_class(game)()')
play_content = play_content.replace('self.env = SnakeEnv(render=True)', 'self.env = get_env_class(game)(render=True)')


with open(play_path, "w", encoding="utf-8") as f:
    f.write(play_content)


ai_path = "app/pages/ai_training.py"
with open(ai_path, "r", encoding="utf-8") as f:
    ai_content = f.read()

ai_content = ai_content.replace("from environments.snake_env import SnakeEnv", imports)
ai_content = ai_content.replace('self.selected_game = "Snake"\n', '')

game_sel_ai = """
        # Game selection
        self.selected_game = "Snake"
        self.game_selector = ctk.CTkOptionMenu(
            header,
            values=["Snake", "Ping Pong", "Flappy Bird", "Chess"],
            command=self.change_game_ai
        )
        self.game_selector.pack(side="left", padx=10)
"""
ai_content = ai_content.replace('ctk.CTkLabel(header, text="🧠 Training Control Center", font=("Arial", 18, "bold"), text_color="cyan").pack(side="left", padx=20)', 'ctk.CTkLabel(header, text="🧠 Training Control Center", font=("Arial", 18, "bold"), text_color="cyan").pack(side="left", padx=20)\n' + game_sel_ai)

ai_content = ai_content.replace('    def build_ui(self):', """
    def change_game_ai(self, choice):
        self.selected_game = choice
        self.log_msg(f"Switched target environment to {choice}")

    def build_ui(self):""")

# Actually modifying the training loop to use the new env requires changing where the env is initialized.
# In ai_training.py, it calls `train()` from rl.dqn.train
# We need to pass the game choice to the training loop, but that requires modifying train() too.

with open(ai_path, "w", encoding="utf-8") as f:
    f.write(ai_content)
