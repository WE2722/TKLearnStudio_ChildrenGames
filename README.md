# TkLearn Studio v1.3 — Children’s Games Edition

A desktop pedagogical sandbox for children to learn Python and play 10 classic games, all in a beautiful Tkinter app.
## Features

- **Live code editor** with syntax highlighting, line numbers, and autocomplete
- **Instant preview** — press F5 to render your Tkinter widgets in real time
- **10 fully playable games** (Maze, Puzzle, Memory, Riddles, Hangman, Tic Tac Toe, Snake, Color Quiz, Math Quiz, Word Scramble)
- **Games lobby** and individual launchers
- **Progress tracking** for lessons
- **Dark / Light theme** toggle
- **Console** with color-coded messages
## Requirements

- Python 3.10+
- Tkinter (included with Python)
- pygments (for syntax highlighting)

## Installation

1. Download or clone this repository.
    ```bash
    pip install -r requirements.txt
    ```

## Usage

From the app folder:

```bash
python main.py
```
## Build Windows Executable (EXE)

To create a standalone Windows executable:

1. Install PyInstaller:
    ```bash
    pip install pyinstaller
    ```
2. Open a terminal in the app folder:
    ```bash
    cd C:\Users\Wiam\Desktop\TkLearnStudio
    ```
3. Run PyInstaller:
    ```bash
    pyinstaller --noconfirm --onefile --windowed --add-data "lessons;lessons" --add-data "data;data" --add-data "src;src" main.py
    ```
    - The EXE will be created in `dist/main.exe`.
    - You can rename and move it to `C:\Users\Wiam\Desktop\my_apps\TkLearnStudio.exe`.

**Note:** If you want a custom icon, add `--icon=icon.ico` (provide your own `.ico` file).
## Keyboard Shortcuts

| Shortcut | Action           |
|----------|------------------|
| F5       | Run code         |
| Ctrl+N   | New file         |
| Ctrl+O   | Open file        |
| Ctrl+S   | Save file        |
| Ctrl+Q   | Quit             |

## Project Structure

```
TkLearnStudio/
├── main.py              # Entry point
├── requirements.txt
├── LICENSE
├── README.md
├── data/                # Progress data
├── lessons/             # Lesson files
└── src/
    ├── games/           # 10 games + manager
    ├── ui/              # UI components
    ├── core/            # Business logic
    └── utils/           # Constants and helpers
```

## License

MIT License — see [LICENSE](LICENSE)

# TkLearn Studio v1.3 — Children’s Games Edition

A desktop pedagogical sandbox for children to learn Python and play 10 classic games, all in a beautiful Tkinter app.

## Features

- **Live code editor** with syntax highlighting, line numbers, and autocomplete
- **Instant preview** — press F5 to render your Tkinter widgets in real time
- **10 fully playable games** (Maze, Puzzle, Memory, Riddles, Hangman, Tic Tac Toe, Snake, Color Quiz, Math Quiz, Word Scramble)
- **Games lobby** and individual launchers
- **Progress tracking** for lessons
- **Dark / Light theme** toggle
- **Console** with color-coded messages

## Requirements

- Python 3.10+
- Tkinter (included with Python)
- pygments (for syntax highlighting)

## Installation

1. Download or clone this repository.
2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

From the app folder:

```bash
python main.py
```

## Build Windows Executable (EXE)

To create a standalone Windows executable:

1. Install PyInstaller:
    ```bash
    pip install pyinstaller
    ```
2. Open a terminal in the app folder:
    ```bash
    cd C:\Users\Wiam\Desktop\TkLearnStudio
    ```
3. Run PyInstaller:
    ```bash
    pyinstaller --noconfirm --onefile --windowed --add-data "lessons;lessons" --add-data "data;data" --add-data "src;src" main.py
    ```
    - The EXE will be created in `dist/main.exe`.
    - You can rename and move it to `C:\Users\Wiam\Desktop\my_apps\TkLearnStudio.exe`.

**Note:** If you want a custom icon, add `--icon=icon.ico` (provide your own `.ico` file).

## Keyboard Shortcuts

| Shortcut | Action           |
|----------|------------------|
| F5       | Run code         |
| Ctrl+N   | New file         |
| Ctrl+O   | Open file        |
| Ctrl+S   | Save file        |
| Ctrl+Q   | Quit             |

## Project Structure

```
TkLearnStudio/
├── main.py              # Entry point
├── requirements.txt
├── LICENSE
├── README.md
├── data/                # Progress data
├── lessons/             # Lesson files
└── src/
     ├── games/           # 10 games + manager
     ├── ui/              # UI components
     ├── core/            # Business logic
     └── utils/           # Constants and helpers
```

## License

MIT License — see [LICENSE](LICENSE)
