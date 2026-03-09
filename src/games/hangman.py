"""Hangman game — gallows drawn on Canvas, 40+ French words across 3 categories."""
import tkinter as tk
from tkinter import ttk
import random


WORDS = {
    'Animaux': [
        'elephant', 'girafe', 'papillon', 'crocodile', 'rhinoceros',
        'hippopotame', 'perroquet', 'tortue', 'dauphin', 'panthere',
        'kangourou', 'flamant', 'pingouin', 'autruche', 'cameleon',
    ],
    'Fruits': [
        'ananas', 'framboise', 'mangue', 'pasteque', 'grenade',
        'clementine', 'abricot', 'cerise', 'myrtille', 'kiwi',
        'mandarine', 'pamplemousse', 'litchi', 'papaye', 'grenadine',
    ],
    'Pays': [
        'france', 'espagne', 'portugal', 'maroc', 'egypte',
        'bresil', 'mexique', 'australie', 'japon', 'canada',
        'allemagne', 'italie', 'argentine', 'colombie', 'zimbabwe',
    ],
}

MAX_WRONG = 6
CANVAS_W = 300
CANVAS_H = 260


class HangmanGame:
    """Hangman game in a Toplevel window."""

    def __init__(self, parent, theme: dict):
        self.parent = parent
        self.theme = theme

        self.win = tk.Toplevel(parent)
        self.win.title("🪢 Pendu")
        self.win.geometry("650x620")
        self.win.resizable(True, True)
        self.win.configure(bg=theme.get('bg', '#282a36'))

        # Session score
        self.session_wins = 0
        self.session_games = 0

        # Game state
        self.word = ''
        self.guessed: set[str] = set()
        self.wrong_count = 0
        self._game_over = False

        self.category_var = tk.StringVar(value='Aléatoire')

        self._build_ui()
        self.start_game()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        bg = self.theme.get('bg', '#282a36')
        fg = self.theme.get('fg', '#f8f8f2')
        btn_bg = self.theme.get('btn_bg', '#6272a4')
        btn_fg = self.theme.get('btn_fg', '#f8f8f2')
        tb_bg = self.theme.get('toolbar_bg', '#44475a')

        # ── Top bar ──────────────────────────────────
        top = tk.Frame(self.win, bg=tb_bg)
        top.pack(fill='x')

        self.lbl_score = tk.Label(top, text="Score : 0 victoires / 0 parties",
                                  font=("Segoe UI", 11), bg=tb_bg, fg=fg)
        self.lbl_score.pack(side='left', padx=12, pady=6)

        self.lbl_status = tk.Label(top, text="",
                                   font=("Segoe UI", 11, "bold"), bg=tb_bg, fg='#50fa7b')
        self.lbl_status.pack(side='left', padx=12, pady=6)

        # ── Category selector ─────────────────────────
        cat_frame = tk.Frame(self.win, bg=bg)
        cat_frame.pack(fill='x', padx=12, pady=4)

        tk.Label(cat_frame, text="Catégorie :", bg=bg, fg=fg,
                 font=("Segoe UI", 10)).pack(side='left')
        for cat in list(WORDS.keys()) + ['Aléatoire']:
            tk.Radiobutton(
                cat_frame, text=cat, variable=self.category_var, value=cat,
                bg=bg, fg=fg, selectcolor=tb_bg, activebackground=bg,
                font=("Segoe UI", 10),
            ).pack(side='left', padx=6)

        # ── Main area ─────────────────────────────────
        main = tk.Frame(self.win, bg=bg)
        main.pack(fill='both', expand=True, padx=12, pady=4)

        # Canvas (left)
        canvas_frame = tk.Frame(main, bg=bg)
        canvas_frame.pack(side='left', padx=4)

        self.canvas = tk.Canvas(canvas_frame, width=CANVAS_W, height=CANVAS_H,
                                bg='white', highlightthickness=2,
                                highlightbackground=btn_bg)
        self.canvas.pack()

        # Right side
        right = tk.Frame(main, bg=bg)
        right.pack(side='left', fill='both', expand=True, padx=8)

        # Word display
        self.lbl_word = tk.Label(right, text="",
                                 font=("Courier New", 22, "bold"),
                                 bg=bg, fg=fg, pady=10)
        self.lbl_word.pack()

        # Wrong guesses
        self.lbl_wrong = tk.Label(right, text="Erreurs : 0/6",
                                  font=("Segoe UI", 10), bg=bg, fg='#ff5555')
        self.lbl_wrong.pack()

        # Letter buttons frame
        letters_outer = tk.Frame(right, bg=bg)
        letters_outer.pack(pady=6)

        self.letter_btns: dict[str, tk.Button] = {}
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        rows = [alphabet[0:9], alphabet[9:18], alphabet[18:]]
        for row_str in rows:
            row_frame = tk.Frame(letters_outer, bg=bg)
            row_frame.pack()
            for ch in row_str:
                b = tk.Button(
                    row_frame, text=ch,
                    font=("Arial", 11, "bold"),
                    width=2, height=1,
                    bg=btn_bg, fg=btn_fg,
                    activebackground=bg, relief='raised', bd=2,
                    command=lambda c=ch: self._guess(c.lower()),
                )
                b.pack(side='left', padx=2, pady=2)
                self.letter_btns[ch] = b

        # ── Bottom bar ───────────────────────────────
        bottom = tk.Frame(self.win, bg=tb_bg)
        bottom.pack(fill='x', side='bottom')

        tk.Button(bottom, text="🔄 Rejouer",
                  font=("Segoe UI", 10), bg=btn_bg, fg=btn_fg,
                  activebackground=bg, relief='flat', padx=10, pady=4,
                  command=self.restart).pack(side='left', padx=10, pady=6)

        tk.Button(bottom, text="❌ Fermer",
                  font=("Segoe UI", 10), bg=btn_bg, fg=btn_fg,
                  activebackground=bg, relief='flat', padx=10, pady=4,
                  command=self.win.destroy).pack(side='right', padx=10, pady=6)

    # ── Game logic ────────────────────────────────────────────────────────────

    def start_game(self) -> None:
        cat = self.category_var.get()
        if cat == 'Aléatoire':
            pool = [w for ws in WORDS.values() for w in ws]
        else:
            pool = WORDS.get(cat, [w for ws in WORDS.values() for w in ws])
        self.word = random.choice(pool)
        self.guessed = set()
        self.wrong_count = 0
        self._game_over = False

        self.lbl_status.configure(text="")
        self.lbl_wrong.configure(text="Erreurs : 0/6")
        self._update_word_display()
        self._reset_letter_buttons()
        self._draw_gallows()
        self._update_score_label()

    def restart(self) -> None:
        self.start_game()

    # ── Guessing ─────────────────────────────────────────────────────────────

    def _guess(self, letter: str) -> None:
        if self._game_over or letter in self.guessed:
            return
        self.guessed.add(letter)
        btn_key = letter.upper()
        if letter in self.word:
            self.letter_btns[btn_key].configure(bg='#50fa7b', fg='#1a1a2e', state='disabled')
            self._update_word_display()
            if all(c in self.guessed or c == ' ' for c in self.word):
                self._win()
        else:
            self.wrong_count += 1
            self.letter_btns[btn_key].configure(bg='#ff5555', fg='white', state='disabled')
            self.lbl_wrong.configure(text=f"Erreurs : {self.wrong_count}/{MAX_WRONG}")
            self._draw_hangman_part(self.wrong_count)
            if self.wrong_count >= MAX_WRONG:
                self._lose()

    # ── Drawing ───────────────────────────────────────────────────────────────

    def _draw_gallows(self) -> None:
        self.canvas.delete('all')
        # Base
        self.canvas.create_line(20, 240, 180, 240, width=4, fill='#333')
        # Vertical pole
        self.canvas.create_line(60, 240, 60, 20, width=4, fill='#333')
        # Horizontal beam
        self.canvas.create_line(60, 20, 180, 20, width=4, fill='#333')
        # Rope
        self.canvas.create_line(180, 20, 180, 50, width=3, fill='#333')

    def _draw_hangman_part(self, part: int) -> None:
        c = self.canvas
        if part == 1:   # Head
            c.create_oval(158, 50, 202, 94, width=3, outline='#333')
        elif part == 2: # Body
            c.create_line(180, 94, 180, 160, width=3, fill='#333')
        elif part == 3: # Left arm
            c.create_line(180, 110, 148, 140, width=3, fill='#333')
        elif part == 4: # Right arm
            c.create_line(180, 110, 212, 140, width=3, fill='#333')
        elif part == 5: # Left leg
            c.create_line(180, 160, 148, 200, width=3, fill='#333')
        elif part == 6: # Right leg
            c.create_line(180, 160, 212, 200, width=3, fill='#333')

    # ── Word display ─────────────────────────────────────────────────────────

    def _update_word_display(self) -> None:
        display = '  '.join(
            (c if c in self.guessed or c == ' ' else '_')
            for c in self.word
        )
        self.lbl_word.configure(text=display)

    def _reset_letter_buttons(self) -> None:
        btn_bg = self.theme.get('btn_bg', '#6272a4')
        btn_fg = self.theme.get('btn_fg', '#f8f8f2')
        for b in self.letter_btns.values():
            b.configure(bg=btn_bg, fg=btn_fg, state='normal')

    # ── Win / Lose ────────────────────────────────────────────────────────────

    def _win(self) -> None:
        self._game_over = True
        self.session_wins += 1
        self.session_games += 1
        self._update_score_label()
        self.lbl_status.configure(
            text=f"🎉 Bravo ! Le mot était : {self.word.upper()}", fg='#50fa7b'
        )
        self._disable_all_buttons()

    def _lose(self) -> None:
        self._game_over = True
        self.session_games += 1
        self._update_score_label()
        # Reveal word
        self.lbl_word.configure(
            text='  '.join(self.word.upper())
        )
        self.lbl_status.configure(
            text=f"💀 Perdu ! Le mot était : {self.word.upper()}", fg='#ff5555'
        )
        self._disable_all_buttons()

    def _disable_all_buttons(self) -> None:
        for b in self.letter_btns.values():
            b.configure(state='disabled')

    def _update_score_label(self) -> None:
        self.lbl_score.configure(
            text=f"Score : {self.session_wins} victoires / {self.session_games} parties"
        )

    def update_score(self, value) -> None:
        pass
