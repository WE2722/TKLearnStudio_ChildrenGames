"""Game Manager — registry and launcher for TkLearn Studio games."""
import importlib
import traceback
import tkinter as tk
from tkinter import messagebox, ttk

GAME_REGISTRY = [
    {'id': 'maze',         'name': '🌀 Labyrinthe',         'age': '6+',  'module': 'maze',         'class': 'MazeGame'},
    {'id': 'puzzle',       'name': '🧩 Puzzle Glissant',    'age': '7+',  'module': 'puzzle',       'class': 'PuzzleGame'},
    {'id': 'memory',       'name': '🃏 Jeu de Mémoire',     'age': '5+',  'module': 'memory',       'class': 'MemoryGame'},
    {'id': 'enigmes',      'name': '🔍 Énigmes',            'age': '8+',  'module': 'enigmes',      'class': 'EnigmesGame'},
    {'id': 'hangman',      'name': '🪢 Pendu',              'age': '8+',  'module': 'hangman',      'class': 'HangmanGame'},
    {'id': 'tictactoe',    'name': '⭕ Morpion',            'age': '6+',  'module': 'tictactoe',    'class': 'TicTacToeGame'},
    {'id': 'snake',        'name': '🐍 Snake',              'age': '7+',  'module': 'snake',        'class': 'SnakeGame'},
    {'id': 'colorquiz',    'name': '🎨 Quiz Couleurs',      'age': '5+',  'module': 'colorquiz',    'class': 'ColorQuizGame'},
    {'id': 'mathquiz',     'name': '🔢 Quiz Maths',         'age': '7+',  'module': 'mathquiz',     'class': 'MathQuizGame'},
    {'id': 'wordscramble', 'name': '🔤 Mots Mélangés',      'age': '9+',  'module': 'wordscramble', 'class': 'WordScrambleGame'},
]


class GameManager:
    """Registry and launcher for the TkLearn Studio games module."""

    def __init__(self):
        self.current_theme: dict = {}

    # ── Public API ────────────────────────────────────

    def get_all_games(self) -> list[dict]:
        """Return the full GAME_REGISTRY list."""
        return GAME_REGISTRY

    def launch_game(self, game_id: str, parent_window, theme: dict) -> bool:
        """Dynamically import and instantiate a game by id.

        Returns True on success, False if the import or instantiation fails.
        """
        entry = next((g for g in GAME_REGISTRY if g['id'] == game_id), None)
        if entry is None:
            messagebox.showerror(
                "Jeu introuvable",
                f"Aucun jeu avec l'identifiant '{game_id}' n'a été trouvé.",
            )
            return False

        module_name = entry['module']
        class_name = entry['class']

        try:
            mod = importlib.import_module(f"src.games.{module_name}")
            cls = getattr(mod, class_name)
            cls(parent_window, theme)
            return True
        except Exception:
            err = traceback.format_exc()
            messagebox.showerror(
                "Erreur de chargement",
                f"Impossible de lancer «{entry['name']}» :\n\n{err}",
            )
            return False

    def open_games_lobby(self, parent_window, theme: dict) -> None:
        """Open the games lobby Toplevel window."""
        lobby = tk.Toplevel(parent_window)
        lobby.title("🎮 Jeux pour Enfants")
        lobby.geometry("700x520")
        lobby.resizable(True, True)
        lobby.configure(bg=theme.get('bg', '#282a36'))

        # ── Header ────────────────────────────────────
        header_frame = tk.Frame(lobby, bg=theme.get('bg', '#282a36'))
        header_frame.pack(fill='x', padx=16, pady=(14, 2))

        tk.Label(
            header_frame,
            text="🎮 Jeux pour Enfants",
            font=("Arial", 20, "bold"),
            bg=theme.get('bg', '#282a36'),
            fg=theme.get('fg', '#f8f8f2'),
        ).pack()

        tk.Label(
            header_frame,
            text="Choisissez un jeu pour commencer !",
            font=("Arial", 11),
            bg=theme.get('bg', '#282a36'),
            fg=theme.get('fg', '#f8f8f2'),
        ).pack(pady=(2, 8))

        ttk.Separator(lobby, orient='horizontal').pack(fill='x', padx=16, pady=(0, 10))

        # ── Game buttons grid ─────────────────────────
        grid_frame = tk.Frame(lobby, bg=theme.get('bg', '#282a36'))
        grid_frame.pack(fill='both', expand=True, padx=16, pady=4)

        games = self.get_all_games()
        for index, game in enumerate(games):
            row = index // 2
            col = index % 2
            gid = game['id']
            btn_text = f"{game['name']}\nÂge : {game['age']}"
            btn = tk.Button(
                grid_frame,
                text=btn_text,
                width=28,
                height=3,
                font=("Arial", 11),
                bg=theme.get('btn_bg', '#6272a4'),
                fg=theme.get('btn_fg', '#f8f8f2'),
                activebackground=theme.get('toolbar_bg', '#44475a'),
                activeforeground=theme.get('btn_fg', '#f8f8f2'),
                relief='flat',
                cursor='hand2',
                command=lambda g=gid: self.launch_game(g, parent_window, theme),
            )
            btn.grid(row=row, column=col, padx=10, pady=6, sticky='nsew')

        for c in range(2):
            grid_frame.columnconfigure(c, weight=1)
        for r in range(5):
            grid_frame.rowconfigure(r, weight=1)

        # ── Footer ────────────────────────────────────
        ttk.Separator(lobby, orient='horizontal').pack(fill='x', padx=16, pady=(6, 0))

        footer = tk.Frame(lobby, bg=theme.get('bg', '#282a36'))
        footer.pack(fill='x', padx=16, pady=10)

        tk.Button(
            footer,
            text="❌ Fermer",
            font=("Arial", 10),
            bg=theme.get('btn_bg', '#6272a4'),
            fg=theme.get('btn_fg', '#f8f8f2'),
            activebackground=theme.get('toolbar_bg', '#44475a'),
            activeforeground=theme.get('btn_fg', '#f8f8f2'),
            relief='flat',
            padx=10,
            pady=4,
            cursor='hand2',
            command=lobby.destroy,
        ).pack(side='right')
