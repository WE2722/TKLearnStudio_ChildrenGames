# Leçon externe : Listbox avec ajout et suppression

frame = tk.Frame(root)
frame.pack(fill='both', expand=True, padx=10, pady=10)

tk.Label(frame, text='Gestion de liste',
         font=('Segoe UI', 14, 'bold')).pack(pady=(0, 8))

# Zone de saisie
entry_frame = tk.Frame(frame)
entry_frame.pack(fill='x', pady=5)

entry = tk.Entry(entry_frame, font=('Segoe UI', 11))
entry.pack(side='left', fill='x', expand=True, padx=(0, 5))

# Listbox avec scrollbar
list_frame = tk.Frame(frame)
list_frame.pack(fill='both', expand=True, pady=5)

scrollbar = tk.Scrollbar(list_frame, orient='vertical')
listbox = tk.Listbox(
    list_frame,
    font=('Segoe UI', 11),
    selectbackground='#3498db',
    selectforeground='white',
    yscrollcommand=scrollbar.set,
    height=8
)
scrollbar.config(command=listbox.yview)
listbox.pack(side='left', fill='both', expand=True)
scrollbar.pack(side='right', fill='y')

# Pré-remplir avec quelques éléments
for item in ['Python', 'Tkinter', 'Label', 'Button', 'Canvas']:
    listbox.insert(tk.END, item)

# Label de statut
status = tk.Label(frame, text='', font=('Segoe UI', 10, 'italic'), fg='#7f8c8d')
status.pack(pady=(5, 0))

def ajouter():
    texte = entry.get().strip()
    if not texte:
        status.config(text='\u26a0 Entrez du texte avant d\'ajouter !', fg='#e74c3c')
        return
    listbox.insert(tk.END, texte)
    entry.delete(0, tk.END)
    status.config(text=f'\u2705 "{texte}" ajouté.', fg='#27ae60')

def supprimer():
    selection = listbox.curselection()
    if not selection:
        status.config(text='\u26a0 Sélectionnez un élément à supprimer !', fg='#e74c3c')
        return
    item_text = listbox.get(selection[0])
    listbox.delete(selection[0])
    status.config(text=f'\u274c "{item_text}" supprimé.', fg='#e67e22')

btn_frame = tk.Frame(frame)
btn_frame.pack(fill='x', pady=5)

tk.Button(
    btn_frame, text='Ajouter',
    font=('Segoe UI', 11),
    command=ajouter,
    bg='#2ecc71', fg='white', width=12
).pack(side='left', padx=5)

tk.Button(
    btn_frame, text='Supprimer',
    font=('Segoe UI', 11),
    command=supprimer,
    bg='#e74c3c', fg='white', width=12
).pack(side='left', padx=5)
