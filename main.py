"""Графическое приложение «Крестики-нолики» для двух игроков на Tkinter."""

import tkinter as tk
from typing import Optional

# Палитра цветов интерфейса в светлой сдержанной теме
BG_COLOR = "#F8FAFC"
CARD_BG = "#FFFFFF"
BORDER_COLOR = "#CBD5E1"
TEXT_PRIMARY = "#0F172A"
TEXT_MUTED = "#475569"
COLOR_X = "#2563EB"
COLOR_O = "#DC2626"
WIN_BG = "#DCFCE7"
WIN_FG = "#15803D"


class TicTacToeGame:
    """Класс с игровой логикой для «Крестиков-ноликов» 3x3."""

    # Все возможные выигрышные комбинации (строки, столбцы, диагонали)
    WINNING_COMBINATIONS = (
        ((0, 0), (0, 1), (0, 2)),
        ((1, 0), (1, 1), (1, 2)),
        ((2, 0), (2, 1), (2, 2)),
        ((0, 0), (1, 0), (2, 0)),
        ((0, 1), (1, 1), (2, 1)),
        ((0, 2), (1, 2), (2, 2)),
        ((0, 0), (1, 1), (2, 2)),
        ((0, 2), (1, 1), (2, 0)),
    )

    def __init__(self) -> None:
        """Инициализирует состояние игры и счетчик побед."""
        self.scores = {"X": 0, "O": 0, "draws": 0}
        self.board: list[list[str]] = []
        self.current_player: str = "X"
        self.winner: Optional[str] = None
        self.winning_cells: list[tuple[int, int]] = []
        self.is_draw: bool = False
        self.is_game_over: bool = False
        self.reset()

    def reset(self) -> None:
        """Сбрасывает игровое поле для начала новой партии."""
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.winner = None
        self.winning_cells = []
        self.is_draw = False
        self.is_game_over = False

    def make_move(self, row: int, col: int) -> bool:
        """Выполняет ход текущего игрока в указанную клетку."""
        if self.is_game_over or self.board[row][col] != "":
            return False

        self.board[row][col] = self.current_player

        # Проверяем победу или ничью после сделанного хода
        win_combo = self.check_winner()
        if win_combo:
            self.winner = self.current_player
            self.winning_cells = list(win_combo)
            self.is_game_over = True
            self.scores[self.winner] += 1
        elif self.is_board_full():
            self.is_draw = True
            self.is_game_over = True
            self.scores["draws"] += 1
        else:
            # Передаем ход второму игроку
            self.current_player = "O" if self.current_player == "X" else "X"

        return True

    def check_winner(self) -> Optional[tuple[tuple[int, int], ...]]:
        """Проверяет наличие победителя и возвращает выигрышную линию."""
        for combo in self.WINNING_COMBINATIONS:
            r1, c1 = combo[0]
            r2, c2 = combo[1]
            r3, c3 = combo[2]
            first = self.board[r1][c1]
            if first and first == self.board[r2][c2] == self.board[r3][c3]:
                return combo
        return None

    def is_board_full(self) -> bool:
        """Возвращает True, если все клетки поля заполнены."""
        return all(cell != "" for row in self.board for cell in row)


class TicTacToeApp:
    """Главное окно и графический интерфейс игры «Крестики-нолики»."""

    def __init__(self, root: tk.Tk) -> None:
        """Инициализирует окно, игровую модель и виджеты."""
        self.root = root
        self.root.title("Крестики-нолики — Лабораторная работа №3")
        self.root.geometry("460x560")
        self.root.configure(bg=BG_COLOR)

        self.game = TicTacToeGame()
        self.buttons: list[list[tk.Button]] = []
        self.status_label: Optional[tk.Label] = None
        self.score_label: Optional[tk.Label] = None
        self.board_frame: Optional[tk.Frame] = None

        self._create_widgets()
        self._update_status_labels()

    def _create_widgets(self) -> None:
        """Создает информационную панель и сетку игрового поля 3x3."""
        header_frame = tk.Frame(self.root, bg=BG_COLOR)
        header_frame.pack(fill="x", padx=20, pady=(16, 8))

        title_label = tk.Label(
            header_frame,
            text="Крестики-нолики",
            font=("Segoe UI", 18, "bold"),
            bg=BG_COLOR,
            fg=TEXT_PRIMARY,
        )
        title_label.pack(anchor="w")

        self.status_label = tk.Label(
            header_frame,
            text="",
            font=("Segoe UI", 12, "bold"),
            bg=BG_COLOR,
            fg=COLOR_X,
        )
        self.status_label.pack(anchor="w", pady=(6, 2))

        self.score_label = tk.Label(
            header_frame,
            text="",
            font=("Segoe UI", 10),
            bg=BG_COLOR,
            fg=TEXT_MUTED,
        )
        self.score_label.pack(anchor="w")

        # Контейнер игрового поля
        self.board_frame = tk.Frame(
            self.root,
            bg=BORDER_COLOR,
            padx=2,
            pady=2,
        )
        self.board_frame.pack(fill="both", expand=True, padx=20, pady=(8, 20))

        # Создаем 9 кнопок-клеток 3x3
        for row in range(3):
            button_row: list[tk.Button] = []
            for col in range(3):
                btn = tk.Button(
                    self.board_frame,
                    text="",
                    font=("Segoe UI", 32, "bold"),
                    bg=CARD_BG,
                    fg=TEXT_PRIMARY,
                    activebackground="#E2E8F0",
                    relief="flat",
                    bd=0,
                    cursor="hand2",
                    command=lambda r=row, c=col: self.on_cell_click(r, c),
                )
                btn.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
                button_row.append(btn)
            self.buttons.append(button_row)

    def on_cell_click(self, row: int, col: int) -> None:
        """Обрабатывает нажатие на клетку игрового поля."""
        moved = self.game.make_move(row, col)
        if not moved:
            return

        symbol = self.game.board[row][col]
        color = COLOR_X if symbol == "X" else COLOR_O
        self.buttons[row][col].configure(text=symbol, fg=color)

        if self.game.winner:
            for r, c in self.game.winning_cells:
                self.buttons[r][c].configure(bg=WIN_BG, fg=WIN_FG)

        self._update_status_labels()

    def _update_status_labels(self) -> None:
        """Обновляет текст статуса хода и счетчика партий."""
        if self.status_label is None or self.score_label is None:
            return

        if self.game.winner:
            self.status_label.configure(
                text=f"Победил игрок {self.game.winner}!",
                fg=WIN_FG,
            )
        elif self.game.is_draw:
            self.status_label.configure(
                text="Ничья! Свободных клеток не осталось.",
                fg=TEXT_PRIMARY,
            )
        else:
            player_color = (
                COLOR_X if self.game.current_player == "X" else COLOR_O
            )
            self.status_label.configure(
                text=f"Сейчас ходит: игрок {self.game.current_player}",
                fg=player_color,
            )

        scores = self.game.scores
        self.score_label.configure(
            text=(
                f"Счет — X: {scores['X']}  |  "
                f"O: {scores['O']}  |  Ничьи: {scores['draws']}"
            )
        )


def main() -> None:
    """Точка входа в приложение."""
    root = tk.Tk()
    TicTacToeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
