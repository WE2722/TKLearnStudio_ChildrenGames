import os
import glob


class LessonLoader:
    LESSONS = [
        {"name": "01 - Fenêtre vide", "file": "lesson_empty.py"},
        {"name": "02 - Label simple", "file": "lesson_label.py"},
        {"name": "03 - Bouton & événement", "file": "lesson_button.py"},
        {"name": "04 - Champ de saisie", "file": "lesson_entry.py"},
        {"name": "05 - Mise en page Grid", "file": "lesson_grid.py"},
    ]

    LESSON_CONTENTS = {
        "lesson_empty.py": (
            "# Leçon 1 : Fenêtre vide avec titre\n"
            "# 'root' est votre conteneur principal (un Frame).\n"
            "\n"
            "root.configure(bg='#ecf0f1')\n"
            "\n"
            "titre = tk.Label(\n"
            "    root,\n"
            "    text='Bienvenue dans TkLearn Studio !',\n"
            "    font=('Segoe UI', 18, 'bold'),\n"
            "    bg='#ecf0f1',\n"
            "    fg='#2c3e50'\n"
            ")\n"
            "titre.pack(expand=True)\n"
        ),

        "lesson_label.py": (
            "# Leçon 2 : Labels avec différents styles\n"
            "\n"
            "lbl1 = tk.Label(\n"
            "    root,\n"
            "    text='Label en relief RAISED',\n"
            "    font=('Helvetica', 14, 'bold'),\n"
            "    fg='white', bg='#3498db',\n"
            "    relief='raised', bd=3,\n"
            "    padx=15, pady=8\n"
            ")\n"
            "lbl1.pack(pady=8, fill='x', padx=20)\n"
            "\n"
            "lbl2 = tk.Label(\n"
            "    root,\n"
            "    text='Label en relief SUNKEN',\n"
            "    font=('Georgia', 13, 'italic'),\n"
            "    fg='#2c3e50', bg='#f1c40f',\n"
            "    relief='sunken', bd=3,\n"
            "    padx=15, pady=8\n"
            ")\n"
            "lbl2.pack(pady=8, fill='x', padx=20)\n"
            "\n"
            "lbl3 = tk.Label(\n"
            "    root,\n"
            "    text='Label en relief GROOVE',\n"
            "    font=('Courier New', 12),\n"
            "    fg='white', bg='#e74c3c',\n"
            "    relief='groove', bd=3,\n"
            "    padx=15, pady=8\n"
            ")\n"
            "lbl3.pack(pady=8, fill='x', padx=20)\n"
        ),

        "lesson_button.py": (
            "# Leçon 3 : Boutons et événements\n"
            "\n"
            "compteur = tk.IntVar(value=0)\n"
            "\n"
            "label = tk.Label(\n"
            "    root,\n"
            "    text='Compteur : 0',\n"
            "    font=('Segoe UI', 16, 'bold'),\n"
            "    fg='#2c3e50'\n"
            ")\n"
            "label.pack(pady=15)\n"
            "\n"
            "def incrementer():\n"
            "    compteur.set(compteur.get() + 1)\n"
            "    label.config(text=f'Compteur : {compteur.get()}')\n"
            "\n"
            "def reinitialiser():\n"
            "    compteur.set(0)\n"
            "    label.config(text='Compteur : 0')\n"
            "\n"
            "btn_frame = tk.Frame(root)\n"
            "btn_frame.pack(pady=10)\n"
            "\n"
            "tk.Button(\n"
            "    btn_frame,\n"
            "    text='+1',\n"
            "    font=('Segoe UI', 12),\n"
            "    command=incrementer,\n"
            "    bg='#2ecc71', fg='white',\n"
            "    width=10\n"
            ").pack(side='left', padx=5)\n"
            "\n"
            "tk.Button(\n"
            "    btn_frame,\n"
            "    text='Reset',\n"
            "    font=('Segoe UI', 12),\n"
            "    command=reinitialiser,\n"
            "    bg='#e74c3c', fg='white',\n"
            "    width=10\n"
            ").pack(side='left', padx=5)\n"
        ),

        "lesson_entry.py": (
            "# Leçon 4 : Champ de saisie avec validation\n"
            "\n"
            "tk.Label(\n"
            "    root,\n"
            "    text='Entrez votre nom :',\n"
            "    font=('Segoe UI', 12)\n"
            ").pack(pady=(10, 0))\n"
            "\n"
            "entry = tk.Entry(root, font=('Segoe UI', 12), width=30)\n"
            "entry.pack(pady=5)\n"
            "\n"
            "result_label = tk.Label(\n"
            "    root,\n"
            "    text='',\n"
            "    font=('Segoe UI', 14, 'bold')\n"
            ")\n"
            "result_label.pack(pady=10)\n"
            "\n"
            "def valider():\n"
            "    nom = entry.get().strip()\n"
            "    if not nom:\n"
            "        result_label.config(\n"
            "            text='\\u26a0 Veuillez entrer un nom !',\n"
            "            fg='#e74c3c'\n"
            "        )\n"
            "    else:\n"
            "        result_label.config(\n"
            "            text=f'Bonjour, {nom} !',\n"
            "            fg='#27ae60'\n"
            "        )\n"
            "\n"
            "tk.Button(\n"
            "    root,\n"
            "    text='Valider',\n"
            "    font=('Segoe UI', 11),\n"
            "    command=valider,\n"
            "    bg='#3498db', fg='white'\n"
            ").pack(pady=5)\n"
        ),

        "lesson_grid.py": (
            "# Leçon 5 : Mise en page Grid - Formulaire\n"
            "\n"
            "header = tk.Label(\n"
            "    root,\n"
            "    text=\"Formulaire d'inscription\",\n"
            "    font=('Segoe UI', 14, 'bold'),\n"
            "    bg='#34495e', fg='white'\n"
            ")\n"
            "header.grid(row=0, column=0, columnspan=2,\n"
            "            sticky='ew', padx=5, pady=5)\n"
            "\n"
            "fields = ['Nom', 'Prénom', 'Email', 'Ville']\n"
            "entries = {}\n"
            "\n"
            "for i, field in enumerate(fields, start=1):\n"
            "    tk.Label(\n"
            "        root,\n"
            "        text=f'{field} :',\n"
            "        font=('Segoe UI', 11)\n"
            "    ).grid(row=i, column=0, sticky='e', padx=5, pady=5)\n"
            "    e = tk.Entry(root, font=('Segoe UI', 11))\n"
            "    e.grid(row=i, column=1, sticky='ew', padx=5, pady=5)\n"
            "    entries[field] = e\n"
            "\n"
            "def soumettre():\n"
            "    data = {k: v.get() for k, v in entries.items()}\n"
            "    msg = '\\n'.join(f'{k}: {v}' for k, v in data.items())\n"
            "    from tkinter import messagebox\n"
            "    messagebox.showinfo('Données saisies', msg)\n"
            "\n"
            "tk.Button(\n"
            "    root,\n"
            "    text='Envoyer',\n"
            "    font=('Segoe UI', 11, 'bold'),\n"
            "    bg='#2ecc71', fg='white',\n"
            "    command=soumettre\n"
            ").grid(row=len(fields)+1, column=0, columnspan=2, pady=10)\n"
            "\n"
            "root.columnconfigure(1, weight=1)\n"
        ),
    }

    def get_lesson_list(self) -> list[dict]:
        return list(self.LESSONS)

    def load_lesson(self, key: str) -> str | None:
        # If key is a full path that exists on disk, read from disk
        if os.path.isabs(key) and os.path.isfile(key):
            with open(key, "r", encoding="utf-8") as f:
                return f.read()
        # Otherwise look up in embedded lessons
        return self.LESSON_CONTENTS.get(key)

    def scan_external_lessons(self, lessons_dir: str) -> list[dict]:
        if not os.path.isdir(lessons_dir):
            return []
        results = []
        for path in sorted(glob.glob(os.path.join(lessons_dir, "*.py"))):
            stem = os.path.splitext(os.path.basename(path))[0]
            results.append({"name": stem, "path": os.path.abspath(path)})
        return results
