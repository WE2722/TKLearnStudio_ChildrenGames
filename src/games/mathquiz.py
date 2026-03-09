"""Math Quiz — arithmetic questions at 4 school levels with speed bonus."""
import tkinter as tk
from tkinter import ttk
import random
import time

TOTAL_QUESTIONS = 20
QUESTION_TIME   = 30   # seconds per question
SPEED_BONUS_SEC = 5    # answer within 5s → +2 bonus pts

# Level definitions: (label, operations, operand_range)
LEVELS = {
    'CP':  {'label': 'CP  (6-7 ans)',   'ops': ['+', '-'],          'max': 10,  'mul_max': 0},
    'CE1': {'label': 'CE1 (7-8 ans)',   'ops': ['+', '-'],          'max': 20,  'mul_max': 0},
    'CE2': {'label': 'CE2 (8-9 ans)',   'ops': ['+', '-', '×'],     'max': 50,  'mul_max': 10},
    'CM':  {'label': 'CM  (9-11 ans)',  'ops': ['+', '-', '×', '÷'],'max': 100, 'mul_max': 12},
}

STAR_THRESHOLDS = [0, 10, 15, 18, 20]   # stars: 0→1★, 1→2★ ... (index = score needed)


def generate_question(level: str) -> dict:
    """Return dict with keys: question (str), answer (int), op (str), a (int), b (int)."""
    cfg = LEVELS[level]
    op = random.choice(cfg['ops'])
    if op == '+':
        a = random.randint(1, cfg['max'])
        b = random.randint(1, cfg['max'])
        ans = a + b
    elif op == '-':
        a = random.randint(1, cfg['max'])
        b = random.randint(1, a)          # ensure non-negative result
        ans = a - b
    elif op == '×':
        a = random.randint(1, cfg['mul_max'])
        b = random.randint(1, cfg['mul_max'])
        ans = a * b
    else:  # ÷
        b = random.randint(1, cfg['mul_max'])
        ans = random.randint(1, cfg['mul_max'])
        a = ans * b                         # guarantee exact division
    return {'question': f"{a} {op} {b} = ?", 'answer': ans, 'op': op, 'a': a, 'b': b}


def count_stars(score: int) -> int:
    """Return 1–4 stars based on score."""
    if score >= 18:
        return 4
    if score >= 15:
        return 3
    if score >= 10:
        return 2
    return 1


class MathQuizGame:
    """Math quiz game in a Toplevel window."""

    def __init__(self, parent, theme: dict):
        self.parent = parent
        self.theme = theme

        self.win = tk.Toplevel(parent)
        self.win.title("🔢 Quiz de Maths")
        self.win.geometry("520x480")
        self.win.resizable(False, False)
        self.win.configure(bg=theme.get('bg', '#282a36'))
        self.win.protocol('WM_DELETE_WINDOW', self._on_close)

        self.score = 0
        self.q_index = 0
        self._current_q: dict = {}
        self._answered = False
        self._timer_val = QUESTION_TIME
        self._q_start: float = 0.0
        self._after_id: str | None = None

        self.level_var = tk.StringVar(value='CE1')

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

        level_frame = tk.Frame(top, bg=tb_bg)
        level_frame.pack(side='right', padx=10)
        tk.Label(level_frame, text="Niveau :", bg=tb_bg, fg=fg,
                 font=("Segoe UI", 10)).pack(side='left')
        for lvl in LEVELS:
            tk.Radiobutton(
                level_frame, text=lvl, variable=self.level_var, value=lvl,
                bg=tb_bg, fg=fg, selectcolor=bg, activebackground=tb_bg,
                font=("Segoe UI", 10),
            ).pack(side='left', padx=3)

        # ── Progress ─────────────────────────────────────────────────────────
        pf = tk.Frame(self.win, bg=bg)
        pf.pack(fill='x', padx=20, pady=(8, 0))
        self.progress = ttk.Progressbar(pf, maximum=TOTAL_QUESTIONS,
                                         length=480, mode='determinate')
        self.progress.pack(fill='x')

        # ── Question area ─────────────────────────────────────────────────────
        self.q_frame = tk.Frame(self.win, bg=bg)
        self.q_frame.pack(expand=True, fill='both', padx=20, pady=8)

        self.lbl_question = tk.Label(self.q_frame, text="",
                                     font=("Segoe UI", 32, 'bold'), bg=bg, fg=fg)
        self.lbl_question.pack(pady=(20, 8))

        entry_frame = tk.Frame(self.q_frame, bg=bg)
        entry_frame.pack(pady=4)

        self.entry = tk.Entry(entry_frame, font=("Segoe UI", 20), width=8,
                              justify='center', bd=2, relief='groove')
        self.entry.pack(side='left', padx=6)
        self.entry.bind('<Return>', lambda e: self._submit())

        tk.Button(entry_frame, text="Valider",
                  font=("Segoe UI", 12), bg=self.theme.get('btn_bg', '#6272a4'),
                  fg=btn_fg, activebackground=bg, relief='flat', padx=10, pady=4,
                  command=self._submit).pack(side='left', padx=6)

        self.lbl_feedback = tk.Label(self.q_frame, text="",
                                     font=("Segoe UI", 13, 'bold'), bg=bg, fg=fg)
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
        self._q_start = time.monotonic()
        self._current_q = generate_question(self.level_var.get())
        self.lbl_question.configure(text=self._current_q['question'])
        self.lbl_feedback.configure(text="")
        self.entry.delete(0, 'end')
        self.entry.configure(state='normal')
        self.entry.focus_set()
        self.progress['value'] = self.q_index
        self._start_timer()

    def _submit(self) -> None:
        if self._answered:
            return
        raw = self.entry.get().strip()
        if not raw:
            return
        # Validate integer input
        if not raw.lstrip('-').isdigit():
            self.lbl_feedback.configure(text="⚠ Entrez un nombre entier.", fg='#ffb86c')
            return
        self._answered = True
        self._cancel_timer()
        self.entry.configure(state='disabled')
        answer = int(raw)
        correct = self._current_q['answer']
        if answer == correct:
            elapsed = time.monotonic() - self._q_start
            bonus = 2 if elapsed <= SPEED_BONUS_SEC else 0
            self.score += 1 + bonus
            if bonus:
                self.lbl_feedback.configure(
                    text=f"✅ Correct ! +{1+bonus} pts (rapidité !)", fg='#50fa7b')
            else:
                self.lbl_feedback.configure(text="✅ Correct ! +1 pt", fg='#50fa7b')
        else:
            self.lbl_feedback.configure(
                text=f"❌ La réponse était {correct}", fg='#ff5555')
        self.q_index += 1
        self._update_score_label()
        self.win.after(1300, self._load_question)

    # ── Timer ─────────────────────────────────────────────────────────────────

    def _start_timer(self) -> None:
        self._tick()

    def _tick(self) -> None:
        if self._answered:
            return
        color = '#50fa7b' if self._timer_val > 9 else '#ff5555'
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
        self.entry.configure(state='disabled')
        correct = self._current_q['answer']
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

        bg     = self.theme.get('bg',         '#282a36')
        fg     = self.theme.get('fg',         '#f8f8f2')
        btn_bg = self.theme.get('btn_bg',     '#6272a4')
        btn_fg = self.theme.get('btn_fg',     '#f8f8f2')

        stars = count_stars(self.score)
        star_str = '⭐' * stars
        if stars == 4:
            msg = "Parfait ! Tu es un génie des maths ! 🧠"
            color = '#50fa7b'
        elif stars == 3:
            msg = "Très bien ! Encore un peu d'entraînement ! 📚"
            color = '#f1fa8c'
        elif stars == 2:
            msg = "Bien ! Continue à pratiquer ! 💪"
            color = '#ffb86c'
        else:
            msg = "Continue de t'entraîner, tu vas progresser ! 🔢"
            color = '#ff5555'

        self.progress['value'] = TOTAL_QUESTIONS
        tk.Label(self.q_frame, text="🏁 Fin du Quiz !",
                 font=("Segoe UI", 18, 'bold'), bg=bg, fg=fg).pack(pady=16)
        tk.Label(self.q_frame, text=star_str,
                 font=("Segoe UI", 28), bg=bg, fg='#f1fa8c').pack()
        tk.Label(self.q_frame, text=f"Score : {self.score} pts",
                 font=("Segoe UI", 16), bg=bg, fg=color).pack(pady=4)
        tk.Label(self.q_frame, text=msg,
                 font=("Segoe UI", 12), bg=bg, fg=fg, wraplength=460).pack(pady=8)
        tk.Button(self.q_frame, text="🔄 Rejouer",
                  font=("Segoe UI", 12), bg=btn_bg, fg=btn_fg,
                  activebackground=bg, relief='flat', padx=14, pady=6,
                  command=self.restart).pack(pady=12)

    def _update_score_label(self) -> None:
        self.lbl_score.configure(text=f"Score : {self.score} / {TOTAL_QUESTIONS}")

    def update_score(self, value: int) -> None:
        self.score = value
        self._update_score_label()

    def _on_close(self) -> None:
        self._cancel_timer()
        self.win.destroy()
