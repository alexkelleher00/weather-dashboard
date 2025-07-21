import tkinter as tk
from tkinter import messagebox

class ScoreboardApp:
    def __init__(self, root, back_callback=None):
        self.root = root
        self.back_callback = back_callback
        self.root.title("Scoreboard")
        self.root.attributes('-fullscreen', True)
        # Default configurations
        self.team_names = ["Team 1", "Team 2"]
        self.scores = [0, 0]
        self.game_finish_score = 7

        self.home_screen()

    def home_screen(self):
        """Creates the home screen for selecting game points and team names"""
        self.clear_screen()
        if self.back_callback:
            back_button = tk.Button(self.root, text="Back to Dashboard", command=self.back_callback)
            back_button.pack(pady=10)

        # Title Label
        title_label = tk.Label(self.root, text="Punks Scoreboard", font=("Arial", 24))
        title_label.pack(pady=20)

        # Point total options
        point_label = tk.Label(self.root, text="Select Game Finish Points:", font=("Arial", 14))
        point_label.pack()

        point_button_frame = tk.Frame(self.root)
        point_button_frame.pack(pady=10)

        points = [7, 11, 15, 21]
        for point in points:
            button = tk.Button(point_button_frame, text=str(point), command=lambda p=point: self.set_game_finish_score(p))
            button.pack(side=tk.LEFT, padx=5)

        # Label for showing the current game score
        self.current_score_label = tk.Label(self.root, text=f"Current Game Finish Score: {self.game_finish_score}")
        self.current_score_label.pack(pady=10)

        # Add team names input
        team_label = tk.Label(self.root, text="Enter Team Names (Leave blank for default teams):")
        team_label.pack(pady=10)

        # Create frame to hold team entries
        self.team_frame = tk.Frame(self.root)
        self.team_frame.pack(pady=5)

        self.team_name_entries = []
        for i in range(2):
            entry = tk.Entry(self.team_frame)
            entry.insert(tk.END, f"Team {i + 1}")
            entry.grid(row=i, column=0, pady=5, padx=10)
            self.team_name_entries.append(entry)

            # Button to remove team
            remove_button = tk.Button(self.team_frame, text="Remove", command=lambda i=i: self.remove_team(i))
            remove_button.grid(row=i, column=1, padx=10)

        # Button to add another team
        add_team_button = tk.Button(self.root, text="Add Team", command=self.add_team)
        add_team_button.pack(pady=5)

        # Button to start the game
        start_button = tk.Button(self.root, text="Start Game", command=self.start_game)
        start_button.pack(pady=25)

    def set_game_finish_score(self, score):
        """Sets the game finish score based on user selection"""
        self.game_finish_score = score
        self.current_score_label.config(text=f"Current Game Finish Score: {self.game_finish_score}")

    def start_game(self):
        """Starts the game and transitions to the game screen"""
        team_names = [entry.get() for entry in self.team_name_entries]
        self.team_names = [name if name else f"Team {i+1}" for i, name in enumerate(team_names)]
        self.scores = [0] * len(self.team_names)

        self.game_screen()

    def game_screen(self):
        """Creates the game screen with scores and buttons to control the game"""
        self.clear_screen()

        score_frame = tk.Frame(self.root)
        score_frame.pack(pady=25)

        self.score_labels = []
        team_colors = ["red", "blue", "green", "purple", "orange", "darkgreen"]

        for i, team_name in enumerate(self.team_names):
            team_color = team_colors[i % len(team_colors)]

            team_label = tk.Label(score_frame, text=team_name, font=("Arial", 28, "bold"), fg=team_color)
            team_label.grid(row=i, column=0, padx=20)

            score_label = tk.Label(score_frame, text=str(self.scores[i]), font=("Arial", 28), fg=team_color)
            score_label.grid(row=i, column=1, padx=20)
            self.score_labels.append(score_label)

            # Large buttons
            increase_button = tk.Button(score_frame, text="+1", font=("Arial", 24), bg=team_color,
                                        command=lambda i=i: self.change_score(i, 1), width=10, height=2)
            increase_button.grid(row=i, column=2, padx=10)

            decrease_button = tk.Button(score_frame, text="-1", font=("Arial", 24), bg=team_color,
                                        command=lambda i=i: self.change_score(i, -1), width=10, height=2)
            decrease_button.grid(row=i, column=3, padx=10)

        total_game_score_label = tk.Label(self.root, text=f"Play To: {self.game_finish_score} Points", font=("Arial", 18))
        total_game_score_label.pack(pady=10)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        reset_button = tk.Button(button_frame, text="Reset Game", font=("Arial", 14), width=15, command=self.reset_game)
        reset_button.pack(side=tk.LEFT, padx=20)

        home_button = tk.Button(button_frame, text="Back to Home", font=("Arial", 14), width=15, command=self.home_screen)
        home_button.pack(side=tk.LEFT, padx=20)

    def change_score(self, team_index, change):
        """Changes the score of a team by the specified amount"""
        self.scores[team_index] += change
        self.score_labels[team_index].config(text=str(self.scores[team_index]))
        self.check_game_over()

    def reset_game(self):
        """Resets the game scores"""
        self.scores = [0] * len(self.team_names)
        for i, score_label in enumerate(self.score_labels):
            score_label.config(text="0")

    def check_game_over(self):
        """Checks if any team has reached the finish score"""
        for i, score in enumerate(self.scores):
            if score >= self.game_finish_score:
                messagebox.showinfo("Game Over", f"{self.team_names[i]} has won the game!")
                self.reset_game()

    def add_team(self):
        """Adds a new team to the game"""
        new_team_name = f"Team {len(self.team_names) + 1}"
        self.team_names.append(new_team_name)
        self.scores.append(0)

        # Create a new team name entry field in the existing frame
        row_num = len(self.team_names) - 1  # Determine where the new entry goes

        # Create the new team entry
        entry = tk.Entry(self.team_frame)
        entry.insert(tk.END, new_team_name)
        entry.grid(row=row_num, column=0, pady=5, padx=10)
        self.team_name_entries.append(entry)

        # Button to remove the new team
        remove_button = tk.Button(self.team_frame, text="Remove", command=lambda i=row_num: self.remove_team(i))
        remove_button.grid(row=row_num, column=1, padx=10)

    def remove_team(self, team_index):
        """Removes a team and refreshes the team entry UI"""
        if len(self.team_names) > 2:
            self.team_names.pop(team_index)
            self.scores.pop(team_index)
            self.team_name_entries.pop(team_index)

            # Clear the team frame
            for widget in self.team_frame.winfo_children():
                widget.destroy()

            # Recreate the team entry fields and remove buttons
            self.team_name_entries = []
            for i, name in enumerate(self.team_names):
                entry = tk.Entry(self.team_frame)
                entry.insert(tk.END, name)
                entry.grid(row=i, column=0, pady=5, padx=10)
                self.team_name_entries.append(entry)

                remove_button = tk.Button(self.team_frame, text="Remove", command=lambda i=i: self.remove_team(i))
                remove_button.grid(row=i, column=1, padx=10)

    def clear_screen(self):
        """Clears the current screen widgets"""
        for widget in self.root.winfo_children():
            widget.destroy()