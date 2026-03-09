import tkinter as tk
from src.utils.constants import CONSOLE_FONT


COLOR_SUCCESS = "#6bff6b"
COLOR_ERROR = "#ff6b6b"
COLOR_INFO = "#6bb5ff"


class ConsoleZone(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.header = tk.Label(
            self,
            text="Console",
            anchor="w",
            font=("Segoe UI", 10, "bold"),
        )
        self.header.pack(fill="x", padx=4, pady=(4, 0))

        self.text = tk.Text(
            self,
            state="disabled",
            font=CONSOLE_FONT,
            bg="#1e1e1e",
            fg="#f8f8f2",
            insertbackground="#f8f8f2",
            relief="flat",
            wrap="word",
            height=8,
        )
        self.text.pack(fill="both", expand=True, padx=4, pady=(0, 4))

        self.text.tag_configure("success", foreground=COLOR_SUCCESS)
        self.text.tag_configure("error", foreground=COLOR_ERROR)
        self.text.tag_configure("info", foreground=COLOR_INFO)

    def _append(self, msg: str, tag: str) -> None:
        self.text.configure(state="normal")
        self.text.insert(tk.END, msg + "\n", tag)
        self.text.configure(state="disabled")
        self.text.see(tk.END)

    def show_success(self, msg: str) -> None:
        self._append(f"[OK] {msg}", "success")

    def show_error(self, msg: str) -> None:
        self._append(f"[ERR] {msg}", "error")

    def show_info(self, msg: str) -> None:
        self._append(f"[INFO] {msg}", "info")

    def clear(self) -> None:
        self.text.configure(state="normal")
        self.text.delete("1.0", tk.END)
        self.text.configure(state="disabled")

    def apply_theme(self, theme: dict) -> None:
        bg = theme.get("console_bg", "#1e1e1e")
        fg = theme.get("console_fg", "#f8f8f2")
        self.text.configure(bg=bg, fg=fg, insertbackground=fg)
        self.header.configure(bg=theme.get("bg", self.header.cget("bg")),
                              fg=theme.get("fg", self.header.cget("fg")))
        self.configure(bg=theme.get("bg", self.cget("bg")))
