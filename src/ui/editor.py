import re
import tkinter as tk
from tkinter import ttk
from src.utils.constants import EDITOR_FONT

# ── Pygments import (graceful fallback) ─────────────────
try:
    from pygments import lex
    from pygments.lexers import PythonLexer
    from pygments.token import Token
    _HAS_PYGMENTS = True
    _LEXER = PythonLexer()
except ImportError:
    _HAS_PYGMENTS = False

# ── Token color map (Dracula-inspired) ──────────────────
TOKEN_COLORS = {
    "keyword":    "#ff79c6",
    "builtin":    "#8be9fd",
    "funcname":   "#50fa7b",
    "classname":  "#50fa7b",
    "string":     "#f1fa8c",
    "number":     "#bd93f9",
    "comment":    "#6272a4",
    "operator":   "#ff79c6",
    "decorator":  "#ffb86c",
}

# ── Regex fallback colors ───────────────────────────────
FALLBACK_KEYWORDS = (
    "import", "from", "def", "class", "if", "else", "elif", "for", "while",
    "return", "True", "False", "None", "as", "try", "except", "with", "in",
    "not", "and", "or", "pass", "break", "continue", "lambda", "yield",
    "raise", "finally", "global", "nonlocal", "del", "assert", "is",
)

# ── Autocomplete dictionaries ───────────────────────────
AUTOCOMPLETE_ITEMS = [
    # Widgets
    "Label", "Button", "Entry", "Frame", "Text", "Canvas", "Listbox",
    "Scrollbar", "Checkbutton", "Radiobutton", "Scale", "Spinbox",
    "PanedWindow", "Menu", "Toplevel", "LabelFrame", "OptionMenu", "Message",
    # Methods
    ".pack()", ".grid()", ".place()", ".config()", ".bind()", ".get()",
    ".set()", ".pack_forget()", ".destroy()", ".after()", ".focus()",
    ".mainloop()", ".winfo_children()", ".update()",
    # Prefixes
    "tk.", "ttk.", "root.",
]


class _AutocompletePopup:
    """Borderless Toplevel with a Listbox for autocomplete suggestions."""

    def __init__(self, parent_text: tk.Text):
        self._parent = parent_text
        self._top = None
        self._listbox = None

    @property
    def visible(self) -> bool:
        return self._top is not None and self._top.winfo_exists()

    def show(self, items: list[str], x: int, y: int) -> None:
        self.hide()
        if not items:
            return
        self._top = tk.Toplevel(self._parent)
        self._top.wm_overrideredirect(True)
        self._top.wm_geometry(f"+{x}+{y}")
        self._top.attributes("-topmost", True)

        self._listbox = tk.Listbox(
            self._top,
            font=EDITOR_FONT,
            bg="#44475a",
            fg="#f8f8f2",
            selectbackground="#6272a4",
            selectforeground="#f8f8f2",
            relief="flat",
            bd=1,
            highlightthickness=0,
            exportselection=False,
            height=min(len(items), 8),
        )
        self._listbox.pack(fill="both", expand=True)
        for item in items:
            self._listbox.insert(tk.END, item)
        if items:
            self._listbox.selection_set(0)

    def hide(self) -> None:
        if self._top and self._top.winfo_exists():
            self._top.destroy()
        self._top = None
        self._listbox = None

    def get_selection(self) -> str | None:
        if not self.visible or not self._listbox:
            return None
        sel = self._listbox.curselection()
        if sel:
            return self._listbox.get(sel[0])
        return None

    def move_selection(self, delta: int) -> None:
        if not self.visible or not self._listbox:
            return
        sel = self._listbox.curselection()
        idx = sel[0] if sel else 0
        new_idx = max(0, min(idx + delta, self._listbox.size() - 1))
        self._listbox.selection_clear(0, tk.END)
        self._listbox.selection_set(new_idx)
        self._listbox.see(new_idx)


class EditorZone(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.header = tk.Label(
            self,
            text="\U0001f4dd Éditeur de code",
            anchor="w",
            font=("Segoe UI", 10, "bold"),
        )
        self.header.pack(fill="x", padx=4, pady=(4, 0))

        text_frame = tk.Frame(self)
        text_frame.pack(fill="both", expand=True, padx=4, pady=(0, 4))

        # ── Gutter (line numbers) ───────────────────
        self.gutter = tk.Text(
            text_frame,
            font=EDITOR_FONT,
            bg="#282a36",
            fg="#858585",
            insertbackground="#282a36",
            relief="flat",
            wrap="none",
            width=4,
            state="disabled",
            takefocus=False,
            cursor="arrow",
            padx=4,
        )
        self.gutter.tag_configure("right", justify="right")
        self.gutter.grid(row=0, column=0, sticky="ns")

        # ── Code editor ────────────────────────────
        self.text = tk.Text(
            text_frame,
            font=EDITOR_FONT,
            bg="#282a36",
            fg="#f8f8f2",
            insertbackground="#f8f8f2",
            selectbackground="#49483e",
            relief="flat",
            undo=True,
            wrap="none",
            tabs=("4c",),
        )

        # ── Scrollbars ─────────────────────────────
        self._v_scroll = ttk.Scrollbar(text_frame, orient="vertical",
                                       command=self._on_v_scroll)
        self._h_scroll = ttk.Scrollbar(text_frame, orient="horizontal",
                                       command=self.text.xview)
        self.text.configure(yscrollcommand=self._on_text_yscroll,
                            xscrollcommand=self._h_scroll.set)

        self.text.grid(row=0, column=1, sticky="nsew")
        self._v_scroll.grid(row=0, column=2, sticky="ns")
        self._h_scroll.grid(row=1, column=0, columnspan=3, sticky="ew")
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(1, weight=1)

        # ── Configure tags for highlighting ─────────
        for tag_name, color in TOKEN_COLORS.items():
            self.text.tag_configure(tag_name, foreground=color)
        # Fallback tags (same names, reused if pygments missing)
        self.text.tag_configure("kw_fallback", foreground="#ff79c6")
        self.text.tag_configure("str_fallback", foreground="#f1fa8c")
        self.text.tag_configure("cmt_fallback", foreground="#6272a4")

        # ── Autocomplete ───────────────────────────
        self._popup = _AutocompletePopup(self.text)

        # ── Bindings ───────────────────────────────
        self.text.bind("<KeyRelease>", self._on_key_release)
        self.text.bind("<MouseWheel>", self._on_mouse_event)
        self.text.bind("<Button-1>", self._on_mouse_event)
        self.text.bind("<Button-4>", self._on_mouse_event)
        self.text.bind("<Button-5>", self._on_mouse_event)
        self.text.bind("<Tab>", self._on_tab)
        self.text.bind("<Return>", self._on_return)
        self.text.bind("<Escape>", self._on_escape)
        self.text.bind("<Up>", self._on_arrow_up)
        self.text.bind("<Down>", self._on_arrow_down)

        self._update_line_numbers()

    # ── Public API ──────────────────────────────────

    def get_code(self) -> str:
        return self.text.get("1.0", tk.END).rstrip("\n")

    def set_code(self, code: str) -> None:
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", code)
        self._highlight()
        self._update_line_numbers()

    def clear(self) -> None:
        self.text.delete("1.0", tk.END)
        self._update_line_numbers()

    def apply_theme(self, theme: dict) -> None:
        ebg = theme.get("editor_bg", "#282a36")
        efg = theme.get("editor_fg", "#f8f8f2")
        gbg = theme.get("gutter_bg", "#282a36")
        gfg = theme.get("gutter_fg", "#858585")
        self.text.configure(bg=ebg, fg=efg, insertbackground=efg)
        self.gutter.configure(bg=gbg, fg=gfg, insertbackground=gbg)
        self.header.configure(bg=theme.get("bg", self.header.cget("bg")),
                              fg=theme.get("fg", self.header.cget("fg")))
        self.configure(bg=theme.get("bg", self.cget("bg")))

    # ── Scrolling sync ──────────────────────────────

    def _on_v_scroll(self, *args) -> None:
        self.text.yview(*args)
        self.gutter.yview(*args)

    def _on_text_yscroll(self, first, last) -> None:
        self._v_scroll.set(first, last)
        self.gutter.yview_moveto(first)

    def _on_mouse_event(self, event=None) -> None:
        self.after(10, self._update_line_numbers)

    # ── Line numbers ────────────────────────────────

    def _update_line_numbers(self) -> None:
        code = self.text.get("1.0", tk.END)
        line_count = code.count("\n")
        if code and not code.endswith("\n"):
            line_count += 1
        if line_count < 1:
            line_count = 1

        gutter_lines = "\n".join(str(i) for i in range(1, line_count + 1))

        self.gutter.configure(state="normal")
        self.gutter.delete("1.0", tk.END)
        self.gutter.insert("1.0", gutter_lines, "right")
        self.gutter.configure(state="disabled")

        first_visible = self.text.yview()[0]
        self.gutter.yview_moveto(first_visible)

    # ── Key event handler ───────────────────────────

    def _on_key_release(self, event=None) -> None:
        # Ignore modifier-only and navigation keys when popup is open
        if event and event.keysym in ("Shift_L", "Shift_R", "Control_L",
                                       "Control_R", "Alt_L", "Alt_R",
                                       "Up", "Down", "Escape", "Tab",
                                       "Return"):
            return
        self._highlight()
        self._update_line_numbers()
        self._try_autocomplete()

    # ── Syntax highlighting ─────────────────────────

    def _highlight(self) -> None:
        if _HAS_PYGMENTS:
            self._highlight_pygments()
        else:
            self._highlight_fallback()

    def _highlight_pygments(self) -> None:
        code = self.text.get("1.0", tk.END)
        all_tags = list(TOKEN_COLORS.keys())
        for tag in all_tags:
            self.text.tag_remove(tag, "1.0", tk.END)

        offset = 0
        for token_type, value in lex(code, _LEXER):
            end_offset = offset + len(value)
            tag = self._token_to_tag(token_type)
            if tag:
                start_idx = self._offset_to_index(offset, code)
                end_idx = self._offset_to_index(end_offset, code)
                self.text.tag_add(tag, start_idx, end_idx)
            offset = end_offset

    def _token_to_tag(self, token_type) -> str | None:
        if token_type in Token.Keyword or token_type in Token.Keyword.Namespace:
            return "keyword"
        if token_type in Token.Name.Builtin:
            return "builtin"
        if token_type in Token.Name.Function:
            return "funcname"
        if token_type in Token.Name.Class:
            return "classname"
        if token_type in Token.Name.Decorator:
            return "decorator"
        if token_type in Token.Literal.String:
            return "string"
        if token_type in Token.Literal.Number:
            return "number"
        if token_type in Token.Comment:
            return "comment"
        if token_type in Token.Operator or token_type in Token.Punctuation:
            return "operator"
        return None

    def _highlight_fallback(self) -> None:
        code = self.text.get("1.0", tk.END)
        for tag in ("kw_fallback", "str_fallback", "cmt_fallback"):
            self.text.tag_remove(tag, "1.0", tk.END)

        # Comments
        for m in re.finditer(r"#[^\n]*", code):
            self.text.tag_add("cmt_fallback",
                              self._offset_to_index(m.start(), code),
                              self._offset_to_index(m.end(), code))
        # Strings
        for m in re.finditer(r'(\"\"\"[\s\S]*?\"\"\"|\'\'\'[\s\S]*?\'\'\'|\"[^\"\n]*\"|\'[^\'\n]*\')', code):
            self.text.tag_add("str_fallback",
                              self._offset_to_index(m.start(), code),
                              self._offset_to_index(m.end(), code))
        # Keywords
        for kw in FALLBACK_KEYWORDS:
            for m in re.finditer(rf"\b{kw}\b", code):
                self.text.tag_add("kw_fallback",
                                  self._offset_to_index(m.start(), code),
                                  self._offset_to_index(m.end(), code))

    def _offset_to_index(self, offset: int, code: str) -> str:
        line = code[:offset].count("\n") + 1
        col = offset - code[:offset].rfind("\n") - 1
        return f"{line}.{col}"

    # ── Autocomplete ────────────────────────────────

    def _try_autocomplete(self) -> None:
        prefix = self._get_current_word()
        if len(prefix) < 2:
            self._popup.hide()
            return

        matches = [item for item in AUTOCOMPLETE_ITEMS
                   if item.lower().startswith(prefix.lower()) and item != prefix]
        if not matches:
            self._popup.hide()
            return

        # Position below cursor
        try:
            bbox = self.text.bbox("insert")
            if bbox is None:
                self._popup.hide()
                return
            bx, by, bw, bh = bbox
            x = self.text.winfo_rootx() + bx
            y = self.text.winfo_rooty() + by + bh + 2
        except tk.TclError:
            self._popup.hide()
            return

        self._popup.show(matches[:8], x, y)

    def _get_current_word(self) -> str:
        line = self.text.get("insert linestart", "insert")
        # Walk backwards to find the start of the current word/prefix
        word = ""
        for ch in reversed(line):
            if ch.isalnum() or ch in ("_", "."):
                word = ch + word
            else:
                break
        return word

    def _insert_completion(self) -> bool:
        if not self._popup.visible:
            return False
        selected = self._popup.get_selection()
        if selected is None:
            self._popup.hide()
            return False
        prefix = self._get_current_word()
        self._popup.hide()
        # Delete the typed prefix, insert the completion
        if prefix:
            line_text = self.text.get("insert linestart", "insert")
            start_col = len(line_text) - len(prefix)
            line_num = self.text.index("insert").split(".")[0]
            self.text.delete(f"{line_num}.{start_col}", "insert")
        self.text.insert("insert", selected)
        self._highlight()
        self._update_line_numbers()
        return True

    def _on_tab(self, event) -> str:
        if self._insert_completion():
            return "break"
        # Default tab: insert 4 spaces
        self.text.insert("insert", "    ")
        self._highlight()
        self._update_line_numbers()
        return "break"

    def _on_return(self, event) -> str | None:
        if self._insert_completion():
            return "break"
        return None  # Let default Enter behavior happen

    def _on_escape(self, event) -> None:
        self._popup.hide()

    def _on_arrow_up(self, event) -> str | None:
        if self._popup.visible:
            self._popup.move_selection(-1)
            return "break"
        return None

    def _on_arrow_down(self, event) -> str | None:
        if self._popup.visible:
            self._popup.move_selection(1)
            return "break"
        return None
