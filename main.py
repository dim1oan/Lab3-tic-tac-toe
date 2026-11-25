"""Графическое приложение «Крестики-нолики» на Tkinter (этап 1: окно)."""

import tkinter as tk


class TicTacToeApp:
    """Главное окно приложения «Крестики-нолики»."""

    def __init__(self, root: tk.Tk) -> None:
        """Инициализирует базовые параметры окна."""
        self.root = root
        self.root.title("Крестики-нолики — Лабораторная работа №3")
        self.root.geometry("460x560")
        self.root.configure(bg="#F8FAFC")

        # Заголовок в верхней части окна
        self.title_label = tk.Label(
            self.root,
            text="Крестики-нолики",
            font=("Segoe UI", 18, "bold"),
            bg="#F8FAFC",
            fg="#0F172A",
        )
        self.title_label.pack(pady=24)


def main() -> None:
    """Точка входа в приложение."""
    root = tk.Tk()
    TicTacToeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
