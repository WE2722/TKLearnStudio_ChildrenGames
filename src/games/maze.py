"""Maze Game — navigable labyrinth with recursive-backtracking generation."""
import tkinter as tk
from tkinter import ttk
import random
import time


# ── Difficulty presets ────────────────────────────────────────────────────────
DIFFICULTY = {
    'Facile':  {'cols': 11, 'rows': 11, 'cell': 45},
    'Moyen':   {'cols': 15, 'rows': 15, 'cell': 35},
    'Difficile': {'cols': 21, 'rows': 21, 'cell': 25},
}


def generate_maze(cols: int, rows: int) -> set:
    """Return a set of frozensets representing REMOVED walls (open passages).

    Uses iterative recursive-backtracking (no Python recursion limit risk).
    A passage between cell A=(c,r) and cell B=(c',r') is represented as
    frozenset({A, B}).  Cells not connected by a passage are separated by a wall.
    """
    visited = [[False] * rows for _ in range(cols)]
    passages: set = set()

    start = (0, 0)
    visited[0][0] = True
    stack = [start]

    while stack:
        c, r = stack[-1]
        # Gather unvisited neighbours (cardinal directions only)
        neighbours = []
        for dc, dr in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nc, nr = c + dc, r + dr
            if 0 <= nc < cols and 0 <= nr < rows and not visited[nc][nr]:
                neighbours.append((nc, nr))

        if neighbours:
            nc, nr = random.choice(neighbours)
            passages.add(frozenset({(c, r), (nc, nr)}))
            visited[nc][nr] = True
            stack.append((nc, nr))
        else:
            stack.pop()

    return passages


class MazeGame:
    """Navigable maze game in a Toplevel window."""

    def __init__(self, parent, theme: dict):
        self.parent = parent
        self.theme = theme

        self.win = tk.Toplevel(parent)
        self.win.title("🌀 Labyrinthe")
        self.win.resizable(True, True)
        self.win.configure(bg=theme.get('bg', '#282a36'))

        # State
        self.difficulty_var = tk.StringVar(value='Moyen')
        self.passages: set = set()
        self.player: tuple = (0, 0)
        self.move_count: int = 0
        self.elapsed: int = 0
        self._timer_id = None
        self._won: bool = False
        self.cols = 15
        self.rows = 15
        self.cell = 35

        self._build_ui()
        self.start_game()

        self.win.focus_set()
        self.win.bind('<Left>',  lambda e: self._move(-1, 0))
        self.win.bind('<Right>', lambda e: self._move(1, 0))
        self.win.bind('<Up>',    lambda e: self._move(0, -1))
        self.win.bind('<Down>',  lambda e: self._move(0, 1))

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        bg = self.theme.get('bg', '#282a36')
        fg = self.theme.get('fg', '#f8f8f2')
        btn_bg = self.theme.get('btn_bg', '#6272a4')
        btn_fg = self.theme.get('btn_fg', '#f8f8f2')
        tb_bg = self.theme.get('toolbar_bg', '#44475a')

        # ── Top bar ───────────────────────────────────
        top = tk.Frame(self.win, bg=tb_bg)
        top.pack(fill='x', padx=0, pady=0)

        self.lbl_moves = tk.Label(
            top, text="Déplacements : 0",
            font=("Segoe UI", 11), bg=tb_bg, fg=fg,
        )
        self.lbl_moves.pack(side='left', padx=12, pady=6)

        self.lbl_timer = tk.Label(
            top, text="⏱ 0s",
            font=("Segoe UI", 11), bg=tb_bg, fg=fg,
        )
        self.lbl_timer.pack(side='left', padx=12, pady=6)

        self.lbl_status = tk.Label(
            top, text="",
            font=("Segoe UI", 11, "bold"), bg=tb_bg, fg='#50fa7b',
        )
        self.lbl_status.pack(side='left', padx=12, pady=6)

        # Difficulty selector
        diff_frame = tk.Frame(top, bg=tb_bg)
        diff_frame.pack(side='right', padx=10)
        tk.Label(diff_frame, text="Difficulté :", bg=tb_bg, fg=fg,
                 font=("Segoe UI", 10)).pack(side='left')
        for diff in DIFFICULTY:
            tk.Radiobutton(
                diff_frame, text=diff, variable=self.difficulty_var, value=diff,
                bg=tb_bg, fg=fg, selectcolor=bg, activebackground=tb_bg,
                font=("Segoe UI", 10),
                command=self.start_game,
            ).pack(side='left', padx=4)

        # ── Canvas ────────────────────────────────────
        self.canvas_frame = tk.Frame(self.win, bg=bg)
        self.canvas_frame.pack(fill='both', expand=True, padx=10, pady=8)

        self.canvas = tk.Canvas(
            self.canvas_frame, bg='white',
            highlightthickness=2, highlightbackground=btn_bg,
        )
        self.canvas.pack(expand=True)

        # ── Bottom bar ────────────────────────────────
        bottom = tk.Frame(self.win, bg=tb_bg)
        bottom.pack(fill='x', padx=0, pady=0)

        tk.Button(
            bottom, text="🔄 Rejouer",
            font=("Segoe UI", 10), bg=btn_bg, fg=btn_fg,
            activebackground=bg, relief='flat', padx=10, pady=4,
            command=self.restart,
        ).pack(side='left', padx=10, pady=6)

        tk.Label(
            bottom,
            text="Utilisez les flèches ← ↑ → ↓ pour vous déplacer",
            font=("Segoe UI", 9), bg=tb_bg, fg=fg,
        ).pack(side='left', padx=8)

        tk.Button(
            bottom, text="❌ Fermer",
            font=("Segoe UI", 10), bg=btn_bg, fg=btn_fg,
            activebackground=bg, relief='flat', padx=10, pady=4,
            command=self._close,
        ).pack(side='right', padx=10, pady=6)

    # ── Game logic ────────────────────────────────────────────────────────────

    def start_game(self) -> None:
        """Generate a new maze and reset all state."""
        self._cancel_timer()
        diff = DIFFICULTY[self.difficulty_var.get()]
        self.cols = diff['cols']
        self.rows = diff['rows']
        self.cell = diff['cell']

        canvas_w = self.cols * self.cell
        canvas_h = self.rows * self.cell
        self.canvas.configure(width=canvas_w, height=canvas_h)

        win_w = canvas_w + 40
        win_h = canvas_h + 120
        self.win.geometry(f"{win_w}x{win_h}")

        self.passages = generate_maze(self.cols, self.rows)
        self.player = (0, 0)
        self.move_count = 0
        self.elapsed = 0
        self._won = False

        self.lbl_moves.configure(text="Déplacements : 0")
        self.lbl_timer.configure(text="⏱ 0s")
        self.lbl_status.configure(text="")

        self._draw_maze()
        self._start_timer()
        self.win.focus_set()

    def restart(self) -> None:
        self.start_game()

    # ── Maze drawing ─────────────────────────────────────────────────────────

    def _draw_maze(self) -> None:
        self.canvas.delete('all')
        c = self.cell
        cols, rows = self.cols, self.rows

        # Background
        self.canvas.configure(bg='white')

        # Draw exit cell (green)
        ex, ey = (cols - 1) * c, (rows - 1) * c
        self.canvas.create_rectangle(
            ex + 2, ey + 2, ex + c - 2, ey + c - 2,
            fill='#50fa7b', outline='', tags='exit',
        )
        self.canvas.create_text(
            ex + c // 2, ey + c // 2,
            text='🏁', font=('Arial', max(8, c // 3)), tags='exit',
        )

        # Draw walls
        for col in range(cols):
            for row in range(rows):
                x, y = col * c, row * c
                # Right wall
                if col + 1 < cols and frozenset({(col, row), (col + 1, row)}) not in self.passages:
                    self.canvas.create_line(x + c, y, x + c, y + c, fill='black', width=2)
                # Bottom wall
                if row + 1 < rows and frozenset({(col, row), (col, row + 1)}) not in self.passages:
                    self.canvas.create_line(x, y + c, x + c, y + c, fill='black', width=2)

        # Border walls
        self.canvas.create_rectangle(0, 0, cols * c, rows * c, outline='black', width=3)

        # Draw player
        self._draw_player()

    def _draw_player(self) -> None:
        self.canvas.delete('player')
        c = self.cell
        px, py = self.player[0] * c, self.player[1] * c
        pad = max(4, c // 5)
        self.canvas.create_oval(
            px + pad, py + pad, px + c - pad, py + c - pad,
            fill='#3498db', outline='#1a6fa8', width=2, tags='player',
        )

    # ── Movement ─────────────────────────────────────────────────────────────

    def _move(self, dc: int, dr: int) -> None:
        if self._won:
            return
        pc, pr = self.player
        nc, nr = pc + dc, pr + dr
        if not (0 <= nc < self.cols and 0 <= nr < self.rows):
            return
        if frozenset({(pc, pr), (nc, nr)}) not in self.passages:
            return   # wall blocks

        self.player = (nc, nr)
        self.move_count += 1
        self.lbl_moves.configure(text=f"Déplacements : {self.move_count}")
        self._draw_player()

        # Win check
        if (nc, nr) == (self.cols - 1, self.rows - 1):
            self._win()

    # ── Win ───────────────────────────────────────────────────────────────────

    def _win(self) -> None:
        self._won = True
        self._cancel_timer()
        self.lbl_status.configure(text="✅ Sortie trouvée !")
        c = self.cell
        cx = (self.cols * c) // 2
        cy = (self.rows * c) // 2
        self.canvas.create_rectangle(
            cx - 160, cy - 45, cx + 160, cy + 45,
            fill='#50fa7b', outline='#27ae60', width=3,
        )
        self.canvas.create_text(
            cx, cy,
            text=f"🎉 Bravo ! {self.move_count} déplacements en {self.elapsed}s !",
            font=('Arial', max(10, c // 3), 'bold'),
            fill='#1e3a2f',
        )

    # ── Timer ─────────────────────────────────────────────────────────────────

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
