import customtkinter as ctk
import webbrowser
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class AcademyPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        title = ctk.CTkLabel(
            self,
            text="🧠 AI Academy: Reinforcement Learning",
            font=("Arial", 30, "bold")
        )
        title.pack(pady=(15, 10))

        # Split layout: Left lessons index, Right reader frame
        split_frame = ctk.CTkFrame(self, fg_color="transparent")
        split_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Left Index
        self.left_panel = ctk.CTkFrame(split_frame, width=240, fg_color=("gray95", "#202020"), corner_radius=12, border_width=1, border_color=("gray85", "#303030"))
        self.left_panel.pack(side="left", fill="y", padx=(0, 10))
        self.left_panel.pack_propagate(False)

        ctk.CTkLabel(self.left_panel, text="Lessons Index", font=("Arial", 16, "bold"), text_color=("#005B96", "cyan")).pack(pady=12)

        self.lessons_scroll = ctk.CTkScrollableFrame(self.left_panel, fg_color="transparent")
        self.lessons_scroll.pack(fill="both", expand=True, padx=5, pady=(0, 10))

        # Right Reader
        self.right_panel = ctk.CTkFrame(split_frame, fg_color=("gray95", "#202020"), corner_radius=12, border_width=1, border_color=("gray85", "#303030"))
        self.right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        self.right_panel.pack_propagate(False)

        # Text Reader
        self.reader = ctk.CTkTextbox(self.right_panel, fg_color="transparent", wrap="word", font=("Arial", 14), text_color=("gray10", "gray80"))
        
        # Configure tags
        self.reader._textbox.tag_config("h1", font=("Arial", 26, "bold"), foreground="#005B96", spacing3=15)
        self.reader._textbox.tag_config("h2", font=("Arial", 20, "bold"), foreground="#B39DDB", spacing1=20, spacing3=10)
        self.reader._textbox.tag_config("h3", font=("Arial", 16, "bold"), foreground="#81C784", spacing1=10, spacing3=5)
        self.reader._textbox.tag_config("p", font=("Arial", 15), foreground="#E0E0E0", spacing3=10)
        self.reader._textbox.tag_config("bold", font=("Arial", 15, "bold"), foreground="#FFFFFF")
        self.reader._textbox.tag_config("code", font=("Courier New", 14), foreground="#10B981", background="#151515", lmargin1=20, lmargin2=20, spacing1=10, spacing3=10)
        self.reader._textbox.tag_config("link", font=("Arial", 15, "underline"), foreground="#3B82F6", spacing1=10, spacing3=10)
        
        self.reader._textbox.tag_bind("link", "<Button-1>", self.open_link)
        self.reader._textbox.tag_bind("link", "<Enter>", lambda e: self.reader._textbox.config(cursor="hand2"))
        self.reader._textbox.tag_bind("link", "<Leave>", lambda e: self.reader._textbox.config(cursor="arrow"))

        # Quiz Frame
        self.quiz_frame = ctk.CTkScrollableFrame(self.right_panel, fg_color="transparent")
        
        self.active_btn = None
        self.lessons_data = self.get_lessons_data()
        
        self.quiz_questions = self.get_quiz_questions()
        self.quiz_answers = {}

        self.build_index()

        # Load first lesson by default
        self.load_lesson("intro")
        
    def open_link(self, event):
        index = self.reader._textbox.index(f"@{event.x},{event.y}")
        line_text = self.reader._textbox.get(f"{index} linestart", f"{index} lineend")
        if "https://" in line_text:
            url = "https://" + line_text.split("https://")[1].strip()
            webbrowser.open(url)

    def build_index(self):
        for key, lesson in self.lessons_data.items():
            btn = ctk.CTkButton(
                self.lessons_scroll,
                text=lesson["title"],
                font=("Arial", 13, "bold"),
                fg_color="transparent",
                text_color=("gray20", "gray80"),
                hover_color=("gray85", "#303030"),
                anchor="w",
                height=38,
                command=lambda k=key: self.load_lesson(k)
            )
            btn.pack(fill="x", pady=4, padx=5)
            lesson["btn"] = btn
            
        # Add Quiz Button
        ctk.CTkFrame(self.lessons_scroll, height=2, fg_color="#303030").pack(fill="x", pady=10, padx=10)
        self.quiz_btn = ctk.CTkButton(
            self.lessons_scroll,
            text="📝 Take the Quiz",
            font=("Arial", 14, "bold"),
            fg_color="#F57C00",
            text_color="#FFFFFF",
            hover_color="#E65100",
            anchor="w",
            height=42,
            command=lambda: self.load_lesson("quiz")
        )
        self.quiz_btn.pack(fill="x", pady=4, padx=5)

    def load_lesson(self, key):
        # Reset button styles
        if self.active_btn:
            self.active_btn.configure(fg_color="transparent", text_color=("gray20", "gray80"))
        
        if key == "quiz":
            self.quiz_btn.configure(fg_color="#1E3A8A", text_color="#FFFFFF")
            self.active_btn = self.quiz_btn
            
            self.reader.pack_forget()
            self.quiz_frame.pack(fill="both", expand=True, padx=15, pady=15)
            self.render_quiz()
        else:
            self.quiz_btn.configure(fg_color="#F57C00", text_color="#FFFFFF")
            lesson = self.lessons_data[key]
            lesson["btn"].configure(fg_color="#1E3A8A", text_color="#FFFFFF")
            self.active_btn = lesson["btn"]
            
            self.quiz_frame.pack_forget()
            self.reader.pack(fill="both", expand=True, padx=15, pady=15)

            self.reader.configure(state="normal")
            self.reader.delete("1.0", "end")

            self.reader.insert("end", lesson["title"] + "\n", "h1")

            for element in lesson["elements"]:
                el_type = element[0]
                val = element[1]

                if el_type == "p":
                    self.reader.insert("end", val + "\n", "p")
                elif el_type == "h2":
                    self.reader.insert("end", val + "\n", "h2")
                elif el_type == "h3":
                    self.reader.insert("end", val + "\n", "h3")
                elif el_type == "code":
                    self.reader.insert("end", val + "\n", "code")
                elif el_type == "link":
                    self.reader.insert("end", val + "\n", "link")

            self.reader.configure(state="disabled")

    def render_quiz(self):
        for child in self.quiz_frame.winfo_children():
            child.destroy()
            
        ctk.CTkLabel(self.quiz_frame, text="🧠 AI Academy Knowledge Check", font=("Arial", 26, "bold"), text_color="#005B96").pack(anchor="w", pady=(0, 20))
        
        self.quiz_answers = {}
        
        for i, q in enumerate(self.quiz_questions):
            q_frame = ctk.CTkFrame(self.quiz_frame, fg_color="#1E1E1E", corner_radius=10, border_width=1, border_color="#303030")
            q_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(q_frame, text=f"Q{i+1}: {q['question']}", font=("Arial", 16, "bold"), wraplength=700, justify="left").pack(anchor="w", padx=15, pady=(15, 10))
            
            var = ctk.IntVar(value=-1)
            self.quiz_answers[i] = var
            
            for j, opt in enumerate(q["options"]):
                rb = ctk.CTkRadioButton(q_frame, text=opt, variable=var, value=j, font=("Arial", 14))
                rb.pack(anchor="w", padx=25, pady=5)
                
            ctk.CTkFrame(q_frame, height=5, fg_color="transparent").pack() # padding
            
        submit_btn = ctk.CTkButton(self.quiz_frame, text="✅ Submit Quiz", font=("Arial", 16, "bold"), fg_color="#10B981", hover_color="#059669", height=45, command=self.submit_quiz)
        submit_btn.pack(pady=30)
        
    def submit_quiz(self):
        for child in self.quiz_frame.winfo_children():
            child.destroy()
            
        score = 0
        total = len(self.quiz_questions)
        
        for i, q in enumerate(self.quiz_questions):
            if self.quiz_answers[i].get() == q["answer"]:
                score += 1
                
        percentage = (score / total) * 100
        
        if percentage >= 90:
            msg = "🏆 Amazing! You are an AI Master!"
            color = "#10B981"
        elif percentage >= 70:
            msg = "👏 Great job! You have a solid grasp of RL concepts."
            color = "#3B82F6"
        elif percentage >= 50:
            msg = "👍 Good effort! Review the basics to solidify your understanding."
            color = "#F57C00"
        else:
            msg = "📚 Keep learning! The AI Academy is here to help you."
            color = "#E11D48"
            
        ctk.CTkLabel(self.quiz_frame, text="Quiz Results", font=("Arial", 28, "bold"), text_color="cyan").pack(pady=(20, 10))
        ctk.CTkLabel(self.quiz_frame, text=f"You scored: {score} / {total}", font=("Arial", 22, "bold"), text_color=color).pack(pady=5)
        ctk.CTkLabel(self.quiz_frame, text=msg, font=("Arial", 16)).pack(pady=(5, 20))
        
        # --- Pie Chart Integration ---
        graph_frame = ctk.CTkFrame(self.quiz_frame, fg_color="transparent")
        graph_frame.pack(fill="x", pady=10)
        
        fig = Figure(figsize=(5, 3), dpi=100, facecolor='#1E1E1E')
        ax = fig.add_subplot(111)
        
        incorrect = total - score
        labels = ['Correct', 'Incorrect'] if incorrect > 0 else ['Correct']
        sizes = [score, incorrect] if incorrect > 0 else [score]
        colors = ['#10B981', '#E11D48'] if incorrect > 0 else ['#10B981']
        
        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
            startangle=90, textprops={'color': "white", 'weight': 'bold', 'fontsize': 10},
            wedgeprops=dict(width=0.4, edgecolor='#1E1E1E')
        )
        
        ax.axis('equal')  
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=5)
        # -----------------------------
        
        # Detailed Review
        ctk.CTkLabel(self.quiz_frame, text="Detailed Analysis:", font=("Arial", 18, "bold")).pack(anchor="w", pady=(20, 10))
        
        for i, q in enumerate(self.quiz_questions):
            user_ans = self.quiz_answers[i].get()
            correct_ans = q["answer"]
            
            review_frame = ctk.CTkFrame(self.quiz_frame, fg_color="#1E1E1E", corner_radius=10, border_width=1, border_color="#303030")
            review_frame.pack(fill="x", pady=8)
            
            header_color = "#10B981" if user_ans == correct_ans else "#E11D48"
            icon = "✅" if user_ans == correct_ans else "❌"
            
            ctk.CTkLabel(review_frame, text=f"{icon} Q{i+1}: {q['question']}", font=("Arial", 15, "bold"), text_color=header_color, wraplength=700, justify="left").pack(anchor="w", padx=15, pady=(15, 5))
            
            if user_ans == correct_ans:
                ctk.CTkLabel(review_frame, text=f"Your Answer: {q['options'][user_ans]}", font=("Arial", 14), text_color="gray80").pack(anchor="w", padx=35, pady=(0, 15))
            else:
                user_text = q['options'][user_ans] if user_ans != -1 else "No Answer Selected"
                ctk.CTkLabel(review_frame, text=f"Your Answer: {user_text}", font=("Arial", 14), text_color="#E11D48").pack(anchor="w", padx=35, pady=2)
                ctk.CTkLabel(review_frame, text=f"Correct Answer: {q['options'][correct_ans]}", font=("Arial", 14), text_color="#10B981").pack(anchor="w", padx=35, pady=(2, 15))

        retake_btn = ctk.CTkButton(self.quiz_frame, text="🔄 Retake Quiz", font=("Arial", 16, "bold"), fg_color="#2563EB", hover_color="#1D4ED8", height=45, command=self.render_quiz)
        retake_btn.pack(pady=30)

    def get_quiz_questions(self):
        return [
            {
                "question": "What is the primary goal of an RL Agent?",
                "options": ["To crash the game", "To maximize cumulative reward over time", "To memorize the exact sequence of inputs", "To minimize its score"],
                "answer": 1
            },
            {
                "question": "What does a Neural Network act as in Deep Q-Learning?",
                "options": ["The 'brain' that predicts the best action based on the state", "The physics engine for the game", "A database of all past states", "The reward generator"],
                "answer": 0
            },
            {
                "question": "What is the 'State' in GameBrain's Flappy Bird environment?",
                "options": ["Just the bird's score", "The pixels on the screen", "The bird's Y-position, velocity, and distance to the next pipes", "The player's username"],
                "answer": 2
            },
            {
                "question": "What is 'Experience Replay' used for?",
                "options": ["To record a video of the game", "To store past memories (state, action, reward) to train on later", "To instantly revive the snake when it dies", "To undo the last move made by the human"],
                "answer": 1
            },
            {
                "question": "If an agent is 'Exploring' (Epsilon-Greedy), what is it doing?",
                "options": ["Always taking the action it thinks is best", "Choosing a completely random action to discover new strategies", "Shutting down the game", "Asking the human player what to do"],
                "answer": 1
            },
            {
                "question": "What happens to 'Epsilon' over time during training?",
                "options": ["It increases, so the agent explores more", "It stays exactly at 1.0 forever", "It decays (decreases), shifting from exploration to exploitation", "It turns into a reward"],
                "answer": 2
            },
            {
                "question": "What is the purpose of 'Reward Shaping'?",
                "options": ["To make the UI look nicer", "To provide small hints/rewards (like moving towards food) to guide learning", "To punish the human player", "To make the game run faster"],
                "answer": 1
            },
            {
                "question": "What is the 'Markov Property'?",
                "options": ["The future depends only on the current state and action, not the history", "The game must be played by a guy named Markov", "The agent always wins", "The reward must be negative"],
                "answer": 0
            },
            {
                "question": "Why does DQN use a 'Target Network'?",
                "options": ["To play multiplayer against another AI", "To stabilize training by providing a fixed target for a short period", "To track the human's high score", "To generate random numbers"],
                "answer": 1
            },
            {
                "question": "In GameBrain's Dashboard, what does 'Average Reward' tell us?",
                "options": ["How fast the game is running", "How well the AI is performing over recent episodes", "How much memory the computer is using", "The number of times the human paused the game"],
                "answer": 1
            },
            {
                "question": "What is a Target Network?",
                "options": ["A network that targets specific enemies", "A slow-updating copy of the main network to keep learning stable", "The server that hosts the game", "A network used only for human players"],
                "answer": 1
            },
            {
                "question": "What is the Discount Factor (Gamma)?",
                "options": ["A coupon code for the game", "A number indicating how much the AI values long-term rewards vs short-term rewards", "The speed at which the snake moves", "The amount of memory used by the replay buffer"],
                "answer": 1
            },
            {
                "question": "What is State Space?",
                "options": ["Outer space levels in a game", "The physical RAM the computer has", "The mathematical representation of the environment given to the AI", "The amount of time the user spends playing"],
                "answer": 2
            },
            {
                "question": "What happens when you increase the 'Batch Size'?",
                "options": ["The AI trains on more past memories at once during an update", "The snake gets thicker", "The screen resolution increases", "The game slows down permanently"],
                "answer": 0
            },
            {
                "question": "What does 'Convergence' mean in training?",
                "options": ["The AI's performance stops improving and stabilizes", "The game crashes", "The human player takes over", "The loss reaches infinity"],
                "answer": 0
            }
        ]

    def get_lessons_data(self):
        return {
            "intro": {
                "title": "1. Beginner Basics: What is AI?",
                "elements": [
                    ("p", "Welcome to the AI Academy! Before we dive into the complex mathematics, let's start with a very simple question: What is Artificial Intelligence?"),
                    ("p", "Imagine a toddler learning to walk. They don't read a manual on gravity and muscle contraction. Instead, they try to stand, fall down, and realize, 'Okay, that didn't work.' They try again, shift their weight differently, and manage to take a step. Every time they fall, they experience a 'penalty.' Every time they take a successful step, they get a 'reward' (cheering parents!)."),
                    ("p", "Artificial Intelligence, specifically Machine Learning, works the exact same way. Instead of writing thousands of lines of code explicitly telling a character how to play Flappy Bird ('IF obstacle is 5 pixels away, THEN jump'), we simply create an environment and let the computer learn through trial and error."),
                    ("h2", "The Three Pillars of Machine Learning"),
                    ("p", "There are generally three main ways computers learn:"),
                    ("p", "1. Supervised Learning: The computer is given a massive textbook of answers. (e.g., showing a computer 10,000 pictures of cats labeled 'Cat')."),
                    ("p", "2. Unsupervised Learning: The computer is given raw data and asked to find patterns. (e.g., grouping customers by purchasing habits)."),
                    ("p", "3. Reinforcement Learning (RL): The computer is dropped into a world, given a goal, and learns entirely by interacting with that world. This is what GameBrain uses!"),
                    ("link", "Learn more: https://www.ibm.com/topics/artificial-intelligence")
                ]
            },
            "nn_basics": {
                "title": "2. Neural Networks Explained",
                "elements": [
                    ("p", "You hear the term 'Neural Network' everywhere, but what actually is it?"),
                    ("p", "Think of a Neural Network as a giant committee of tiny decision-makers. In our games, the 'State' (what the AI sees) is handed to the committee. Each member of the committee looks at a small piece of the information, multiplies it by an 'importance factor' (called a Weight), adds their own personal bias, and passes their opinion to the next row of decision-makers."),
                    ("h2", "Layers of the Network"),
                    ("p", "A Neural Network is divided into layers:"),
                    ("code", "  [Input Layer] --> [Hidden Layers] --> [Output Layer]"),
                    ("p", "• Input Layer: The eyes of the AI. In Snake, this is a list of 12 numbers telling the AI where the food is, where the walls are, and where its tail is."),
                    ("p", "• Hidden Layers: The actual brain. These are the decision-makers that calculate complex patterns. GameBrain uses layers with 128 'neurons' each."),
                    ("p", "• Output Layer: The final decision. In Snake, this layer outputs 4 numbers, one for each possible action (UP, DOWN, LEFT, RIGHT). The AI looks at which number is the highest and takes that action!"),
                    ("h2", "Learning = Adjusting Weights"),
                    ("p", "When an AI makes a mistake (like running into a wall), we 'punish' it. A mathematical algorithm called Backpropagation goes backwards through the committee and tells everyone, 'You gave bad advice! Lower your weights!' Over time, the committee gets very, very good at giving the right advice."),
                    ("link", "Learn more: https://www.3blue1brown.com/topics/neural-networks")
                ]
            },
            "rl_basics": {
                "title": "3. Reinforcement Learning",
                "elements": [
                    ("p", "Reinforcement Learning (RL) is a subfield of machine learning where an Agent learns to make decisions by performing actions in an Environment to maximize some cumulative Reward."),
                    ("h2", "The Feedback Loop"),
                    ("p", "The agent interacts with the environment in an endless cycle. Imagine playing a video game blindfolded, where the only feedback you get is someone saying 'Good' or 'Bad' after you press a button on the controller."),
                    ("code", "   +------------+             Action (A)            +-------------+\n   |            | --------------------------------> |             |\n   |   Agent    |                                   | Environment |\n   |            | <-------------------------------- |             |\n   +------------+        State (S) & Reward (R)     +-------------+"),
                    ("p", "1. Observation (State): The agent observes the current state S of the environment (e.g., the bird's height in Flappy Bird)."),
                    ("p", "2. Decision (Action): The agent chooses an action A according to its policy (e.g., Flap or Don't Flap)."),
                    ("p", "3. Execution: The environment updates based on that action, moving to a new state S'."),
                    ("p", "4. Learning (Reward): The environment returns a reward R (e.g., +1 for passing a pipe, -100 for crashing). The agent uses this to update its brain."),
                    ("link", "Learn more: https://spinningup.openai.com/en/latest/spinningup/rl_intro.html")
                ]
            },
            "gamebrain_arch": {
                "title": "4. Inside GameBrain",
                "elements": [
                    ("p", "GameBrain is built entirely in Python using CustomTkinter for the UI and PyTorch for the AI brains. Let's break down how the application actually works under the hood."),
                    ("h2", "The Application Architecture"),
                    ("p", "GameBrain is divided into several independent systems that talk to each other:"),
                    ("h3", "1. The Environments (environments/)"),
                    ("p", "These are the games themselves (Snake, Ping Pong, Flappy Bird). However, they aren't written like normal games. They are written as 'Gym Environments'. This means they don't rely on graphics to run. They can run millions of times in the background instantly by just returning mathematical states and taking mathematical actions."),
                    ("h3", "2. The RL Brains (rl/)"),
                    ("p", "This is where the PyTorch Deep Q-Networks live. When you click 'Train', GameBrain spawns an instance of an environment and an instance of a DQN Agent. The Agent rapidly plays the environment in a loop, storing memories in its Replay Buffer and updating its Neural Network weights."),
                    ("h3", "3. The Data Loggers (app/utils/)"),
                    ("p", "As the Agent trains, it generates massive amounts of data. The `TrainingLogger` captures every episode's score, loss, and epsilon value, saving them instantly to a CSV file. The `LeaderboardManager` watches for high scores and records them so you can view them on the Dashboard."),
                    ("h3", "4. The UI (app/pages/)"),
                    ("p", "The UI constantly reads the logs and states. When you play a game in 'Duel Mode', the UI is actually running two separate environments side-by-side, passing your keyboard inputs to one, and the AI's Neural Network predictions to the other!"),
                    ("link", "Learn more: https://pytorch.org/tutorials/")
                ]
            },
            "dqn": {
                "title": "5. Deep Q-Networks",
                "elements": [
                    ("p", "In simple environments, an AI can just memorize a massive spreadsheet of every possible state and what the best move is (this is called tabular Q-Learning). But in complex games, there are millions of possible states. A spreadsheet would take up terabytes of RAM!"),
                    ("h2", "Enter Deep Q-Networks (DQN)"),
                    ("p", "Deep Q-Networks solve this by throwing away the spreadsheet and replacing it with a Neural Network. Instead of looking up the answer, the network calculates an approximation of the answer on the fly!"),
                    ("code", "  Input (State Vector)       Hidden Layers          Outputs (Q-Values)\n     [S_1, S_2, ... S_12]  -->  [128] --> [128]  -->  [UP, DOWN, LEFT, RIGHT]"),
                    ("p", "The network outputs 'Q-Values'. A Q-Value is simply the AI's prediction of how much total future reward it will get if it takes that action. If UP outputs 50.0 and DOWN outputs 10.0, the AI chooses UP because it predicts a higher future score."),
                    ("p", "During training, we minimize the error between our current Q prediction and the actual reward we end up getting. This allows the network to constantly 'correct' its intuition."),
                    ("link", "Learn more: https://www.cs.toronto.edu/~vmnih/docs/dqn.pdf")
                ]
            },
            "exploration": {
                "title": "6. Exploration vs Exploitation",
                "elements": [
                    ("p", "A fundamental challenge in AI is balancing exploration (trying crazy random things to discover new strategies) and exploitation (using what you already know to get a high score)."),
                    ("p", "Imagine going to a restaurant. You can 'exploit' by ordering your favorite meal (guaranteed happiness). Or you can 'explore' by ordering something completely new (it might be terrible, but it might become your new favorite!)."),
                    ("h2", "Epsilon-Greedy Strategy"),
                    ("p", "We implement this trade-off in code using a variable called Epsilon (ε):"),
                    ("code", "  With probability Epsilon:      Choose action at random (Exploration)\n  With probability 1 - Epsilon:  Choose action argmax_a Q(S, a) (Exploitation)"),
                    ("p", "At the start of training, Epsilon is 1.0 (100%). The AI is essentially flailing around randomly. This is crucial because it needs to accidentally stumble into the food to realize food is good!"),
                    ("p", "After every step, we multiply Epsilon by a decay factor (e.g. 0.995). Slowly, over thousands of games, the AI transitions from 100% random exploration to 99% exploitation, relying on its highly trained Neural Network to dominate the game."),
                    ("link", "Learn more: https://en.wikipedia.org/wiki/Multi-armed_bandit#Semi-uniform_strategies")
                ]
            },
            "reward_engineering": {
                "title": "7. Reward Engineering",
                "elements": [
                    ("p", "Rewards shape the optimal behavior of the agent. But AI is incredibly literal. If you design rewards poorly, the AI will find a loophole and do something you completely didn't intend! (Like spinning in circles forever just to stay alive)."),
                    ("h2", "GameBrain Reward Structures"),
                    ("p", "Let's look at how we shaped the rewards for our Snake agent:"),
                    ("code", "  Eating Food:       +20.0  (Strong positive reinforcement)\n  Dying (Wall/Self): -20.0  (Strong negative penalty)\n  Moving Closer:     +0.35  (Shaping reward for guiding search)\n  Moving Away:       -0.25  (Slight penalty to discourage wasting steps)"),
                    ("p", "Notice the 'Moving Closer' reward? If we only rewarded the snake for eating food, it would be extremely hard for it to learn at the beginning because accidentally finding food by moving randomly is rare. By giving it tiny breadcrumbs (+0.35) for getting closer to the food, we 'shape' its behavior and speed up learning by 100x!"),
                    ("link", "Learn more: https://bair.berkeley.edu/blog/2019/12/20/reward-shaping/")
                ]
            },
            "target_networks": {
                "title": "8. Target Networks",
                "elements": [
                    ("p", "In Deep Q-Learning, the AI tries to predict future rewards. But because it is constantly updating its own brain, the 'target' it is aiming for keeps moving. Imagine trying to hit a bullseye that shifts every time you shoot an arrow!"),
                    ("h2", "Stabilizing with a Second Brain"),
                    ("p", "To fix this, we use a 'Target Network'. This is simply a frozen copy of the main Neural Network. We use this frozen copy to calculate our targets, and we only update it occasionally (e.g. every 1,000 steps)."),
                    ("p", "By freezing the target, the main network has a stable goal to aim for, which prevents the AI from falling into feedback loops and forgetting how to play.")
                ]
            },
            "replay_buffer": {
                "title": "9. The Replay Buffer",
                "elements": [
                    ("p", "If an AI only learns from the exact moment it is currently experiencing, it will suffer from 'Catastrophic Forgetting'. If the snake only moves right for 50 steps, it forgets how to move left!"),
                    ("h2", "Learning from Past Memories"),
                    ("p", "The Replay Buffer is a massive database that stores the last 100,000 steps the AI took (State, Action, Reward, Next State)."),
                    ("p", "During training, instead of learning from the current step, the AI randomly samples a 'batch' of 64 memories from the buffer. This breaks the correlation between consecutive steps and ensures the AI remembers how to handle all situations.")
                ]
            },
            "gamma": {
                "title": "10. Discount Factor (Gamma)",
                "elements": [
                    ("p", "How much should an AI care about the future? If Gamma is 0, the AI only cares about immediate rewards (like eating food right in front of it) and will happily crash into a wall immediately after."),
                    ("h2", "Valuing the Future"),
                    ("p", "If Gamma is 0.99, the AI values a reward 100 steps in the future almost as much as a reward right now. This forces the AI to plan ahead. In Ping Pong, it learns to hit the ball in a way that makes it harder for the opponent to return it later, rather than just surviving the current hit.")
                ]
            },
            "state_space": {
                "title": "11. State Space Design",
                "elements": [
                    ("p", "The 'State' is everything the AI knows about the world. If we don't give the AI enough information, it's like playing a game blindfolded."),
                    ("h2", "Pixels vs Vectors"),
                    ("p", "We could give the AI raw pixels from the screen, but that requires massive Convolutional Neural Networks and days of training. Instead, GameBrain uses 'Vector States'."),
                    ("p", "In Flappy Bird, the state is simply 3 numbers: [Bird Y Velocity, Distance to Top Pipe, Distance to Bottom Pipe]. This is all the math the AI needs to master the game instantly!")
                ]
            },
            "batch_learning": {
                "title": "12. Batch Size & Learning Rate",
                "elements": [
                    ("p", "When the AI updates its brain, it doesn't just look at one memory. It looks at a 'Batch'. A Batch Size of 64 means it averages the error across 64 different memories before adjusting its weights."),
                    ("h2", "The Learning Rate"),
                    ("p", "The Learning Rate determines how aggressively the AI changes its weights. A rate of 0.001 is common. If the rate is too high, the AI will overreact and destroy its own knowledge. If it's too low, it will take years to learn anything.")
                ]
            },
            "overfitting": {
                "title": "13. Overfitting in RL",
                "elements": [
                    ("p", "Overfitting occurs when an AI memorizes a specific level instead of actually learning how to play the game."),
                    ("h2", "Memorization vs Generalization"),
                    ("p", "If we always spawned the Snake food in the exact same spot, the AI would learn a hardcoded path to get there. If we moved the food 1 pixel, the AI would fail completely!"),
                    ("p", "To prevent overfitting, we add randomness to our environments. The food spawns randomly, pipes appear at different heights, and the ball bounces at different angles. This forces the AI to learn 'Generalization'.")
                ]
            },
            "pytorch": {
                "title": "14. PyTorch Basics",
                "elements": [
                    ("p", "PyTorch is the Deep Learning engine that powers GameBrain. It is an open-source library developed by Meta (Facebook)."),
                    ("h2", "Tensors and GPUs"),
                    ("p", "At its core, PyTorch operates on 'Tensors', which are essentially multi-dimensional arrays (like grids of numbers). The magic of PyTorch is that it can move these Tensors to your graphics card (GPU)."),
                    ("p", "GPUs have thousands of cores that can perform millions of matrix multiplications simultaneously, which is why AI training is vastly faster on a GPU than a CPU.")
                ]
            },
            "convergence": {
                "title": "15. Convergence",
                "elements": [
                    ("p", "How do you know when an AI is 'done' training? In Reinforcement Learning, we look for 'Convergence'."),
                    ("h2", "When to Stop"),
                    ("p", "Convergence means the AI's policy has stabilized. The Average Reward plateaus at a high number, and the Loss function stops dropping. At this point, the AI has mastered the game given its current Neural Network size and State representation."),
                    ("p", "If it converges but still plays badly, you need to add more layers to the Neural Network, or redesign your Rewards!")
                ]
            }
        }