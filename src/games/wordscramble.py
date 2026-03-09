"""Word Scramble — unscramble letters with hints and animated feedback."""
import tkinter as tk
from tkinter import ttk
import random

# 40 French words across 4 categories (10 each)
WORDS: dict[str, list[str]] = {
    'Animaux': [
        'CHAT', 'CHIEN', 'LAPIN', 'POULE', 'VACHE',
        'CANARD', 'MOUTON', 'CHEVAL', 'COCHON', 'GRENOUILLE',
    ],
    'Fruits': [
        'POMME', 'POIRE', 'BANANE', 'RAISIN', 'CITRON',
        'PECHE', 'MELON', 'FIGUE', 'MANGUE', 'CERISE',
    ],
    'Couleurs': [
        'ROUGE', 'BLEU', 'VERT', 'JAUNE', 'BLANC',
        'NOIR', 'ORANGE', 'VIOLET', 'ROSE', 'GRIS',
    ],
    'École': [
        'LIVRE', 'STYLO', 'CAHIER', 'TABLE', 'CHAISE',
        'CRAYON', 'GOMME', 'REGLE', 'CARTABLE', 'ARDOISE',
    ],
}

ALL_WORDS: list[tuple[str, str]] = [
    (cat, word) for cat, words in WORDS.items() for word in words
]

TOTAL_WORDS   = 20
WORD_TIME     = 60    # seconds per word
HINT_PENALTY  = 2     # points deducted per hint used

LETTER_COLORS = ['#e74c3c', '#3498db', '#27ae60', '#f39c12',
                 '#9b59b6', '#1abc9c', '#e67e22', '#2980b9']


def scramble(word: str) -> str:
    """Fisher-Yates shuffle guaranteed to differ from original."""
    letters = list(word)
    for attempt in range(200):
        random.shuffle(letters)
        if letters != list(word):
            return ''.join(letters)
    # Fallback: rotate by 1 (always differs for len >= 2)
    letters = list(word)
    letters.append(letters.pop(0))
    return ''.join(letters)


class WordScrambleGame:
    """Word Scramble game in a Toplevel window."""

    def __init__(self, parent, theme: dict):
        self.parent = parent
        self.theme = theme

        self.win = tk.Toplevel(parent)
        self.win.title("🔤 Mots Mêlés")
        self.win.geometry("580x520")
        self.win.resizable(False, False)
        self.win.configure(bg=theme.get('bg', '#282a36'))
        self.win.protocol('WM_DELETE_WINDOW', self._on_close)

        self.score = 0
        self.w_index = 0
        self._word_pool: list[tuple[str, str]] = []
        self._current_word = ''
        self._current_cat  = ''
        self._scrambled    = ''
        self._hints_used   = 0
        self._answered     = False
        self._timer_val    = WORD_TIME
        self._after_id: str | None = None

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

        self.lbl_score = tk.Label(top, text="Score : 0",
                                  font=("Segoe UI", 11), bg=tb_bg, fg=fg)
        self.lbl_score.pack(side='left', padx=12, pady=6)

        self.lbl_timer = tk.Label(top, text=f"⏱ {WORD_TIME}s",
                                  font=("Segoe UI", 11, 'bold'), bg=tb_bg, fg='#50fa7b')
        self.lbl_timer.pack(side='left', padx=12)

        self.lbl_cat = tk.Label(top, text="",
                                font=("Segoe UI", 10, 'italic'), bg=tb_bg, fg=fg)
        self.lbl_cat.pack(side='right', padx=12)

        # ── Progress ─────────────────────────────────────────────────────────
        pf = tk.Frame(self.win, bg=bg)
        pf.pack(fill='x', padx=20, pady=(8, 0))
        self.progress = ttk.Progressbar(pf, maximum=TOTAL_WORDS,
                                         length=540, mode='determinate')
        self.progress.pack(fill='x')

        # ── Main area ─────────────────────────────────────────────────────────
        main = tk.Frame(self.win, bg=bg)
        main.pack(expand=True, fill='both', padx=20, pady=6)

        self.lbl_qnum = tk.Label(main, text="",
                                 font=("Segoe UI", 11), bg=bg, fg=self.theme.get('toolbar_bg', '#44475a'))
        self.lbl_qnum.pack()

        # Scrambled letters display (colored tiles)
        self.tiles_frame = tk.Frame(main, bg=bg)
        self.tiles_frame.pack(pady=8)

        # Hint area — shows progressively revealed letters
        self.lbl_hint = tk.Label(main, text="",
                                 font=("Segoe UI", 14, 'bold'), bg=bg, fg='#f1fa8c')
        self.lbl_hint.pack(pady=2)

        # Entry
        entry_frame = tk.Frame(main, bg=bg)
        entry_frame.pack(pady=6)

        self.entry = tk.Entry(entry_frame, font=("Segoe UI", 18), width=14,
                              justify='center', bd=2, relief='groove')
        self.entry.pack(side='left', padx=6)
        self.entry.bind('<Return>', lambda e: self._submit())

        tk.Button(entry_frame, text="Valider",
                  font=("Segoe UI", 11), bg=self.theme.get('btn_bg', '#6272a4'),
                  fg=btn_fg, activebackground=bg, relief='flat', padx=10, pady=4,
                  command=self._submit).pack(side='left', padx=4)

        tk.Button(entry_frame, text=f"💡 Indice (−{HINT_PENALTY})",
                  font=("Segoe UI", 11), bg=self.theme.get('toolbar_bg', '#44475a'),
                  fg=fg, activebackground=bg, relief='flat', padx=8, pady=4,
                  command=self._give_hint).pack(side='left', padx=4)

        self.lbl_feedback = tk.Label(main, text="",
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
        self.w_index = 0
        self._word_pool = random.sample(ALL_WORDS, TOTAL_WORDS)
        self.progress['value'] = 0
        self._load_word()

    def restart(self) -> None:
        self.start_game()

    def _load_word(self) -> None:
        if self.w_index >= TOTAL_WORDS:
            self._show_end_screen()
            return
        self._cancel_timer()
        self._answered = False
        self._hints_used = 0
        self._timer_val = WORD_TIME

        self._current_cat, self._current_word = self._word_pool[self.w_index]
        self._scrambled = scramble(self._current_word)

        self.lbl_cat.configure(text=f"Catégorie : {self._current_cat}")
        self.lbl_qnum.configure(text=f"Mot {self.w_index + 1} / {TOTAL_WORDS}")
        self.lbl_hint.configure(text="")
        self.lbl_feedback.configure(text="")
        self.entry.delete(0, 'end')
        self.entry.configure(state='normal')
        self.entry.focus_set()
        self.progress['value'] = self.w_index

        self._render_tiles()
        self._start_timer()

    def _render_tiles(self) -> None:
        for w in self.tiles_frame.winfo_children():
            w.destroy()
        for i, letter in enumerate(self._scrambled):
            color = LETTER_COLORS[i % len(LETTER_COLORS)]
            lbl = tk.Label(self.tiles_frame, text=letter,
                           font=("Segoe UI", 22, 'bold'),
                           bg=color, fg='white',
                           width=2, relief='raised', padx=4, pady=6)
            lbl.pack(side='left', padx=3)

    def _give_hint(self) -> None:
        if self._answered:
            return
        word = self._current_word
        revealed = self._hints_used + 1
        if revealed > len(word):
            return
        hint_text = ' '.join(
            letter if i < revealed else '_'
            for i, letter in enumerate(word)
        )
        self.lbl_hint.configure(text=hint_text)
        self._hints_used = revealed
        self._update_score_label()

    def _submit(self) -> None:
        if self._answered:
            return
        raw = self.entry.get().strip().upper()
        if not raw:
            return
        self._cancel_timer()
        self._answered = True
        self.entry.configure(state='disabled')

        if raw == self._current_word:
            pts = max(1, 10 - self._hints_used * HINT_PENALTY)
            self.score += pts
            self.lbl_feedback.configure(text=f"✅ Bravo ! +{pts} pts", fg='#50fa7b')
            self._animate_correct(0)
        else:
            self.lbl_feedback.configure(
                text=f"❌ Le mot était : {self._current_word}", fg='#ff5555')
            self.w_index += 1
            self._update_score_label()
            self.win.after(1400, self._load_word)

    def _animate_correct(self, step: int) -> None:
        """Flash tiles green one by one then advance."""
        tiles = self.tiles_frame.winfo_children()
        if step < len(tiles):
            tiles[step].configure(bg='#50fa7b')
            self.win.after(80, self._animate_correct, step + 1)
        else:
            self.w_index += 1
            self._update_score_label()
            self.win.after(400, self._load_word)

    # ── Timer ─────────────────────────────────────────────────────────────────

    def _start_timer(self) -> None:
        self._tick()

    def _tick(self) -> None:
        if self._answered:
            return
        color = '#50fa7b' if self._timer_val > 10 else '#ff5555'
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
        self.lbl_feedback.configure(
            text=f"⏰ Temps écoulé ! Mot : {self._current_word}", fg='#ffb86c')
        self.w_index += 1
        self._update_score_label()
        self.win.after(1400, self._load_word)

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
        for w in self.tiles_frame.winfo_children():
            w.destroy()
        self.lbl_qnum.configure(text="")
        self.lbl_cat.configure(text="")
        self.lbl_hint.configure(text="")
        self.lbl_feedback.configure(text="")
        self.entry.configure(state='disabled')

        bg     = self.theme.get('bg',         '#282a36')
        fg     = self.theme.get('fg',         '#f8f8f2')
        btn_bg = self.theme.get('btn_bg',     '#6272a4')
        btn_fg = self.theme.get('btn_fg',     '#f8f8f2')

        max_score = TOTAL_WORDS * 10
        pct = self.score / max_score
        if pct >= 0.85:
            msg = "Champion(ne) ! Vocabulaire parfait ! 🏆"
            color = '#50fa7b'
        elif pct >= 0.6:
            msg = "Très bien ! Un peu plus et tu seras champion(ne) ! 🌟"
            color = '#f1fa8c'
        else:
            msg = "Continue à apprendre du vocabulaire ! 📚"
            color = '#ffb86c'

        self.progress['value'] = TOTAL_WORDS
        # Show in a temporary overlay frame inside tiles_frame area
        end_frame = tk.Frame(self.win, bg=bg)
        end_frame.place(relx=0.5, rely=0.45, anchor='center')

        tk.Label(end_frame, text="🏁 Fin du jeu !",
                 font=("Segoe UI", 18, 'bold'), bg=bg, fg=fg).pack(pady=10)
        tk.Label(end_frame, text=f"Score : {self.score} / {max_score}",
                 font=("Segoe UI", 16), bg=bg, fg=color).pack()
        tk.Label(end_frame, text=msg,
                 font=("Segoe UI", 12), bg=bg, fg=fg, wraplength=480).pack(pady=8)
        tk.Button(end_frame, text="🔄 Rejouer",
                  font=("Segoe UI", 12), bg=btn_bg, fg=btn_fg,
                  activebackground=bg, relief='flat', padx=14, pady=6,
                  command=lambda: (end_frame.destroy(), self.restart())).pack(pady=10)

    def _update_score_label(self) -> None:
        self.lbl_score.configure(text=f"Score : {self.score}")

    def update_score(self, value: int) -> None:
        self.score = value
        self._update_score_label()

    def _on_close(self) -> None:
        self._cancel_timer()
        self.win.destroy()
