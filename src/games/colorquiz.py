"""Color Quiz — identify colors, name hex values, and learn color mixing."""
import tkinter as tk
from tkinter import ttk
import random

# 12 named colors with their hex codes
COLORS = [
    ("Rouge",      "#e74c3c"),
    ("Bleu",       "#3498db"),
    ("Vert",       "#27ae60"),
    ("Jaune",      "#f1c40f"),
    ("Orange",     "#e67e22"),
    ("Violet",     "#9b59b6"),
    ("Rose",       "#e91e63"),
    ("Cyan",       "#00bcd4"),
    ("Marron",     "#795548"),
    ("Gris",       "#95a5a6"),
    ("Blanc",      "#ffffff"),
    ("Noir",       "#212121"),
]

# Mixing rules: (color1_name, color2_name) → result_name
MIXING = [
    ("Rouge",  "Jaune",  "Orange"),
    ("Rouge",  "Bleu",   "Violet"),
    ("Bleu",   "Jaune",  "Vert"),
    ("Rouge",  "Blanc",  "Rose"),
    ("Blanc",  "Noir",   "Gris"),
]

TOTAL_QUESTIONS = 20
QUESTION_TIME   = 10   # seconds per question

MODES = ['Couleur → Nom', 'Nom → Couleur', 'Mélange']


def _make_color_to_name_question(asked: list) -> dict:
    """Show a color swatch; pick the correct name."""
    name, hexval = random.choice(COLORS)
    # 4 choices
    others = [c[0] for c in COLORS if c[0] != name]
    choices = random.sample(others, 3) + [name]
    random.shuffle(choices)
    return {'type': 'color_to_name', 'name': name, 'hex': hexval, 'choices': choices}


def _make_name_to_color_question() -> dict:
    """Show a color name; pick the correct swatch hex."""
    name, hexval = random.choice(COLORS)
    others = [c[1] for c in COLORS if c[0] != name]
    wrong_hexes = random.sample(others, 3)
    choices_hex = wrong_hexes + [hexval]
    random.shuffle(choices_hex)
    return {'type': 'name_to_color', 'name': name, 'hex': hexval,
            'choices': choices_hex}


def _make_mixing_question() -> dict:
    """What color do you get mixing A + B?"""
    c1, c2, result = random.choice(MIXING)
    others = [c[0] for c in COLORS if c not in (result, c1, c2)]
    wrong = random.sample(others, 3)
    choices = wrong + [result]
    random.shuffle(choices)
    return {'type': 'mixing', 'c1': c1, 'c2': c2, 'answer': result,
            'choices': choices}


def build_question(mode: str) -> dict:
    if mode == 'Couleur → Nom':
        return _make_color_to_name_question([])
    elif mode == 'Nom → Couleur':
        return _make_name_to_color_question()
    else:
        return _make_mixing_question()


class ColorQuizGame:
    """Color quiz game in a Toplevel window."""

    def __init__(self, parent, theme: dict):
        self.parent = parent
        self.theme = theme

        self.win = tk.Toplevel(parent)
        self.win.title("🎨 Quiz des Couleurs")
        self.win.geometry("580x520")
        self.win.resizable(False, False)
        self.win.configure(bg=theme.get('bg', '#282a36'))
        self.win.protocol('WM_DELETE_WINDOW', self._on_close)

        self.score = 0
        self.q_index = 0
        self._current_q: dict = {}
        self._answered = False
        self._timer_val = QUESTION_TIME
        self._after_id: str | None = None

        self.mode_var = tk.StringVar(value='Couleur → Nom')

        self._build_ui()
        self.start_game()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        bg     = self.theme.get('bg',         '#282a36')
        fg     = self.theme.get('fg',         '#f8f8f2')
        btn_bg = self.theme.get('btn_bg',     '#6272a4')
        btn_fg = self.theme.get('btn_fg',     '#f8f8f2')
        tb_bg  = self.theme.get('toolbar_bg', '#44475a')

        # ── Toolbar ──────────────────────────────────────────────────────────
        top = tk.Frame(self.win, bg=tb_bg)
        top.pack(fill='x')

        self.lbl_score = tk.Label(top, text="Score : 0 / 20",
                                  font=("Segoe UI", 11), bg=tb_bg, fg=fg)
        self.lbl_score.pack(side='left', padx=12, pady=6)

        self.lbl_timer = tk.Label(top, text=f"⏱ {QUESTION_TIME}s",
                                  font=("Segoe UI", 11, 'bold'), bg=tb_bg, fg='#50fa7b')
        self.lbl_timer.pack(side='left', padx=12)

        mode_frame = tk.Frame(top, bg=tb_bg)
        mode_frame.pack(side='right', padx=10)
        tk.Label(mode_frame, text="Mode :", bg=tb_bg, fg=fg,
                 font=("Segoe UI", 10)).pack(side='left')
        for m in MODES:
            tk.Radiobutton(
                mode_frame, text=m.split(' → ')[0] if '→' in m else m,
                variable=self.mode_var, value=m,
                bg=tb_bg, fg=fg, selectcolor=bg, activebackground=tb_bg,
                font=("Segoe UI", 9),
            ).pack(side='left', padx=3)

        # ── Progress ─────────────────────────────────────────────────────────
        progress_frame = tk.Frame(self.win, bg=bg)
        progress_frame.pack(fill='x', padx=20, pady=(8, 0))

        self.progress = ttk.Progressbar(progress_frame, maximum=TOTAL_QUESTIONS,
                                         length=540, mode='determinate')
        self.progress.pack(fill='x')

        # ── Question area ─────────────────────────────────────────────────────
        self.q_frame = tk.Frame(self.win, bg=bg)
        self.q_frame.pack(expand=True, fill='both', padx=20, pady=8)

        self.lbl_question = tk.Label(self.q_frame, text="",
                                     font=("Segoe UI", 14, 'bold'), bg=bg, fg=fg,
                                     wraplength=520, justify='center')
        self.lbl_question.pack(pady=(10, 6))

        self.canvas_color = tk.Canvas(self.q_frame, width=160, height=90,
                                      highlightthickness=2,
                                      highlightbackground=btn_bg)
        self.canvas_color.pack(pady=4)

        self.choices_frame = tk.Frame(self.q_frame, bg=bg)
        self.choices_frame.pack(pady=6)

        self.lbl_feedback = tk.Label(self.q_frame, text="",
                                     font=("Segoe UI", 12, 'bold'), bg=bg, fg=fg)
        self.lbl_feedback.pack(pady=4)

        # ── Bottom ────────────────────────────────────────────────────────────
        bottom = tk.Frame(self.win, bg=tb_bg)
        bottom.pack(fill='x', side='bottom')

        tk.Button(bottom, text="🔄 Recommencer",
                  font=("Segoe UI", 10), bg=btn_bg, fg=btn_fg,
                  activebackground=bg, relief='flat', padx=10, pady=4,
                  command=self.restart).pack(side='left', padx=10, pady=6)

        tk.Button(bottom, text="❌ Fermer",
                  font=("Segoe UI", 10), bg=btn_bg, fg=btn_fg,
                  activebackground=bg, relief='flat', padx=10, pady=4,
                  command=self._on_close).pack(side='right', padx=10, pady=6)

    # ── Game Core ─────────────────────────────────────────────────────────────

    def start_game(self) -> None:
        self._cancel_timer()
        self.score = 0
        self.q_index = 0
        self._answered = False
        self.progress['value'] = 0
        self._load_question()

    def restart(self) -> None:
        self.start_game()

    def _load_question(self) -> None:
        if self.q_index >= TOTAL_QUESTIONS:
            self._show_end_screen()
            return
        self._cancel_timer()
        self._answered = False
        self._timer_val = QUESTION_TIME
        self._current_q = build_question(self.mode_var.get())
        self._render_question()
        self.lbl_feedback.configure(text="")
        self.progress['value'] = self.q_index
        self._start_timer()

    def _render_question(self) -> None:
        q = self._current_q
        # Clear choices
        for w in self.choices_frame.winfo_children():
            w.destroy()

        bg     = self.theme.get('bg',         '#282a36')
        fg     = self.theme.get('fg',         '#f8f8f2')
        btn_bg = self.theme.get('btn_bg',     '#6272a4')
        btn_fg = self.theme.get('btn_fg',     '#f8f8f2')

        qtype = q['type']

        if qtype == 'color_to_name':
            self.lbl_question.configure(text=f"Question {self.q_index + 1}/{TOTAL_QUESTIONS}\nQuelle est cette couleur ?")
            self.canvas_color.configure(bg=q['hex'])
            self.canvas_color.pack()
            for choice in q['choices']:
                tk.Button(self.choices_frame, text=choice,
                          font=("Segoe UI", 12), bg=btn_bg, fg=btn_fg,
                          activebackground=bg, relief='flat', padx=14, pady=6, width=10,
                          command=lambda c=choice: self._answer(c)).pack(
                    side='left', padx=8)

        elif qtype == 'name_to_color':
            self.lbl_question.configure(
                text=f"Question {self.q_index + 1}/{TOTAL_QUESTIONS}\nQuelle case correspond à « {q['name']} » ?")
            self.canvas_color.pack_forget()
            for hexval in q['choices']:
                c = tk.Canvas(self.choices_frame, width=80, height=60,
                              bg=hexval, cursor='hand2',
                              highlightthickness=2, highlightbackground='#555')
                c.pack(side='left', padx=8)
                c.bind('<Button-1>', lambda e, h=hexval: self._answer(h))

        else:  # mixing
            self.lbl_question.configure(
                text=f"Question {self.q_index + 1}/{TOTAL_QUESTIONS}\n{q['c1']} + {q['c2']} = ?")
            self.canvas_color.pack_forget()
            for choice in q['choices']:
                tk.Button(self.choices_frame, text=choice,
                          font=("Segoe UI", 12), bg=btn_bg, fg=btn_fg,
                          activebackground=bg, relief='flat', padx=14, pady=6, width=10,
                          command=lambda c=choice: self._answer(c)).pack(
                    side='left', padx=8)

    def _get_correct(self) -> str:
        q = self._current_q
        if q['type'] == 'name_to_color':
            return q['hex']
        elif q['type'] == 'mixing':
            return q['answer']
        return q['name']

    def _answer(self, chosen: str) -> None:
        if self._answered:
            return
        self._answered = True
        self._cancel_timer()
        correct = self._get_correct()
        if chosen == correct:
            self.score += 1
            self.lbl_feedback.configure(text="✅ Bonne réponse !", fg='#50fa7b')
        else:
            if self._current_q['type'] == 'name_to_color':
                self.lbl_feedback.configure(
                    text=f"❌ C'était : {correct}", fg='#ff5555')
            else:
                self.lbl_feedback.configure(
                    text=f"❌ La bonne réponse est : {correct}", fg='#ff5555')
        self.q_index += 1
        self._update_score_label()
        self.win.after(1200, self._load_question)

    # ── Timer ─────────────────────────────────────────────────────────────────

    def _start_timer(self) -> None:
        self._tick()

    def _tick(self) -> None:
        if self._answered:
            return
        color = '#50fa7b' if self._timer_val > 4 else '#ff5555'
        self.lbl_timer.configure(text=f"⏱ {self._timer_val}s", fg=color)
        if self._timer_val <= 0:
            self._time_up()
            return
        self._timer_val -= 1
        self._after_id = self.win.after(1000, self._tick)

    def _time_up(self) -> None:
        if self._answered:
            return
        self._answered = True
        correct = self._get_correct()
        if self._current_q['type'] == 'name_to_color':
            self.lbl_feedback.configure(
                text=f"⏰ Temps écoulé ! Réponse : {correct}", fg='#ffb86c')
        else:
            self.lbl_feedback.configure(
                text=f"⏰ Temps écoulé ! Réponse : {correct}", fg='#ffb86c')
        self.q_index += 1
        self._update_score_label()
        self.win.after(1400, self._load_question)

    def _cancel_timer(self) -> None:
        if self._after_id:
            try:
                self.win.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    # ── End screen ────────────────────────────────────────────────────────────

    def _show_end_screen(self) -> None:
        self._cancel_timer()
        for w in self.q_frame.winfo_children():
            w.destroy()

        bg = self.theme.get('bg', '#282a36')
        fg = self.theme.get('fg', '#f8f8f2')
        btn_bg = self.theme.get('btn_bg', '#6272a4')
        btn_fg = self.theme.get('btn_fg', '#f8f8f2')

        pct = self.score / TOTAL_QUESTIONS
        if pct >= 0.9:
            msg = "Excellent ! Tu es un expert des couleurs ! 🎨"
            color = '#50fa7b'
        elif pct >= 0.7:
            msg = "Très bien ! Encore un peu de pratique ! 🌈"
            color = '#f1fa8c'
        elif pct >= 0.5:
            msg = "Pas mal ! Continue à apprendre ! 💪"
            color = '#ffb86c'
        else:
            msg = "Continue à t'entraîner ! 🔍"
            color = '#ff5555'

        self.progress['value'] = TOTAL_QUESTIONS
        tk.Label(self.q_frame, text="🏁 Fin du Quiz !",
                 font=("Segoe UI", 18, 'bold'), bg=bg, fg=fg).pack(pady=20)
        tk.Label(self.q_frame, text=f"Score : {self.score} / {TOTAL_QUESTIONS}",
                 font=("Segoe UI", 16), bg=bg, fg=color).pack()
        tk.Label(self.q_frame, text=msg,
                 font=("Segoe UI", 13), bg=bg, fg=fg, wraplength=480).pack(pady=10)
        tk.Button(self.q_frame, text="🔄 Rejouer",
                  font=("Segoe UI", 12), bg=btn_bg, fg=btn_fg,
                  activebackground=bg, relief='flat', padx=14, pady=6,
                  command=self.restart).pack(pady=14)

    def _update_score_label(self) -> None:
        self.lbl_score.configure(text=f"Score : {self.score} / {TOTAL_QUESTIONS}")

    def update_score(self, value: int) -> None:
        self.score = value
        self._update_score_label()

    def _on_close(self) -> None:
        self._cancel_timer()
        self.win.destroy()
