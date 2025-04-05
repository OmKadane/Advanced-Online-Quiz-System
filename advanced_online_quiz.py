import tkinter as tk, random, sqlite3
from tkinter import simpledialog, messagebox

# Database setup
conn = sqlite3.connect("quiz_scores.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS scores(name TEXT, score INTEGER)")
conn.commit()

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.i = 0
        self.s = 0
        self.time_left = 20
        self.timer_event = None  # Store the timer event ID for cancellation
        self.root.title("Quiz")
        self.root.geometry("400x300")
        self.root.config(bg="lightblue")

        # Get player name
        self.player_name = simpledialog.askstring("Player Name", "Enter your name:", parent=root)
        if not self.player_name:
            self.player_name = "Player"

        # Quiz questions and answers (last option is correct)
        self.q = {
            "What is the capital of Japan?": ["Tokyo", "Kyoto", "Osaka", "Nagoya", "Tokyo"],
            "Who developed Python?": ["Dennis Ritchie", "James Gosling", "Bjarne Stroustrup", "Guido van Rossum", "Guido van Rossum"],
            "Which planet is known as the Red Planet?": ["Earth", "Mars", "Jupiter", "Venus", "Mars"],
            "What is the largest ocean on Earth?": ["Indian", "Atlantic", "Pacific", "Arctic", "Pacific"],
            "What is the national animal of India?": ["Tiger", "Elephant", "Lion", "Leopard", "Tiger"]
        }

        self.quiz = random.sample(list(self.q.items()), len(self.q))

        self.q_label = tk.Label(root, font=("Arial", 14), wraplength=400)
        self.q_label.pack(pady=20)

        self.btns = [tk.Button(root, font=("Arial", 12), width=20) for _ in range(4)]
        for b in self.btns:
            b.pack(pady=5)

        self.timer_label = tk.Label(root, font=("Arial", 12))
        self.timer_label.pack(pady=5)

        self.next_q()

    def next_q(self):
        if self.i == len(self.quiz):
            return self.end_quiz()

        q, opts = self.quiz[self.i]
        self.correct_ans = opts[4].strip().lower()

        self.q_label.config(text=f"Q{self.i + 1}/{len(self.quiz)}: {q}")
        random.shuffle(opts[:4])

        for b, opt in zip(self.btns, opts[:4]):
            b.config(text=opt, command=lambda o=opt: self.check_ans(o))

        self.time_left = 20

        if self.timer_event:
            self.root.after_cancel(self.timer_event)

        self.update_timer()

    def check_ans(self, o):
        if o.strip().lower() == self.correct_ans:
            self.s += 1
        self.i += 1

        if self.timer_event:
            self.root.after_cancel(self.timer_event)

        self.next_q()

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_label.config(text=f"Time: {self.time_left}s")
            self.timer_event = self.root.after(1000, self.update_timer)
        else:
            self.i += 1
            self.next_q()

    def end_quiz(self):
        cursor.execute("INSERT INTO scores VALUES(?, ?)", (self.player_name, self.s))
        conn.commit()

        messagebox.showinfo("Quiz Over", f"{self.player_name}, Your score: {self.s}/{len(self.quiz)}")

        cursor.execute("SELECT * FROM scores ORDER BY score DESC LIMIT 5")
        scores = cursor.fetchall()
        leaderboard = "\n".join(f"{idx+1}. {name} - {score}" for idx, (name, score) in enumerate(scores))
        messagebox.showinfo("Leaderboard", f"Leaderboard:\n{leaderboard}")

        # Ask to restart the quiz
        if messagebox.askyesno("Play Again?", "Do you want to play again?"):
            self.i = 0
            self.s = 0
            self.quiz = random.sample(list(self.q.items()), len(self.q))
            self.next_q()
        else:
            conn.close()
            self.root.quit()

root = tk.Tk()
QuizApp(root)
root.mainloop()
