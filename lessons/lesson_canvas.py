# Leçon externe : Dessin sur Canvas
# Dessine différentes formes géométriques colorées

canvas = tk.Canvas(root, width=400, height=350, bg='#fdfefe')
canvas.pack(expand=True, padx=10, pady=10)

# Rectangle bleu
canvas.create_rectangle(20, 20, 150, 100,
                        fill='#3498db', outline='#2980b9', width=2)
canvas.create_text(85, 60, text='Rectangle',
                   font=('Segoe UI', 10), fill='white')

# Ovale rouge
canvas.create_oval(180, 20, 380, 120,
                   fill='#e74c3c', outline='#c0392b', width=2)
canvas.create_text(280, 70, text='Ovale',
                   font=('Segoe UI', 10), fill='white')

# Ligne verte
canvas.create_line(20, 150, 380, 150,
                   fill='#2ecc71', width=4, dash=(8, 4))

# Arc jaune
canvas.create_arc(20, 180, 180, 320,
                  start=0, extent=270,
                  fill='#f1c40f', outline='#f39c12', width=2)
canvas.create_text(100, 250, text='Arc',
                   font=('Segoe UI', 10))

# Polygone violet (étoile simplifiée)
canvas.create_polygon(
    280, 180, 300, 240, 370, 240,
    310, 275, 330, 340, 280, 300,
    230, 340, 250, 275, 190, 240,
    260, 240,
    fill='#9b59b6', outline='#8e44ad', width=2
)
canvas.create_text(280, 260, text='Polygone',
                   font=('Segoe UI', 9), fill='white')
