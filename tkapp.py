# coding: utf-8
from __future__ import unicode_literals
try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk
import locale
from datetime import datetime

from model import Report, database


class Application(object):
    pagging = 10
    date_format = "%d %b %H:%M"

    def __init__(self, title, width=300, height=200):
        Report.create_table_if_not_exist()
        self.datetime_create = datetime.now()
        locale.setlocale(locale.LC_ALL, '')

        # Инициализация окна с помощью родительского конструктора.
        self.window = tk.Frame(tk.Tk(), width=width, height=height)

        # Установить заголовок.
        self.window.master.title(title)

        # Мы будем использовать сетку в качестве менеджера компоновки.
        self.window.grid()

        # Текстовое поле ввода отчета о проделанной работе за период.
        self.report = tk.Text(self.window, height=7, width=40)

        # Кнопка сохранения отчета и выхода из редактора.
        self.save_report_button = tk.Button(self.window, text='Сохранить', command=self.save_report)

        # Расстоновка и отрисовка элементов.
        tk.Label(self.window, text="Текущее время").grid(row=0, column=0, sticky=tk.W)
        tk.Label(self.window, text=self.datetime_create.strftime(self.date_format)).grid(row=0, column=1, sticky=tk.W)

        tk.Label(self.window, text="Время последнего отчета").grid(row=1, column=0, sticky=tk.W)
        tk.Label(self.window, text=Report.get_last_report_time(self.date_format)).grid(row=1, column=1, sticky=tk.W)

        self.report.grid(row=2, column=0, columnspan=2)
        self.save_report_button.grid(row=3, column=0)

    def missed_report(self):
        """Сохранить отчет как пропущенный и выйти."""
        with database.transaction():
            Report.create(
                created=self.datetime_create,
                is_missed=True
            )
        self.quit()

    def save_report(self):
        """Сохранить отчет и выйти."""
        with database.transaction():
            Report.create(
                report=self.report.get('0.0', tk.END),
                created=self.datetime_create
            )
        self.quit()

    def _center_window(self, w=300, h=200):
        """
        Отцентрировать окно.
        """
        # get screen width and height
        ws = self.window.winfo_screenwidth()
        hs = self.window.winfo_screenheight()
        # calculate position x, y
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.window.master.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def quit(self, *args, **kwargs):
        self.window.quit()

    def run(self):
        self._center_window()
        # Установить таймер бездействия на 15 минут, после которого считать отчет пропущенным.
        self.window.after(1000 * 60 * 15, self.missed_report)
        self.window.mainloop()


if __name__ == '__main__':
    app = Application("Добавить отчет о проделанной работе")
    app.run()
