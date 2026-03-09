"""Tic Tac Toe — Human vs AI with minimax (Hard), block (Medium), random (Easy)."""
import tkinter as tk
from tkinter import ttk
import random
import math


CELL = 150
CANVAS_SIZE = CELL * 3   # 450
WIN_COMBOS = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),   # cols
    (0, 4, 8), (2, 4, 6),               # diags
]


def check_winner(board: list) -> str | None:
    """Return 'X', 'O', 'draw', or None."""
    for a, b, c in WIN_COMBOS:
        if board[a] == board[b] == board[c] and board[a] != '':
            return board[a]
    if all(cell != '' for cell in board):
        return 'draw'
    return None


def get_empty(board: list) -> list[int]:
    return [i for i, c in enumerate(board) if c == '']


def minimax(board: list, is_maximizing: bool, alpha: float, beta: float) -> int:
    """Minimax with alpha-beta pruning. AI = 'O' (maximizing)."""
    winner = check_winner(board)
    if winner == 'O':
        return 1
    if winner == 'X':
        return -1
    if winner == 'draw':
        return 0

    if is_maximizing:
        best = -math.inf
        for i in get_empty(board):
            board[i] = 'O'
            best = max(best, minimax(board, False, alpha, beta))
            board[i] = ''
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best
    else:
        best = math.inf
        for i in get_empty(board):
            board[i] = 'X'
            best = min(best, minimax(board, True, alpha, beta))
            board[i] = ''
            beta = min(beta, best)
            if beta <= alpha:
                break
        return best


def ai_move_hard(board: list) -> int:
    best_score = -math.inf
    best_move = -1
    for i in get_empty(board):
        board[i] = 'O'
        score = minimax(board, False, -math.inf, math.inf)
        board[i] = ''
        if score > best_score:
            best_score = score
            best_move = i
    return best_move


def ai_move_medium(board: list) -> int:
    """Block human win if possible, else random."""
    # First check if AI can win
    for i in get_empty(board):
        board[i] = 'O'
        if check_winner(board) == 'O':
            board[i] = ''
            return i
        board[i] = ''
    # Block human win
    for i in get_empty(board):
        board[i] = 'X'
        if check_winner(board) == 'X':
            board[i] = ''
            return i
        board[i] = ''
    return random.choice(get_empty(board))


def ai_move_easy(board: list) -> int:
    return random.choice(get_empty(board))


class TicTacToeGame:
    """Tic Tac Toe with AI opponent in a Toplevel window."""

    def __init__(self, parent, theme: dict):
        self.parent = parent
        self.theme = theme

        self.win = tk.Toplevel(parent)
        self.win.title("⭕ Morpion")
        self.win.geometry("500x580")
        self.win.resizable(True, True)
        self.win.configure(bg=theme.get('bg', '#282a36'))

        # Session score
        self.score_human = 0
        self.score_ai = 0
        self.score_draw = 0

        self.difficulty_var = tk.StringVar(value='Moyen')
        self.board: list[str] = [''] * 9
        self._game_over = False
        self._human_turn = True

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

        self.lbl_score = tk.Label(top,
                                  text="Vous : 0 | IA : 0 | Nuls : 0",
                                  font=("Segoe UI", 11), bg=tb_bg, fg=fg)
        self.lbl_score.pack(side='left', padx=12, pady=6)

        diff_frame = tk.Frame(top, bg=tb_bg)
        diff_frame.pack(side='right', padx=10)
        tk.Label(diff_frame, text="Niveau :", bg=tb_bg, fg=fg,
                 font=("Segoe UI", 10)).pack(side='left')
        for d in ('Facile', 'Moyen', 'Difficile'):
            tk.Radiobutton(
                diff_frame, text=d, variable=self.difficulty_var, value=d,
                bg=tb_bg, fg=fg, selectcolor=bg, activebackground=tb_bg,
                font=("Segoe UI", 10),
            ).pack(side='left', padx=4)

        self.lbl_status = tk.Label(self.win, text="À vous de jouer !",
                                   font=("Segoe UI", 13, "bold"), bg=bg, fg=fg)
        self.lbl_status.pack(pady=6)

        canvas_frame = tk.Frame(self.win, bg=bg)
        canvas_frame.pack(expand=True)

        self.canvas = tk.Canvas(canvas_frame, width=CANVAS_SIZE, height=CANVAS_SIZE,
                                bg=self.theme.get('preview_bg', '#ffffff'),
                                highlightthickness=2, highlightbackground=btn_bg)
        self.canvas.pack()
        self.canvas.bind('<Button-1>', self._on_click)

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
        self.board = [''] * 9
        self._game_over = False
        self._human_turn = True
        self.lbl_status.configure(text="À vous de jouer !", fg=self.theme.get('fg', '#f8f8f2'))
        self._draw_board()

    def restart(self) -> None:
        self.start_game()

    # ── Drawing ───────────────────────────────────────────────────────────────

    def _draw_board(self) -> None:
        self.canvas.delete('all')
        preview_bg = self.theme.get('preview_bg', '#ffffff')
        self.canvas.configure(bg=preview_bg)
        # Grid lines
        for i in (1, 2):
            self.canvas.create_line(i * CELL, 0, i * CELL, CANVAS_SIZE,
                                    fill='#555', width=4)
            self.canvas.create_line(0, i * CELL, CANVAS_SIZE, i * CELL,
                                    fill='#555', width=4)
        # Marks
        for idx, mark in enumerate(self.board):
            if mark:
                self._draw_mark(idx, mark)

    def _draw_mark(self, idx: int, mark: str) -> None:
        row, col = idx // 3, idx % 3
        x0, y0 = col * CELL, row * CELL
        cx, cy = x0 + CELL // 2, y0 + CELL // 2
        pad = 28
        if mark == 'X':
            self.canvas.create_line(x0 + pad, y0 + pad,
                                    x0 + CELL - pad, y0 + CELL - pad,
                                    fill='#e74c3c', width=8, tags='mark')
            self.canvas.create_line(x0 + CELL - pad, y0 + pad,
                                    x0 + pad, y0 + CELL - pad,
                                    fill='#e74c3c', width=8, tags='mark')
        else:
            r = CELL // 2 - pad
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                    outline='#3498db', width=8, tags='mark')

    def _highlight_win(self, combo: tuple) -> None:
        for idx in combo:
            row, col = idx // 3, idx % 3
            x0, y0 = col * CELL, row * CELL
            self.canvas.create_rectangle(x0 + 4, y0 + 4,
                                         x0 + CELL - 4, y0 + CELL - 4,
                                         fill='#f1fa8c', outline='', tags='highlight')
        if self.canvas.find_withtag('mark'):
            self.canvas.tag_lower('highlight', 'mark')

    # ── Player interaction ────────────────────────────────────────────────────

    def _on_click(self, event: tk.Event) -> None:
        if self._game_over or not self._human_turn:
            return
        col = event.x // CELL
        row = event.y // CELL
        if not (0 <= col < 3 and 0 <= row < 3):
            return
        idx = row * 3 + col
        if self.board[idx] != '':
            return

        self.board[idx] = 'X'
        self._draw_mark(idx, 'X')
        self._human_turn = False

        result = check_winner(self.board)
        if result:
            self._end_game(result)
        else:
            self.lbl_status.configure(text="L'IA réfléchit...")
            self.win.after(300, self._ai_move)

    def _ai_move(self) -> None:
        if self._game_over:
            return
        empty = get_empty(self.board)
        if not empty:
            return

        diff = self.difficulty_var.get()
        if diff == 'Difficile':
            move = ai_move_hard(self.board)
        elif diff == 'Moyen':
            move = ai_move_medium(self.board)
        else:
            move = ai_move_easy(self.board)

        self.board[move] = 'O'
        self._draw_mark(move, 'O')
        self._human_turn = True

        result = check_winner(self.board)
        if result:
            self._end_game(result)
        else:
            self.lbl_status.configure(text="À vous de jouer !")

    # ── End ───────────────────────────────────────────────────────────────────

    def _end_game(self, result: str) -> None:
        self._game_over = True
        if result == 'X':
            self.score_human += 1
            self.lbl_status.configure(text="🎉 Vous avez gagné !", fg='#50fa7b')
        elif result == 'O':
            self.score_ai += 1
            self.lbl_status.configure(text="🤖 L'IA a gagné !", fg='#ff5555')
        else:
            self.score_draw += 1
            self.lbl_status.configure(text="🤝 Égalité !", fg='#ffb86c')

        # Highlight winning combo
        for combo in WIN_COMBOS:
            a, b, c = combo
            if self.board[a] == self.board[b] == self.board[c] != '':
                self._highlight_win(combo)
                break

        self._update_score()

    def _update_score(self) -> None:
        self.lbl_score.configure(
            text=f"Vous : {self.score_human} | IA : {self.score_ai} | Nuls : {self.score_draw}"
        )

    def update_score(self, value) -> None:
        pass
