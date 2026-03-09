from tkinter import filedialog


class FileManager:
    def __init__(self):
        self._filetypes = [("Python files", "*.py"), ("All files", "*.*")]

    def open_file(self) -> str | None:
        path = filedialog.askopenfilename(
            title="Ouvrir un fichier Python",
            filetypes=self._filetypes,
        )
        if not path:
            return None
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def save_file(self, content: str) -> bool:
        path = filedialog.asksaveasfilename(
            title="Enregistrer le fichier",
            defaultextension=".py",
            filetypes=self._filetypes,
        )
        if not path:
            return False
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True

    def new_file(self) -> str:
        return ""
