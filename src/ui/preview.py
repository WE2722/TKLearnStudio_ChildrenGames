import traceback
import tkinter as tk
from tkinter import ttk


class PreviewZone(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self._error_callback = None
        self._success_callback = None

        self.header = tk.Label(
            self,
            text="\U0001f441 Prévisualisation",
            anchor="w",
            font=("Segoe UI", 10, "bold"),
        )
        self.header.pack(fill="x", padx=4, pady=(4, 0))

        self.render_area = tk.Frame(self, bg="white", relief="sunken", bd=1)
        self.render_area.pack(fill="both", expand=True, padx=4, pady=(0, 4))

    def execute_code(self, code: str) -> tuple[bool, str | None]:
        self.clear()
        exec_globals = {
            "tk": tk,
            "ttk": ttk,
            "root": self.render_area,
            "__builtins__": __builtins__,
        }
        try:
            exec(code, exec_globals)
            if self._success_callback:
                self._success_callback()
            return (True, None)
        except Exception:
            tb = traceback.format_exc()
            if self._error_callback:
                self._error_callback(tb)
            return (False, tb)

    def clear(self) -> None:
        for child in self.render_area.winfo_children():
            child.destroy()

    def set_error_callback(self, fn) -> None:
        self._error_callback = fn

    def set_success_callback(self, fn) -> None:
        self._success_callback = fn

    def apply_theme(self, theme: dict) -> None:
        self.header.configure(bg=theme.get("bg", self.header.cget("bg")),
                              fg=theme.get("fg", self.header.cget("fg")))
        self.configure(bg=theme.get("bg", self.cget("bg")))
        self.render_area.configure(bg=theme.get("preview_bg", "white"))
