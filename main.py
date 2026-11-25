"""Графическое приложение «Крестики-нолики» для двух игроков на Tkinter."""

import tkinter as tk
from tkinter import messagebox
from typing import Optional

# Палитра цветов интерфейса в светлой сдержанной теме
BG_COLOR = "#F8FAFC"
CARD_BG = "#FFFFFF"
HOVER_BG = "#F1F5F9"
BORDER_COLOR = "#CBD5E1"
TEXT_PRIMARY = "#0F172A"
TEXT_MUTED = "#475569"
BTN_BG = "#E2E8F0"
BTN_ACTIVE = "#CBD5E1"
COLOR_X = "#2563EB"
COLOR_O = "#DC2626"
WIN_BG = "#DCFCE7"
WIN_FG = "#15803D"

FONT_FAMILY = "Segoe UI"
MIN_WINDOW_WIDTH = 360
MIN_WINDOW_HEIGHT = 460


class GameError(Exception):
    """Базовое исключение для ошибок игровой логики."""


class InvalidCellError(GameError):
    """Вызывается при обращении к клетке вне границ поля 3x3."""


class CellOccupiedError(GameError):
    """Вызывается при попытке сделать ход в уже занятую клетку."""


class GameFinishedError(GameError):
    """Вызывается при попытке хода после окончания текущей партии."""


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
        """Инициализирует состояние игры и счетчик партий."""
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

    def make_move(self, row: int, col: int) -> str:
        """Выполняет ход текущего игрока в клетку (row, col).

        Возвращает поставленный символ ('X' или 'O').
        При нарушении правил выбрасывает одно из исключений GameError.
        """
        if not (0 <= row < 3 and 0 <= col < 3):
            raise InvalidCellError(
                f"Некорректные координаты клетки: ({row}, {col})."
            )

        if self.is_game_over:
            raise GameFinishedError(
                "Партия уже завершена! Нажмите «Новая игра», "
                "чтобы начать следующий раунд."
            )

        if self.board[row][col] != "":
            occupied_by = self.board[row][col]
            raise CellOccupiedError(
                f"Клетка ({row + 1}, {col + 1}) уже занята "
                f"символом «{occupied_by}»!"
            )

        placed_symbol = self.current_player
        self.board[row][col] = placed_symbol

        # Проверяем победу или ничью после сделанного хода
        win_combo = self.check_winner()
        if win_combo:
            self.winner = placed_symbol
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

        return placed_symbol

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
        """Инициализирует окно, меню, сетку и обработчики событий."""
        self.root = root
        self.root.title("Крестики-нолики — Лабораторная работа №3")
        self.root.geometry("460x560")
        self.root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.root.configure(bg=BG_COLOR)

        self.game = TicTacToeGame()
        self.buttons: list[list[tk.Button]] = []
        self.status_label: Optional[tk.Label] = None
        self.score_label: Optional[tk.Label] = None
        self.board_frame: Optional[tk.Frame] = None
        self.restart_btn: Optional[tk.Button] = None
        self._current_font_size: int = 32

        self._configure_root_grid()
        self._create_menu()
        self._create_widgets()
        self._bind_shortcuts()
        self._update_status_labels()

    def _configure_root_grid(self) -> None:
        """Настраивает масштабирование строк и столбцов главного окна."""
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)

    def _create_menu(self) -> None:
        """Создает верхнее меню приложения («Игра» и «Справка»)."""
        menu_bar = tk.Menu(self.root, tearoff=0)

        game_menu = tk.Menu(menu_bar, tearoff=0)
        game_menu.add_command(
            label="Новая игра",
            accelerator="Ctrl+N",
            command=self.new_game,
        )
        game_menu.add_separator()
        game_menu.add_command(
            label="Выход",
            accelerator="Ctrl+Q",
            command=self.exit_app,
        )
        menu_bar.add_cascade(label="Игра", menu=game_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(
            label="Об авторе",
            accelerator="F1",
            command=self.show_about,
        )
        menu_bar.add_cascade(label="Справка", menu=help_menu)

        self.root.config(menu=menu_bar)

    def _bind_shortcuts(self) -> None:
        """Привязывает горячие клавиши к основным действиям меню."""
        self.root.bind("<Control-n>", lambda _event: self.new_game())
        self.root.bind("<Control-N>", lambda _event: self.new_game())
        self.root.bind("<Control-q>", lambda _event: self.exit_app())
        self.root.bind("<Control-Q>", lambda _event: self.exit_app())
        self.root.bind("<F1>", lambda _event: self.show_about())

    def _create_widgets(self) -> None:
        """Создает информационную панель и масштабируемое поле 3x3."""
        header_frame = tk.Frame(self.root, bg=BG_COLOR)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 8))
        header_frame.columnconfigure(0, weight=1)
        header_frame.columnconfigure(1, weight=0)

        title_label = tk.Label(
            header_frame,
            text="Крестики-нолики",
            font=(FONT_FAMILY, 18, "bold"),
            bg=BG_COLOR,
            fg=TEXT_PRIMARY,
        )
        title_label.grid(row=0, column=0, sticky="w")

        self.restart_btn = tk.Button(
            header_frame,
            text="Новая игра",
            font=(FONT_FAMILY, 10, "bold"),
            bg=BTN_BG,
            fg=TEXT_PRIMARY,
            activebackground=BTN_ACTIVE,
            activeforeground=TEXT_PRIMARY,
            relief="flat",
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.new_game,
        )
        self.restart_btn.grid(row=0, column=1, sticky="e")
        self.restart_btn.bind(
            "<Enter>",
            lambda _e: self._set_widget_bg(self.restart_btn, BTN_ACTIVE),
        )
        self.restart_btn.bind(
            "<Leave>",
            lambda _e: self._set_widget_bg(self.restart_btn, BTN_BG),
        )

        self.status_label = tk.Label(
            header_frame,
            text="",
            font=(FONT_FAMILY, 12, "bold"),
            bg=BG_COLOR,
            fg=COLOR_X,
        )
        self.status_label.grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(8, 2)
        )

        self.score_label = tk.Label(
            header_frame,
            text="",
            font=(FONT_FAMILY, 10),
            bg=BG_COLOR,
            fg=TEXT_MUTED,
        )
        self.score_label.grid(row=2, column=0, columnspan=2, sticky="w")

        # Контейнер игрового поля с равномерным масштабированием 3x3
        self.board_frame = tk.Frame(
            self.root,
            bg=BORDER_COLOR,
            padx=2,
            pady=2,
        )
        self.board_frame.grid(
            row=1, column=0, sticky="nsew", padx=20, pady=(8, 20)
        )
        self.board_frame.bind("<Configure>", self._on_board_resize)

        for index in range(3):
            self.board_frame.rowconfigure(
                index, weight=1, uniform="board_row"
            )
            self.board_frame.columnconfigure(
                index, weight=1, uniform="board_col"
            )

        # Создаем 9 кнопок-клеток игрового поля
        for row in range(3):
            button_row: list[tk.Button] = []
            for col in range(3):
                btn = tk.Button(
                    self.board_frame,
                    text="",
                    font=(FONT_FAMILY, self._current_font_size, "bold"),
                    bg=CARD_BG,
                    fg=TEXT_PRIMARY,
                    activebackground=BTN_BG,
                    relief="flat",
                    bd=0,
                    cursor="hand2",
                    command=lambda r=row, c=col: self.on_cell_click(r, c),
                )
                btn.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
                btn.bind(
                    "<Enter>",
                    lambda _e, r=row, c=col: self._on_cell_hover(r, c, True),
                )
                btn.bind(
                    "<Leave>",
                    lambda _e, r=row, c=col: self._on_cell_hover(r, c, False),
                )
                button_row.append(btn)
            self.buttons.append(button_row)

    def _set_widget_bg(
        self, widget: Optional[tk.Widget], color: str
    ) -> None:
        """Безопасно меняет цвет фона виджета при наведении курсора."""
        if widget is None:
            return
        try:
            widget.configure(bg=color)
        except tk.TclError:
            pass

    def _on_cell_hover(self, row: int, col: int, is_enter: bool) -> None:
        """Подсвечивает свободную клетку при наведении курсора."""
        try:
            if (row, col) in self.game.winning_cells:
                return
            if is_enter and not self.game.is_game_over:
                if self.game.board[row][col] == "":
                    self.buttons[row][col].configure(bg=HOVER_BG)
                    return
            self.buttons[row][col].configure(bg=CARD_BG)
        except (IndexError, tk.TclError):
            pass

    def _on_board_resize(self, event: tk.Event) -> None:
        """Динамически подстраивает размер шрифта X/O под размер окна."""
        try:
            cell_size = min(event.width, event.height) // 3
            new_size = max(16, min(68, int(cell_size * 0.36)))
            if new_size == self._current_font_size:
                return
            self._current_font_size = new_size
            for row in self.buttons:
                for btn in row:
                    btn.configure(font=(FONT_FAMILY, new_size, "bold"))
        except tk.TclError as exc:
            if self.root.winfo_exists():
                messagebox.showerror(
                    "Ошибка отрисовки",
                    f"Не удалось масштабировать игровое поле:\n{exc}",
                )

    def on_cell_click(self, row: int, col: int) -> None:
        """Обрабатывает клик по клетке с перехватом всех исключений."""
        try:
            symbol = self.game.make_move(row, col)
            color = COLOR_X if symbol == "X" else COLOR_O
            self.buttons[row][col].configure(
                text=symbol,
                fg=color,
                bg=CARD_BG,
            )

            if self.game.winner:
                for win_r, win_c in self.game.winning_cells:
                    self.buttons[win_r][win_c].configure(
                        bg=WIN_BG,
                        fg=WIN_FG,
                    )

            self._update_status_labels()
        except CellOccupiedError as exc:
            messagebox.showwarning("Клетка занята", str(exc))
        except GameFinishedError as exc:
            messagebox.showwarning("Игра окончена", str(exc))
        except InvalidCellError as exc:
            messagebox.showerror("Некорректный ход", str(exc))
        except tk.TclError as exc:
            messagebox.showerror(
                "Ошибка отрисовки",
                f"Произошел сбой при обновлении поля:\n{exc}",
            )
        except Exception as exc:
            messagebox.showerror(
                "Непредвиденная ошибка",
                f"Возникла ошибка при обработке хода:\n{exc}",
            )

    def new_game(self) -> None:
        """Перезапускает партию и сбрасывает отображение кнопок."""
        try:
            self.game.reset()
            for row in range(3):
                for col in range(3):
                    self.buttons[row][col].configure(
                        text="",
                        bg=CARD_BG,
                        fg=TEXT_PRIMARY,
                    )
            self._update_status_labels()
        except tk.TclError as exc:
            messagebox.showerror(
                "Ошибка отрисовки",
                f"Не удалось очистить игровое поле:\n{exc}",
            )
        except Exception as exc:
            messagebox.showerror(
                "Ошибка перезапуска",
                f"Не удалось начать новую игру:\n{exc}",
            )

    def show_about(self) -> None:
        """Отображает справочное окно с информацией об авторе."""
        try:
            messagebox.showinfo(
                "Об авторе",
                "Игра «Крестики-нолики» для двух игроков\n"
                "Лабораторная работа №3 "
                "«Приложения с графическим интерфейсом»\n\n"
                "Автор: Ткачук Дмитрий Владимирович\n"
                "Группа: ИДБ-25-15, 2 курс\n"
                "ВУЗ: МГТУ «СТАНКИН»\n"
                "GitHub: https://github.com/dim1oan",
            )
        except tk.TclError as exc:
            messagebox.showerror(
                "Ошибка интерфейса",
                f"Не удалось открыть окно «Об авторе»:\n{exc}",
            )

    def exit_app(self) -> None:
        """Завершает работу графического приложения."""
        try:
            self.root.destroy()
        except tk.TclError as exc:
            messagebox.showerror(
                "Ошибка выхода",
                f"Не удалось закрыть окно:\n{exc}",
            )

    def _update_status_labels(self) -> None:
        """Обновляет метку текущего хода и строку общего счета."""
        if self.status_label is None or self.score_label is None:
            return

        try:
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
        except tk.TclError as exc:
            messagebox.showerror(
                "Ошибка отрисовки",
                f"Не удалось обновить статус игры:\n{exc}",
            )


def main() -> None:
    """Точка входа в программу с защитой от критических сбоев."""
    try:
        root = tk.Tk()
        TicTacToeApp(root)
        root.mainloop()
    except tk.TclError as exc:
        messagebox.showerror(
            "Ошибка графической подсистемы",
            f"Не удалось инициализировать окно Tkinter:\n{exc}",
        )
    except Exception as exc:
        messagebox.showerror(
            "Критическая ошибка",
            f"Непредвиденный сбой приложения:\n{exc}",
        )


if __name__ == "__main__":
    main()
