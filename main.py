import os
import sys
import tkinter as tk
from tkinter import ttk

from src.utils.constants import (
    APP_TITLE, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT,
    THEME_DARK, THEME_LIGHT,
)
from src.ui.editor import EditorZone
from src.ui.preview import PreviewZone
from src.ui.console import ConsoleZone
from src.ui.menus import MenuBar
from src.core.file_manager import FileManager
from src.core.lesson_loader import LessonLoader
from src.core.progress_manager import ProgressManager
from src.games.game_manager import GameManager


class TkLearnStudio:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.root.geometry("1100x720")

        # ── State ───────────────────────────────────
        self.current_theme = THEME_DARK
        self.current_lesson_name = None

        # ── Core modules ────────────────────────────
        self.file_manager = FileManager()
        self.lesson_loader = LessonLoader()
        self.game_manager = GameManager()
        self.game_manager.current_theme = self.current_theme

        app_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(app_dir, "data")
        self.progress_manager = ProgressManager(data_dir=data_dir)

        lessons_dir = os.path.join(app_dir, "lessons")
        self.external_lessons = self.lesson_loader.scan_external_lessons(lessons_dir)

        # ── Build UI ────────────────────────────────
        self._build_menu()
        self._build_toolbar()
        self._build_main_area()
        self._build_console()
        self._bind_shortcuts()

        # ── Initial state ───────────────────────────
        self._apply_full_theme(self.current_theme)
        self._update_progress_bar()

        # Load default lesson
        default_code = self.lesson_loader.load_lesson("lesson_empty.py")
        if default_code:
            self.editor.set_code(default_code)
            self.current_lesson_name = "lesson_empty.py"

        self.console.show_info(
            "Bienvenue dans TkLearn Studio ! Appuyez sur F5 pour exécuter votre code."
        )

    # ── Menu ────────────────────────────────────────

    def _build_menu(self) -> None:
        callbacks = {
            "new": self._on_new,
            "open": self._on_open,
            "save": self._on_save,
            "quit": self._on_quit,
            "run": self.run_code,
            "reset_preview": self._on_reset_preview,
            "load_lesson": self._load_lesson,
            "toggle_theme": self._toggle_theme,
            "reset_progress": self._reset_progress,
            "color_picker": lambda: None,
            "show_about": lambda: None,
            "open_games": self._on_open_games,
            "launch_game": self._on_launch_game,
        }
        self.menubar = MenuBar(
            self.root,
            callbacks,
            self.lesson_loader.get_lesson_list(),
            self.external_lessons,
        )
        self.root.config(menu=self.menubar)
        self.menubar.update_lesson_labels(self.progress_manager.get_all_progress())

    # ── Toolbar ─────────────────────────────────────

    def _build_toolbar(self) -> None:
        self.toolbar = tk.Frame(self.root, bd=1, relief="flat")
        self.toolbar.pack(fill="x", side="top")

        self.btn_run = tk.Button(
            self.toolbar, text="\u25b6 Lancer (F5)",
            command=self.run_code, relief="flat", padx=8, pady=4,
        )
        self.btn_run.pack(side="left", padx=4, pady=4)

        self.btn_clear = tk.Button(
            self.toolbar, text="\U0001f5d1 Effacer",
            command=self._on_clear, relief="flat", padx=8, pady=4,
        )
        self.btn_clear.pack(side="left", padx=4, pady=4)

        self.btn_save = tk.Button(
            self.toolbar, text="\U0001f4be Sauvegarder",
            command=self._on_save, relief="flat", padx=8, pady=4,
        )
        self.btn_save.pack(side="left", padx=4, pady=4)

        self.btn_load = tk.Button(
            self.toolbar, text="\U0001f4c2 Charger leçon",
            command=self._load_lesson_dialog, relief="flat", padx=8, pady=4,
        )
        self.btn_load.pack(side="left", padx=4, pady=4)

        self.btn_theme = tk.Button(
            self.toolbar, text="\U0001f319 Thème",
            command=self._toggle_theme, relief="flat", padx=8, pady=4,
        )
        self.btn_theme.pack(side="left", padx=4, pady=4)

        self.btn_games = tk.Button(
            self.toolbar, text="🎮 Jeux",
            command=self._on_open_games, relief="flat", padx=8, pady=4,
        )
        self.btn_games.pack(side="left", padx=4, pady=4)

        # Progress bar (right side)
        self.progress_label = tk.Label(
            self.toolbar, text="0/0 leçons (0%)",
            font=("Segoe UI", 9),
        )
        self.progress_label.pack(side="right", padx=(4, 10), pady=4)

        self.progress_bar = ttk.Progressbar(
            self.toolbar, length=120, mode="determinate", maximum=100,
        )
        self.progress_bar.pack(side="right", padx=4, pady=4)

    # ── Main area ───────────────────────────────────

    def _build_main_area(self) -> None:
        self.paned = ttk.PanedWindow(self.root, orient="horizontal")
        self.paned.pack(fill="both", expand=True, padx=4, pady=4)

        self.editor = EditorZone(self.paned)
        self.preview = PreviewZone(self.paned)

        self.paned.add(self.editor, weight=1)
        self.paned.add(self.preview, weight=1)

    # ── Console ─────────────────────────────────────

    def _build_console(self) -> None:
        self.console = ConsoleZone(self.root, height=150)
        self.console.pack(fill="x", side="bottom", padx=4, pady=(0, 4))

    # ── Keyboard shortcuts ──────────────────────────

    def _bind_shortcuts(self) -> None:
        self.root.bind("<F5>", lambda e: self.run_code())
        self.root.bind("<Control-s>", lambda e: self._on_save())
        self.root.bind("<Control-n>", lambda e: self._on_new())
        self.root.bind("<Control-o>", lambda e: self._on_open())
        self.root.bind("<Control-q>", lambda e: self._on_quit())

    # ── Core: run code ──────────────────────────────

    def run_code(self) -> None:
        self.console.clear()
        code = self.editor.get_code()
        if not code.strip():
            self.console.show_info("Rien à exécuter — l'éditeur est vide.")
            return
        success, error = self.preview.execute_code(code)
        if success:
            self.console.show_success("Exécution terminée avec succès !")
            if self.current_lesson_name:
                self.progress_manager.mark_complete(self.current_lesson_name)
                self._update_progress_bar()
                self.menubar.update_lesson_labels(
                    self.progress_manager.get_all_progress()
                )
        else:
            self.console.show_error(error)

    # ── Lesson loading ──────────────────────────────

    def _load_lesson(self, key: str) -> None:
        content = self.lesson_loader.load_lesson(key)
        if content is not None:
            self.editor.set_code(content)
            self.current_lesson_name = key
            self.console.clear()
            self.console.show_info(f"Leçon chargée : {key}")
        else:
            self.console.show_error(f"Leçon introuvable : {key}")

    def _load_lesson_dialog(self) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title("Charger une leçon")
        dialog.geometry("380x320")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog, text="Sélectionnez une leçon :",
            font=("Segoe UI", 11, "bold"),
        ).pack(padx=10, pady=(10, 5))

        listbox = tk.Listbox(dialog, font=("Segoe UI", 11), activestyle="dotbox")
        listbox.pack(fill="both", expand=True, padx=10, pady=5)

        all_items = []
        lessons = self.lesson_loader.get_lesson_list()
        for lesson in lessons:
            listbox.insert(tk.END, lesson["name"])
            all_items.append(lesson["file"])

        if self.external_lessons:
            listbox.insert(tk.END, "── Leçons externes ──")
            all_items.append(None)
            for ext in self.external_lessons:
                listbox.insert(tk.END, ext["name"])
                all_items.append(ext["path"])

        def on_confirm():
            sel = listbox.curselection()
            if sel:
                idx = sel[0]
                key = all_items[idx]
                if key is not None:
                    self._load_lesson(key)
            dialog.destroy()

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(btn_frame, text="Charger", command=on_confirm).pack(
            side="left", padx=5
        )
        ttk.Button(btn_frame, text="Annuler", command=dialog.destroy).pack(
            side="right", padx=5
        )

    # ── File callbacks ──────────────────────────────

    def _on_new(self) -> None:
        self.editor.set_code(self.file_manager.new_file())
        self.preview.clear()
        self.console.clear()
        self.current_lesson_name = None
        self.console.show_info("Nouveau fichier créé.")

    def _on_open(self) -> None:
        content = self.file_manager.open_file()
        if content is not None:
            self.editor.set_code(content)
            self.current_lesson_name = None
            self.console.clear()
            self.console.show_info("Fichier ouvert avec succès.")

    def _on_save(self) -> None:
        code = self.editor.get_code()
        if self.file_manager.save_file(code):
            self.console.show_success("Fichier enregistré avec succès.")
        else:
            self.console.show_info("Enregistrement annulé.")

    def _on_quit(self) -> None:
        self.root.destroy()

    def _on_reset_preview(self) -> None:
        self.preview.clear()
        self.console.clear()
        self.console.show_info("Aperçu réinitialisé.")

    def _on_clear(self) -> None:
        self.editor.clear()
        self.preview.clear()
        self.console.clear()
        self.current_lesson_name = None
        self.console.show_info("Éditeur et aperçu effacés.")

    # ── Theme ───────────────────────────────────────

    def _toggle_theme(self) -> None:
        if self.current_theme["name"] == "dark":
            self.current_theme = THEME_LIGHT
        else:
            self.current_theme = THEME_DARK
        self._apply_full_theme(self.current_theme)

    def _apply_full_theme(self, theme: dict) -> None:
        bg = theme["bg"]
        fg = theme["fg"]
        tb_bg = theme["toolbar_bg"]
        btn_bg = theme["btn_bg"]
        btn_fg = theme["btn_fg"]

        self.root.configure(bg=bg)

        # Toolbar
        self.toolbar.configure(bg=tb_bg)
        for btn in (self.btn_run, self.btn_clear, self.btn_save,
                    self.btn_load, self.btn_theme, self.btn_games):
            btn.configure(bg=btn_bg, fg=btn_fg, activebackground=tb_bg,
                          activeforeground=btn_fg)
        self.progress_label.configure(bg=tb_bg, fg=btn_fg)

        # Update theme button label
        if theme["name"] == "dark":
            self.btn_theme.configure(text="\U0001f319 Thème")
        else:
            self.btn_theme.configure(text="\u2600\ufe0f Thème")

        # Zones
        self.editor.apply_theme(theme)
        self.preview.apply_theme(theme)
        self.console.apply_theme(theme)
        # Propagate theme to game manager
        self.game_manager.current_theme = theme

    # ── Progress bar ────────────────────────────────

    def _update_progress_bar(self) -> None:
        stats = self.progress_manager.get_stats()
        done = stats["done"]
        total = stats["total"]
        pct = stats["percent"]
        self.progress_bar["value"] = pct
        self.progress_label.configure(text=f"{done}/{total} leçons ({pct}%)")

    # ── Reset progress ──────────────────────────────

    def _reset_progress(self) -> None:
        self.progress_manager.reset_progress()
        self._update_progress_bar()
        self.menubar.update_lesson_labels({})
        self.console.clear()
        self.console.show_info("Progression réinitialisée.")

    # ── Games ────────────────────────────────────────

    def _on_open_games(self) -> None:
        self.game_manager.open_games_lobby(self.root, self.current_theme)

    def _on_launch_game(self, game_id: str) -> None:
        self.game_manager.launch_game(game_id, self.root, self.current_theme)

    # ── Run ─────────────────────────────────────────

    def run(self) -> None:
        self.root.mainloop()


def main():
    app = TkLearnStudio()
    app.run()


if __name__ == "__main__":
    main()
