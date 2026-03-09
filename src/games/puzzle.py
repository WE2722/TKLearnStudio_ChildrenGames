"""Sliding Puzzle (15-puzzle, 8-puzzle, 24-puzzle) game."""
import tkinter as tk
from tkinter import ttk
import random
import time


DIFFICULTY = {
    'Facile':    {'size': 3},
    'Moyen':     {'size': 4},
    'Difficile': {'size': 5},
}

TILE_PALETTE = [
    '#ff79c6', '#8be9fd', '#50fa7b', '#ffb86c', '#bd93f9',
    '#ff5555', '#f1fa8c', '#6272a4', '#ff92df', '#80ffea',
    '#a4ffff', '#ffffa5', '#ffd6ff', '#d6ffff', '#ffeed6',
    '#d6ffd6', '#ffd6d6', '#d6d6ff', '#ffe4b5', '#b5e4ff',
    '#e4ffb5', '#ffb5e4', '#b5ffe4', '#e4b5ff', '#ffd6b5',
]


def _is_solvable(tiles: list[int], size: int) -> bool:
    """Return True if the flat tile list (0 = blank) is solvable."""
    inversions = 0
    flat = [t for t in tiles if t != 0]
    for i in range(len(flat)):
        for j in range(i + 1, len(flat)):
            if flat[i] > flat[j]:
                inversions += 1

    if size % 2 == 1:
        return inversions % 2 == 0
    else:
        blank_row = tiles.index(0) // size
        row_from_bottom = size - blank_row
        if row_from_bottom % 2 == 1:
            return inversions % 2 == 0
        else:
            return inversions % 2 == 1


def shuffle_solvable(size: int) -> list[int]:
    """Generate a solvable puzzle by making 300 random valid moves from goal state."""
    n = size * size
    tiles = list(range(1, n)) + [0]  # goal state: 1,2,...,n-1,0
    blank = n - 1
    for _ in range(300):
        r, c = blank // size, blank % size
        moves = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < size and 0 <= nc < size:
                moves.append(nr * size + nc)
        swap = random.choice(moves)
        tiles[blank], tiles[swap] = tiles[swap], tiles[blank]
        blank = swap
    return tiles


def is_solved(tiles: list[int]) -> bool:
    """Return True when tiles are in goal state (1..n-1, 0 at end)."""
    n = len(tiles)
    if tiles[-1] != 0:
        return False
    return all(tiles[i] == i + 1 for i in range(n - 1))


class PuzzleGame:
    """Sliding tile puzzle in a Toplevel window."""

    TILE_SIZE = 100

    def __init__(self, parent, theme: dict):
        self.parent = parent
        self.theme = theme

        self.win = tk.Toplevel(parent)
        self.win.title("🧩 Puzzle Glissant")
        self.win.resizable(True, True)
        self.win.configure(bg=theme.get('bg', '#282a36'))

        self.difficulty_var = tk.StringVar(value='Moyen')
        self.size = 4
        self.tiles: list[int] = []
        self.move_count = 0
        self.elapsed = 0
        self._timer_id = None
        self._won = False

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

        self.lbl_moves = tk.Label(top, text="Mouvements : 0",
                                  font=("Segoe UI", 11), bg=tb_bg, fg=fg)
        self.lbl_moves.pack(side='left', padx=12, pady=6)

        self.lbl_timer = tk.Label(top, text="⏱ 0s",
                                  font=("Segoe UI", 11), bg=tb_bg, fg=fg)
        self.lbl_timer.pack(side='left', padx=12, pady=6)

        self.lbl_status = tk.Label(top, text="",
                                   font=("Segoe UI", 11, "bold"), bg=tb_bg, fg='#50fa7b')
        self.lbl_status.pack(side='left', padx=12, pady=6)

        diff_frame = tk.Frame(top, bg=tb_bg)
        diff_frame.pack(side='right', padx=10)
        tk.Label(diff_frame, text="Taille :", bg=tb_bg, fg=fg,
                 font=("Segoe UI", 10)).pack(side='left')
        for d in DIFFICULTY:
            tk.Radiobutton(
                diff_frame, text=d, variable=self.difficulty_var, value=d,
                bg=tb_bg, fg=fg, selectcolor=bg, activebackground=tb_bg,
                font=("Segoe UI", 10),
                command=self.start_game,
            ).pack(side='left', padx=4)

        canvas_container = tk.Frame(self.win, bg=bg)
        canvas_container.pack(fill='both', expand=True, padx=12, pady=8)

        self.canvas = tk.Canvas(canvas_container, bg=bg,
                                highlightthickness=0)
        self.canvas.pack(expand=True)
        self.canvas.bind('<Button-1>', self._on_click)

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
        self.size = DIFFICULTY[self.difficulty_var.get()]['size']
        ts = self.TILE_SIZE
        canvas_size = self.size * ts
        self.canvas.configure(width=canvas_size, height=canvas_size)
        win_w = canvas_size + 40
        win_h = canvas_size + 120
        self.win.geometry(f"{win_w}x{win_h}")

        self.tiles = shuffle_solvable(self.size)
        self.move_count = 0
        self.elapsed = 0
        self._won = False
        self.lbl_moves.configure(text="Mouvements : 0")
        self.lbl_timer.configure(text="⏱ 0s")
        self.lbl_status.configure(text="")

        self._draw_board()
        self._start_timer()

    def restart(self) -> None:
        self.start_game()

    # ── Drawing ───────────────────────────────────────────────────────────────

    def _draw_board(self) -> None:
        self.canvas.delete('all')
        ts = self.TILE_SIZE
        n = self.size * self.size
        for idx, val in enumerate(self.tiles):
            row = idx // self.size
            col = idx % self.size
            x0, y0 = col * ts, row * ts
            x1, y1 = x0 + ts, y0 + ts
            if val == 0:
                # Empty cell
                self.canvas.create_rectangle(x0 + 2, y0 + 2, x1 - 2, y1 - 2,
                                              fill=self.theme.get('bg', '#21222c'),
                                              outline='', tags=f'tile_{idx}')
            else:
                color = TILE_PALETTE[(val - 1) % len(TILE_PALETTE)]
                self.canvas.create_rectangle(x0 + 4, y0 + 4, x1 - 4, y1 - 4,
                                              fill=color, outline='white', width=2,
                                              tags=f'tile_{idx}')
                self.canvas.create_text(
                    x0 + ts // 2, y0 + ts // 2,
                    text=str(val),
                    font=('Arial', max(16, ts // 3), 'bold'),
                    fill='#1a1a2e',
                    tags=f'tile_{idx}',
                )

    # ── Interaction ───────────────────────────────────────────────────────────

    def _on_click(self, event: tk.Event) -> None:
        if self._won:
            return
        ts = self.TILE_SIZE
        col = event.x // ts
        row = event.y // ts
        if not (0 <= col < self.size and 0 <= row < self.size):
            return
        clicked_idx = row * self.size + col
        blank_idx = self.tiles.index(0)

        br, bc = blank_idx // self.size, blank_idx % self.size
        cr, cc = row, col
        if abs(br - cr) + abs(bc - cc) != 1:
            return  # not adjacent

        # Slide
        self.tiles[blank_idx], self.tiles[clicked_idx] = (
            self.tiles[clicked_idx], self.tiles[blank_idx])
        self.move_count += 1
        self.lbl_moves.configure(text=f"Mouvements : {self.move_count}")
        self._draw_board()

        if is_solved(self.tiles):
            self._win()

    # ── Win ───────────────────────────────────────────────────────────────────

    def _win(self) -> None:
        self._won = True
        self._cancel_timer()
        self.lbl_status.configure(text="🎉 Bravo !")
        ts = self.TILE_SIZE
        cx = (self.size * ts) // 2
        cy = (self.size * ts) // 2
        self.canvas.create_rectangle(cx - 180, cy - 50, cx + 180, cy + 50,
                                      fill='#50fa7b', outline='#27ae60', width=3)
        self.canvas.create_text(
            cx, cy,
            text=f"🎉 Bravo ! {self.move_count} mouvements en {self.elapsed}s !",
            font=('Arial', 14, 'bold'), fill='#1e3a2f',
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
