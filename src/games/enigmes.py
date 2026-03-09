"""Énigmes (Riddles) Game — 15 French child-appropriate riddles."""
import tkinter as tk
from tkinter import ttk
import unicodedata


def _normalize(text: str) -> str:
    """Lowercase + remove accents for accent-insensitive comparison."""
    nfkd = unicodedata.normalize('NFKD', text.lower().strip())
    return ''.join(c for c in nfkd if not unicodedata.combining(c))


RIDDLES = [
    {
        'question': "J'ai des aiguilles mais je ne couds pas. Que suis-je ?",
        'answer': 'horloge',
        'hint': "Je mesure le temps.",
    },
    {
        'question': "Plus je sèche, plus je suis mouillée. Que suis-je ?",
        'answer': 'serviette',
        'hint': "On m'utilise après le bain.",
    },
    {
        'question': "Je parle sans bouche et entends sans oreilles. Que suis-je ?",
        'answer': 'echo',
        'hint': "Je répète ce qu'on me dit dans les montagnes.",
    },
    {
        'question': "Je cours mais n'ai pas de jambes. Que suis-je ?",
        'answer': 'riviere',
        'hint': "Je coule entre les collines.",
    },
    {
        'question': "On me jette quand on a besoin de moi et on me reprend quand on n'a plus besoin. Que suis-je ?",
        'answer': 'ancre',
        'hint': "Je sers à arrêter les bateaux.",
    },
    {
        'question': "Je suis plein de trous mais je retiens l'eau. Que suis-je ?",
        'answer': 'eponge',
        'hint': "On m'utilise pour faire la vaisselle.",
    },
    {
        'question': "Je suis toujours devant toi mais ne peut pas être vu. Que suis-je ?",
        'answer': 'futur',
        'hint': "On dit que j'appartiens aux enfants.",
    },
    {
        'question': "Plus je vieillis, plus je grandis. Que suis-je ?",
        'answer': 'arbre',
        'hint': "Les oiseaux font leur nid sur moi.",
    },
    {
        'question': "Je n'ai pas de fenêtres, pas de portes, mais une pièce d'or est à l'intérieur. Que suis-je ?",
        'answer': 'oeuf',
        'hint': "Les poules me pondent.",
    },
    {
        'question': "Je suis léger comme une plume, mais même le plus fort ne peut me tenir longtemps. Que suis-je ?",
        'answer': 'souffle',
        'hint': "On me retient sous l'eau.",
    },
    {
        'question': "Je monte et descends sans bouger. Que suis-je ?",
        'answer': 'escalier',
        'hint': "Je relie les étages d'un immeuble.",
    },
    {
        'question': "J'ai quatre pattes le matin, deux pattes le midi, et trois pattes le soir. Que suis-je ?",
        'answer': 'homme',
        'hint': "C'est l'énigme du Sphinx.",
    },
    {
        'question': "Je suis blanc en hiver et vert en été. Je recouche les arbres. Que suis-je ?",
        'answer': 'neige',
        'hint': "Les enfants adorent jouer avec moi.",
    },
    {
        'question': "J'ai une queue mais pas de corps. Je vole sans ailes. Que suis-je ?",
        'answer': 'cerf-volant',
        'hint': "On me fait voler par grand vent.",
    },
    {
        'question': "Je suis rond comme une pomme, plat comme une tarte. Je parle, je chante et j'entertain. Que suis-je ?",
        'answer': 'television',
        'hint': "On me regarde dans le salon.",
    },
]


class EnigmesGame:
    """Interactive riddles game in a Toplevel window."""

    def __init__(self, parent, theme: dict):
        self.parent = parent
        self.theme = theme

        self.win = tk.Toplevel(parent)
        self.win.title("🔍 Énigmes")
        self.win.geometry("600x550")
        self.win.resizable(True, True)
        self.win.configure(bg=theme.get('bg', '#282a36'))

        # State
        self.current = 0
        self.score = 0
        self.wrong_attempts = 0
        self.hint_used = False
        self._game_over = False

        self._build_ui()
        self.start_game()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        bg = self.theme.get('bg', '#282a36')
        fg = self.theme.get('fg', '#f8f8f2')
        btn_bg = self.theme.get('btn_bg', '#6272a4')
        btn_fg = self.theme.get('btn_fg', '#f8f8f2')
        tb_bg = self.theme.get('toolbar_bg', '#44475a')
        ed_bg = self.theme.get('editor_bg', '#1e1f29')

        # ── Top bar ──────────────────────────────────
        top = tk.Frame(self.win, bg=tb_bg)
        top.pack(fill='x')

        self.lbl_question_num = tk.Label(top, text="Énigme 1/15",
                                         font=("Segoe UI", 12, "bold"),
                                         bg=tb_bg, fg=fg)
        self.lbl_question_num.pack(side='left', padx=12, pady=6)

        self.lbl_score = tk.Label(top, text="Score : 0/15",
                                  font=("Segoe UI", 12), bg=tb_bg, fg=fg)
        self.lbl_score.pack(side='right', padx=12, pady=6)

        # ── Progress bar ─────────────────────────────
        progress_frame = tk.Frame(self.win, bg=bg)
        progress_frame.pack(fill='x', padx=12, pady=(6, 2))
        self.progress_bar = ttk.Progressbar(progress_frame, maximum=15,
                                             mode='determinate', length=560)
        self.progress_bar.pack(fill='x')

        # ── Question area ─────────────────────────────
        q_frame = tk.Frame(self.win, bg=ed_bg, bd=2, relief='flat')
        q_frame.pack(fill='x', padx=12, pady=8)

        self.lbl_question = tk.Label(
            q_frame, text="",
            font=("Arial", 14), bg=ed_bg, fg=fg,
            wraplength=540, justify='center', pady=16,
        )
        self.lbl_question.pack(fill='x', padx=10)

        # ── Answer entry ─────────────────────────────
        entry_frame = tk.Frame(self.win, bg=bg)
        entry_frame.pack(fill='x', padx=12, pady=4)

        self.entry = tk.Entry(
            entry_frame,
            font=("Arial", 14), bg=ed_bg, fg=fg,
            insertbackground=fg, relief='flat', bd=4,
            justify='center',
        )
        self.entry.pack(fill='x', ipady=6)
        self.entry.bind('<Return>', lambda e: self._validate())

        # ── Buttons ───────────────────────────────────
        btn_frame = tk.Frame(self.win, bg=bg)
        btn_frame.pack(fill='x', padx=12, pady=6)

        self.btn_validate = tk.Button(
            btn_frame, text="✅ Valider",
            font=("Segoe UI", 11), bg=btn_bg, fg=btn_fg,
            activebackground=tb_bg, relief='flat', padx=12, pady=6,
            command=self._validate,
        )
        self.btn_validate.pack(side='left', padx=4)

        self.btn_hint = tk.Button(
            btn_frame, text="💡 Indice",
            font=("Segoe UI", 11), bg=btn_bg, fg=btn_fg,
            activebackground=tb_bg, relief='flat', padx=12, pady=6,
            command=self._show_hint,
        )
        self.btn_hint.pack(side='left', padx=4)

        self.btn_next = tk.Button(
            btn_frame, text="➡ Suivante",
            font=("Segoe UI", 11), bg='#44475a', fg='#6272a4',
            activebackground=tb_bg, relief='flat', padx=12, pady=6,
            state='disabled',
            command=self._next_question,
        )
        self.btn_next.pack(side='right', padx=4)

        # ── Result label ─────────────────────────────
        self.lbl_result = tk.Label(
            self.win, text="",
            font=("Segoe UI", 12, "bold"),
            bg=bg, fg=fg,
        )
        self.lbl_result.pack(pady=4)

        # ── Hint label ───────────────────────────────
        self.lbl_hint = tk.Label(
            self.win, text="",
            font=("Arial", 12), bg=bg, fg='#ffb86c',
        )
        self.lbl_hint.pack(pady=2)

        # ── Bottom bar ───────────────────────────────
        bottom = tk.Frame(self.win, bg=tb_bg)
        bottom.pack(fill='x', side='bottom')

        tk.Button(bottom, text="🔄 Rejouer",
                  font=("Segoe UI", 10), bg=btn_bg, fg=btn_fg,
                  activebackground=bg, relief='flat', padx=10, pady=4,
                  command=self.restart).pack(side='left', padx=10, pady=6)

        tk.Button(bottom, text="❌ Fermer",
                  font=("Segoe UI", 10), bg=btn_bg, fg=btn_fg,
                  activebackground=bg, relief='flat', padx=10, pady=4,
                  command=self.win.destroy).pack(side='right', padx=10, pady=6)

    # ── Game logic ────────────────────────────────────────────────────────────

    def start_game(self) -> None:
        self.current = 0
        self.score = 0
        self.wrong_attempts = 0
        self.hint_used = False
        self._game_over = False
        self._show_question()

    def restart(self) -> None:
        self.start_game()

    def _show_question(self) -> None:
        if self.current >= len(RIDDLES):
            self._show_end_screen()
            return
        riddle = RIDDLES[self.current]
        self.wrong_attempts = 0
        self.hint_used = False

        self.lbl_question_num.configure(text=f"Énigme {self.current + 1}/15")
        self.lbl_question.configure(text=riddle['question'])
        self.lbl_result.configure(text="", fg=self.theme.get('fg', '#f8f8f2'))
        self.lbl_hint.configure(text="")
        self.entry.delete(0, 'end')
        self.entry.configure(state='normal')
        self.entry.focus_set()
        self.progress_bar['value'] = self.current
        self.btn_next.configure(state='disabled', fg='#6272a4', bg='#44475a')
        self.btn_validate.configure(state='normal')
        self.btn_hint.configure(state='normal')
        self._update_score_label()

    def _validate(self) -> None:
        if self._game_over:
            return
        raw = self.entry.get()
        if not raw.strip():
            return
        riddle = RIDDLES[self.current]
        if _normalize(raw) == _normalize(riddle['answer']):
            self.score += 1
            self.lbl_result.configure(text="✅ Correct !", fg='#50fa7b')
            self._update_score_label()
            self._unlock_next()
        else:
            self.wrong_attempts += 1
            if self.wrong_attempts >= 3:
                self.lbl_result.configure(
                    text=f"❌ Réponse : « {riddle['answer']} »", fg='#ff5555'
                )
                self._unlock_next()
            else:
                remaining = 3 - self.wrong_attempts
                self.lbl_result.configure(
                    text=f"❌ Essayez encore ({remaining} essai{'s' if remaining > 1 else ''} restant{'s' if remaining > 1 else ''})",
                    fg='#ff5555',
                )

    def _show_hint(self) -> None:
        riddle = RIDDLES[self.current]
        answer = riddle['answer']
        hint_text = ' '.join('_' for _ in answer) + f"  ({len(answer)} lettres)\n💡 {riddle['hint']}"
        self.lbl_hint.configure(text=hint_text)
        self.hint_used = True

    def _unlock_next(self) -> None:
        self.btn_validate.configure(state='disabled')
        self.btn_hint.configure(state='disabled')
        self.entry.configure(state='disabled')
        btn_bg = self.theme.get('btn_bg', '#6272a4')
        btn_fg = self.theme.get('btn_fg', '#f8f8f2')
        self.btn_next.configure(state='normal', bg=btn_bg, fg=btn_fg)

    def _next_question(self) -> None:
        self.current += 1
        self._show_question()

    def _update_score_label(self) -> None:
        self.lbl_score.configure(text=f"Score : {self.score}/15")

    # ── End screen ────────────────────────────────────────────────────────────

    def _show_end_screen(self) -> None:
        self._game_over = True
        self.progress_bar['value'] = 15
        for w in self.win.winfo_children():
            if isinstance(w, tk.Frame) and w not in []:
                pass
        self.lbl_question.configure(
            text=f"🎉 Partie terminée !\n\nVotre score final : {self.score}/15",
            font=("Arial", 16, "bold"),
        )
        self.entry.configure(state='disabled')
        self.btn_validate.configure(state='disabled')
        self.btn_hint.configure(state='disabled')
        self.btn_next.configure(state='disabled')
        self.lbl_question_num.configure(text="Terminé !")
        pct = (self.score / 15) * 100
        if pct >= 80:
            msg = "🏆 Excellent ! Tu es un génie des énigmes !"
            color = '#50fa7b'
        elif pct >= 50:
            msg = "👍 Bien joué ! Continue comme ça !"
            color = '#ffb86c'
        else:
            msg = "📚 Continue à pratiquer, tu vas progresser !"
            color = '#ff79c6'
        self.lbl_result.configure(text=msg, fg=color)

    def update_score(self, value) -> None:
        pass
