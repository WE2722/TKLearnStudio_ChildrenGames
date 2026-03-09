"""Memory Card Game — flip matching pairs."""
import tkinter as tk
from tkinter import ttk
import random
import time


EMOJIS_NORMAL = ['🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼']
EMOJIS_EXTENDED = [
    '🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼',
    '🐨', '🐯', '🦁', '🐮', '🐷', '🐸', '🐵', '🦋',
    '🌸', '🌺',
]

DIFFICULTY = {
    'Facile':    {'grid': 4, 'pairs': 8,  'emojis': EMOJIS_NORMAL,   'flip_delay': 2000},
    'Moyen':     {'grid': 4, 'pairs': 8,  'emojis': EMOJIS_NORMAL,   'flip_delay': 1000},
    'Difficile': {'grid': 6, 'pairs': 18, 'emojis': EMOJIS_EXTENDED, 'flip_delay': 800},
}

CARD_W = 90
CARD_H = 90


class MemoryGame:
    """Memory card matching game in a Toplevel window."""

    def __init__(self, parent, theme: dict):
        self.parent = parent
        self.theme = theme

        self.win = tk.Toplevel(parent)
        self.win.title("🃏 Jeu de Mémoire")
        self.win.resizable(True, True)
        self.win.configure(bg=theme.get('bg', '#282a36'))

        self.difficulty_var = tk.StringVar(value='Moyen')

        # State
        self.cards: list[dict] = []      # each: {emoji, btn, matched, revealed}
        self.flipped: list[int] = []     # indices of face-up unmatched cards
        self.pairs_found = 0
        self.attempts = 0
        self.elapsed = 0
        self._timer_id = None
        self._won = False
        self._locked = False             # block clicks while flipping back

        self._build_ui()
        self.start_game()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        bg = self.theme.get('bg', '#282a36')
        fg = self.theme.get('fg', '#f8f8f2')
        btn_bg = self.theme.get('btn_bg', '#6272a4')
        btn_fg = self.theme.get('btn_fg', '#f8f8f2')
        tb_bg = self.theme.get('toolbar_bg', '#44475a')

        top = tk.Frame(self.win, bg=tb_bg)
        top.pack(fill='x')

        self.lbl_score = tk.Label(top, text="Paires : 0/8 | Essais : 0",
                                  font=("Segoe UI", 11), bg=tb_bg, fg=fg)
        self.lbl_score.pack(side='left', padx=12, pady=6)

        self.lbl_timer = tk.Label(top, text="⏱ 0s",
                                  font=("Segoe UI", 11), bg=tb_bg, fg=fg)
        self.lbl_timer.pack(side='left', padx=12, pady=6)

        self.lbl_status = tk.Label(top, text="",
                                   font=("Segoe UI", 11, "bold"), bg=tb_bg, fg='#50fa7b')
        self.lbl_status.pack(side='left', padx=12, pady=6)

        diff_frame = tk.Frame(top, bg=tb_bg)
        diff_frame.pack(side='right', padx=10)
        tk.Label(diff_frame, text="Niveau :", bg=tb_bg, fg=fg,
                 font=("Segoe UI", 10)).pack(side='left')
        for d in DIFFICULTY:
            tk.Radiobutton(
                diff_frame, text=d, variable=self.difficulty_var, value=d,
                bg=tb_bg, fg=fg, selectcolor=bg, activebackground=tb_bg,
                font=("Segoe UI", 10),
                command=self.start_game,
            ).pack(side='left', padx=4)

        self.grid_frame = tk.Frame(self.win, bg=bg)
        self.grid_frame.pack(fill='both', expand=True, padx=12, pady=8)

        bottom = tk.Frame(self.win, bg=tb_bg)
        bottom.pack(fill='x')

        tk.Button(bottom, text="🔄 Rejouer", font=("Segoe UI", 10),
                  bg=btn_bg, fg=btn_fg, activebackground=bg, relief='flat',
                  padx=10, pady=4, command=self.restart).pack(side='left', padx=10, pady=6)

        tk.Button(bottom, text="❌ Fermer", font=("Segoe UI", 10),
                  bg=btn_bg, fg=btn_fg, activebackground=bg, relief='flat',
                  padx=10, pady=4, command=self._close).pack(side='right', padx=10, pady=6)

    # ── Game logic ────────────────────────────────────────────────────────────

    def start_game(self) -> None:
        self._cancel_timer()
        diff = DIFFICULTY[self.difficulty_var.get()]
        self.grid_size = diff['grid']
        self.total_pairs = diff['pairs']
        self.flip_delay = diff['flip_delay']
        emojis = diff['emojis'][:self.total_pairs]

        symbols = emojis * 2
        random.shuffle(symbols)

        # Clear grid
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        self.cards = []
        self.flipped = []
        self.pairs_found = 0
        self.attempts = 0
        self.elapsed = 0
        self._won = False
        self._locked = False

        self._update_score_label()
        self.lbl_timer.configure(text="⏱ 0s")
        self.lbl_status.configure(text="")

        bg = self.theme.get('bg', '#282a36')
        btn_bg = self.theme.get('btn_bg', '#6272a4')

        for idx, emoji in enumerate(symbols):
            row = idx // self.grid_size
            col = idx % self.grid_size
            card = {
                'emoji': emoji,
                'matched': False,
                'revealed': False,
                'btn': None,
            }
            btn = tk.Button(
                self.grid_frame,
                text="?",
                font=("Arial", 22, "bold"),
                width=3, height=1,
                bg=btn_bg,
                fg=self.theme.get('btn_fg', '#f8f8f2'),
                activebackground=btn_bg,
                relief='raised', bd=3,
                command=lambda i=idx: self._flip(i),
            )
            btn.grid(row=row, column=col, padx=4, pady=4, ipadx=8, ipady=8)
            card['btn'] = btn
            self.cards.append(card)

        for c in range(self.grid_size):
            self.grid_frame.columnconfigure(c, weight=1)

        win_w = self.grid_size * (CARD_W + 12) + 30
        win_h = self.grid_size * (CARD_H + 12) + 120
        self.win.geometry(f"{win_w}x{win_h}")

        self._start_timer()

    def restart(self) -> None:
        self.start_game()

    # ── Card interaction ─────────────────────────────────────────────────────

    def _flip(self, idx: int) -> None:
        if self._locked or self._won:
            return
        card = self.cards[idx]
        if card['matched'] or card['revealed']:
            return
        if len(self.flipped) >= 2:
            return

        card['revealed'] = True
        card['btn'].configure(
            text=card['emoji'],
            font=("Arial", 22),
            bg='#f8f8f2',
            fg='#1a1a2e',
        )
        self.flipped.append(idx)

        if len(self.flipped) == 2:
            self.attempts += 1
            self._check_pair()

    def _check_pair(self) -> None:
        i1, i2 = self.flipped
        c1, c2 = self.cards[i1], self.cards[i2]
        if c1['emoji'] == c2['emoji']:
            # Match!
            c1['matched'] = True
            c2['matched'] = True
            # Flash green
            c1['btn'].configure(bg='#50fa7b')
            c2['btn'].configure(bg='#50fa7b')
            self.flipped = []
            self.pairs_found += 1
            self._update_score_label()
            if self.pairs_found == self.total_pairs:
                self.win.after(400, self._win)
        else:
            # No match — flip back after delay
            self._locked = True
            self.win.after(self.flip_delay, self._hide_pair, i1, i2)

    def _hide_pair(self, i1: int, i2: int) -> None:
        btn_bg = self.theme.get('btn_bg', '#6272a4')
        for idx in (i1, i2):
            c = self.cards[idx]
            c['revealed'] = False
            c['btn'].configure(
                text="?",
                font=("Arial", 22, "bold"),
                bg=btn_bg,
                fg=self.theme.get('btn_fg', '#f8f8f2'),
            )
        self.flipped = []
        self._locked = False
        self._update_score_label()

    # ── Win ───────────────────────────────────────────────────────────────────

    def _win(self) -> None:
        self._won = True
        self._cancel_timer()
        self.lbl_status.configure(
            text=f"🎉 Félicitations ! Toutes les paires trouvées en {self.elapsed}s !"
        )

    # ── Score ─────────────────────────────────────────────────────────────────

    def _update_score_label(self) -> None:
        self.lbl_score.configure(
            text=f"Paires : {self.pairs_found}/{self.total_pairs} | Essais : {self.attempts}"
        )

    # ── Timer ────────────────────────────────────────────────────────────────

    def _start_timer(self) -> None:
        self._tick()

    def _tick(self) -> None:
        if not self._won and self.win.winfo_exists():
            self.lbl_timer.configure(text=f"⏱ {self.elapsed}s")
            self.elapsed += 1
            self._timer_id = self.win.after(1000, self._tick)

    def _cancel_timer(self) -> None:
        if self._timer_id is not None:
            try:
                self.win.after_cancel(self._timer_id)
            except Exception:
                pass
            self._timer_id = None

    def _close(self) -> None:
        self._cancel_timer()
        self.win.destroy()

    def update_score(self, value) -> None:
        pass
