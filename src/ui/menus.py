import tkinter as tk
from tkinter import messagebox, colorchooser
from src.utils.constants import APP_TITLE, APP_VERSION
from src.games.game_manager import GAME_REGISTRY


class MenuBar(tk.Menu):
    def __init__(self, parent, callbacks: dict,
                 lessons: list, external_lessons: list):
        super().__init__(parent, tearoff=0)
        self._callbacks = callbacks
        self._lessons = lessons
        self._external_lessons = external_lessons
        self._lecons_menu = None
        self._theme_label_index = None
        self._is_dark = True

        self._build_fichier_menu()
        self._build_lecons_menu()
        self._build_execution_menu()
        self._build_jeux_menu()
        self._build_outils_menu()
        self._build_aide_menu()

    # ── Fichier ─────────────────────────────────────

    def _build_fichier_menu(self) -> None:
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Nouveau", accelerator="Ctrl+N",
                         command=self._callbacks["new"])
        menu.add_command(label="Ouvrir", accelerator="Ctrl+O",
                         command=self._callbacks["open"])
        menu.add_command(label="Enregistrer", accelerator="Ctrl+S",
                         command=self._callbacks["save"])
        menu.add_separator()
        menu.add_command(label="Quitter", accelerator="Ctrl+Q",
                         command=self._callbacks["quit"])
        self.add_cascade(label="Fichier", menu=menu)

    # ── Leçons ──────────────────────────────────────

    def _build_lecons_menu(self) -> None:
        self._lecons_menu = tk.Menu(self, tearoff=0)

        # Embedded lessons
        for lesson in self._lessons:
            key = lesson["file"]
            name = lesson["name"]
            label = f"\u25cb {name}"
            self._lecons_menu.add_command(
                label=label,
                command=lambda k=key: self._callbacks["load_lesson"](k),
            )

        # External lessons separator + items
        if self._external_lessons:
            self._lecons_menu.add_command(
                label="\u2500\u2500 Leçons externes \u2500\u2500",
                state="disabled",
            )
            for ext in self._external_lessons:
                path = ext["path"]
                self._lecons_menu.add_command(
                    label=ext["name"],
                    command=lambda p=path: self._callbacks["load_lesson"](p),
                )

        self.add_cascade(label="Leçons", menu=self._lecons_menu)

    # ── Exécution ───────────────────────────────────

    def _build_execution_menu(self) -> None:
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Lancer", accelerator="F5",
                         command=self._callbacks["run"])
        menu.add_command(label="Réinitialiser l'aperçu",
                         command=self._callbacks["reset_preview"])
        self.add_cascade(label="Exécution", menu=menu)

    # ── Jeux ────────────────────────────────────────

    def _build_jeux_menu(self) -> None:
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="🎮 Ouvrir le Lobby des Jeux...",
                         command=self._callbacks.get("open_games", lambda: None))
        menu.add_separator()
        for game in GAME_REGISTRY:
            gid = game['id']
            name = game['name']
            age = game['age']
            menu.add_command(
                label=f"{name}  ({age})",
                command=lambda g=gid: self._callbacks.get("launch_game",
                                                          lambda _: None)(g),
            )
        self.add_cascade(label="🎮 Jeux", menu=menu)

    # ── Outils ──────────────────────────────────────

    def _build_outils_menu(self) -> None:
        self._outils_menu = tk.Menu(self, tearoff=0)
        self._outils_menu.add_command(
            label="\U0001f319 Thème sombre",
            command=self._on_toggle_theme,
        )
        self._theme_label_index = 0
        self._outils_menu.add_command(
            label="\U0001f3a8 Sélecteur de couleurs",
            command=self._pick_color,
        )
        self._outils_menu.add_separator()
        self._outils_menu.add_command(
            label="Réinitialiser progression",
            command=self._callbacks["reset_progress"],
        )
        self.add_cascade(label="Outils", menu=self._outils_menu)

    def _on_toggle_theme(self) -> None:
        self._callbacks["toggle_theme"]()
        self._is_dark = not self._is_dark
        if self._is_dark:
            new_label = "\U0001f319 Thème sombre"
        else:
            new_label = "\u2600\ufe0f Thème clair"
        self._outils_menu.entryconfigure(
            self._theme_label_index, label=new_label
        )

    def _pick_color(self) -> None:
        result = colorchooser.askcolor(title="Choisir une couleur")
        if result and result[1]:
            hex_color = result[1]
            try:
                self.master.clipboard_clear()
                self.master.clipboard_append(hex_color)
            except tk.TclError:
                pass

    # ── Aide ────────────────────────────────────────

    def _build_aide_menu(self) -> None:
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="À propos", command=self._show_about)
        self.add_cascade(label="Aide", menu=menu)

    def _show_about(self) -> None:
        messagebox.showinfo(
            "À propos",
            f"{APP_TITLE} v{APP_VERSION}\n\n"
            "Un environnement d'apprentissage interactif\n"
            "pour Python et Tkinter.\n\n"
            "Écrivez du code à gauche, exécutez avec F5,\n"
            "et visualisez le résultat à droite !",
        )

    # ── Update lesson labels (○/✅) ─────────────────

    def update_lesson_labels(self, progress: dict) -> None:
        if not self._lecons_menu:
            return
        for i, lesson in enumerate(self._lessons):
            key = lesson["file"]
            name = lesson["name"]
            if progress.get(key, False):
                label = f"\u2705 {name}"
            else:
                label = f"\u25cb {name}"
            self._lecons_menu.entryconfigure(i, label=label)
