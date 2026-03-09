"""Snake — classic snake game with increasing speed."""
import tkinter as tk
import random

CELL = 30
COLS = 20
ROWS = 20
CANVAS_W = CELL * COLS   # 600
CANVAS_H = CELL * ROWS   # 600

DIFFICULTY = {
    'Facile':    {'speed': 200, 'label': 'Facile'},
    'Moyen':     {'speed': 130, 'label': 'Moyen'},
    'Difficile': {'speed': 80,  'label': 'Difficile'},
}

DIRS = {
    'Up':    (0, -1),
    'Down':  (0,  1),
    'Left':  (-1, 0),
    'Right': (1,  0),
}
OPPOSITE = {'Up': 'Down', 'Down': 'Up', 'Left': 'Right', 'Right': 'Left'}


class SnakeGame:
    """Snake game in a Toplevel window."""

    def __init__(self, parent, theme: dict):
        self.parent = parent
        self.theme = theme

        self.win = tk.Toplevel(parent)
        self.win.title("🐍 Serpent")
        self.win.resizable(False, False)
        self.win.configure(bg=theme.get('bg', '#282a36'))
        self.win.protocol('WM_DELETE_WINDOW', self._on_close)
        self.win.bind('<KeyPress>', self._on_key)
        self.win.focus_set()

        # Session state
        self.high_score = 0

        # Runtime state (set in start_game)
        self.snake: list[tuple[int, int]] = []
        self.direction = 'Right'
        self._next_dir = 'Right'
        self.food: tuple[int, int] = (0, 0)
        self.score = 0
        self._running = False
        self._paused = False
        self._after_id: str | None = None
        self._base_speed = DIFFICULTY['Moyen']['speed']
        self._foods_eaten = 0

        self.difficulty_var = tk.StringVar(value='Moyen')

        self._build_ui()
        self.start_game()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        bg  = self.theme.get('bg', '#282a36')
        fg  = self.theme.get('fg', '#f8f8f2')
        btn_bg = self.theme.get('btn_bg', '#6272a4')
        btn_fg = self.theme.get('btn_fg', '#f8f8f2')
        tb_bg  = self.theme.get('toolbar_bg', '#44475a')

        # ── Toolbar ──────────────────────────────────────────────────────────
        top = tk.Frame(self.win, bg=tb_bg)
        top.pack(fill='x')

        self.lbl_score = tk.Label(top, text="Score : 0   Meilleur : 0",
                                  font=("Segoe UI", 11), bg=tb_bg, fg=fg)
        self.lbl_score.pack(side='left', padx=12, pady=6)

        diff_frame = tk.Frame(top, bg=tb_bg)
        diff_frame.pack(side='right', padx=10)
        tk.Label(diff_frame, text="Vitesse :", bg=tb_bg, fg=fg,
                 font=("Segoe UI", 10)).pack(side='left')
        for d in ('Facile', 'Moyen', 'Difficile'):
            tk.Radiobutton(
                diff_frame, text=d, variable=self.difficulty_var, value=d,
                bg=tb_bg, fg=fg, selectcolor=bg, activebackground=tb_bg,
                font=("Segoe UI", 10),
                command=self._on_difficulty_change,
            ).pack(side='left', padx=4)

        # ── Canvas ───────────────────────────────────────────────────────────
        canvas_bg = self.theme.get('editor_bg', '#1e1f29')
        self.canvas = tk.Canvas(self.win, width=CANVAS_W, height=CANVAS_H,
                                bg=canvas_bg, highlightthickness=2,
                                highlightbackground=btn_bg)
        self.canvas.pack(padx=6, pady=4)

        # ── Status + hint ────────────────────────────────────────────────────
        mid = tk.Frame(self.win, bg=bg)
        mid.pack(fill='x')
        self.lbl_status = tk.Label(mid, text="",
                                   font=("Segoe UI", 11, "bold"), bg=bg, fg=fg)
        self.lbl_status.pack(side='left', padx=12)
        tk.Label(mid, text="P = pause  |  Flèches = direction",
                 font=("Segoe UI", 9), bg=bg, fg=tb_bg).pack(side='right', padx=10)

        # ── Bottom bar ───────────────────────────────────────────────────────
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

    # ── Game core ─────────────────────────────────────────────────────────────

    def start_game(self) -> None:
        self._cancel_loop()
        cx, cy = COLS // 2, ROWS // 2
        self.snake = [(cx - 2, cy), (cx - 1, cy), (cx, cy)]
        self.direction = 'Right'
        self._next_dir = 'Right'
        self.score = 0
        self._foods_eaten = 0
        self._running = True
        self._paused = False
        self._base_speed = DIFFICULTY[self.difficulty_var.get()]['speed']
        self._place_food()
        self._update_labels()
        self.lbl_status.configure(text="", fg=self.theme.get('fg', '#f8f8f2'))
        self._draw()
        self._after_id = self.win.after(self._current_speed(), self._loop)

    def restart(self) -> None:
        self.start_game()

    def _on_difficulty_change(self) -> None:
        self._base_speed = DIFFICULTY[self.difficulty_var.get()]['speed']

    def _place_food(self) -> None:
        occupied = set(self.snake)
        free = [(c, r) for c in range(COLS) for r in range(ROWS)
                if (c, r) not in occupied]
        if free:
            self.food = random.choice(free)

    def _current_speed(self) -> int:
        """Decrease interval by 5ms every 5 foods, minimum 40ms."""
        reduction = (self._foods_eaten // 5) * 5
        return max(40, self._base_speed - reduction)

    # ── Loop ──────────────────────────────────────────────────────────────────

    def _loop(self) -> None:
        if not self._running or self._paused:
            return
        self._step()
        if self._running and not self._paused:
            self._after_id = self.win.after(self._current_speed(), self._loop)

    def _step(self) -> None:
        self.direction = self._next_dir
        hx, hy = self.snake[-1]
        dx, dy = DIRS[self.direction]
        nx, ny = hx + dx, hy + dy

        # Wall collision
        if not (0 <= nx < COLS and 0 <= ny < ROWS):
            self._game_over()
            return

        # Self collision (exclude tail since it will move)
        if (nx, ny) in self.snake[:-1]:
            self._game_over()
            return

        self.snake.append((nx, ny))

        if (nx, ny) == self.food:
            self.score += 10
            self._foods_eaten += 1
            if self.score > self.high_score:
                self.high_score = self.score
            self._place_food()
        else:
            self.snake.pop(0)

        self._update_labels()
        self._draw()

    def _game_over(self) -> None:
        self._running = False
        self._cancel_loop()
        self._draw()
        msg = f"Game Over ! Score : {self.score}"
        if self.score == self.high_score and self.score > 0:
            msg += "  🏆 Nouveau record !"
        self.lbl_status.configure(text=msg, fg='#ff5555')

    def _cancel_loop(self) -> None:
        if self._after_id:
            try:
                self.win.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    # ── Input ─────────────────────────────────────────────────────────────────

    def _on_key(self, event: tk.Event) -> None:
        key = event.keysym
        if key == 'p' or key == 'P':
            self._toggle_pause()
            return
        if key in DIRS and self._running and not self._paused:
            if key != OPPOSITE.get(self.direction):
                self._next_dir = key

    def _toggle_pause(self) -> None:
        if not self._running:
            return
        self._paused = not self._paused
        if self._paused:
            self.lbl_status.configure(text="⏸ Pause — appuie sur P pour reprendre",
                                       fg='#ffb86c')
        else:
            self.lbl_status.configure(text="", fg=self.theme.get('fg', '#f8f8f2'))
            self._after_id = self.win.after(self._current_speed(), self._loop)

    # ── Drawing ───────────────────────────────────────────────────────────────

    def _draw(self) -> None:
        self.canvas.delete('all')
        # Grid (subtle)
        grid_color = self.theme.get('editor_bg', '#22233a')
        for c in range(COLS + 1):
            self.canvas.create_line(c * CELL, 0, c * CELL, CANVAS_H,
                                    fill=grid_color, width=1)
        for r in range(ROWS + 1):
            self.canvas.create_line(0, r * CELL, CANVAS_W, r * CELL,
                                    fill=grid_color, width=1)

        # Food
        fx, fy = self.food
        self.canvas.create_oval(
            fx * CELL + 4, fy * CELL + 4,
            fx * CELL + CELL - 4, fy * CELL + CELL - 4,
            fill='#ff5555', outline='', tags='food'
        )

        # Snake body
        for i, (cx, cy) in enumerate(self.snake):
            color = '#27ae60' if i == len(self.snake) - 1 else '#2ecc71'
            self.canvas.create_rectangle(
                cx * CELL + 1, cy * CELL + 1,
                cx * CELL + CELL - 1, cy * CELL + CELL - 1,
                fill=color, outline='', tags='snake'
            )

        # Eyes on head
        hx, hy = self.snake[-1]
        dx, dy = DIRS[self.direction]
        ex1 = hx * CELL + CELL // 2 - dy * 6 - 4
        ey1 = hy * CELL + CELL // 2 + dx * 6 - 4
        ex2 = hx * CELL + CELL // 2 - dy * 6 + 4
        ey2 = hy * CELL + CELL // 2 + dx * 6 + 4
        for ex, ey in ((ex1, ey1), (ex2, ey2)):
            self.canvas.create_oval(ex - 3, ey - 3, ex + 3, ey + 3,
                                    fill='white', outline='')

    def _update_labels(self) -> None:
        self.lbl_score.configure(
            text=f"Score : {self.score}   Meilleur : {self.high_score}"
        )

    def update_score(self, value: int) -> None:
        self.score = value
        self._update_labels()

    def _on_close(self) -> None:
        self._cancel_loop()
        self.win.destroy()
