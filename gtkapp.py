#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals
import locale
from datetime import datetime

import gtk
import glib

from model import Report, database


class Application(object):
    padding = 10
    date_format = "%d %b %H:%M"

    def __init__(self, title, width=400, height=300):
        locale.setlocale(locale.LC_ALL, '')
        self.datetime_create = datetime.now()
        Report.create_table_if_not_exist()

        self.window = gtk.Window()
        self.window.connect("destroy", self.quit)
        self.window.set_size_request(width, height)
        self.window.set_border_width(self.padding)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_title(title)
        self.create_widgets()
        self.create_accel()
        self.window.show_all()

    def create_accel(self):
        # Создаём группу ускорителей
        accelgroup = gtk.AccelGroup()

        # Add the accelerator group to the toplevel window
        self.window.add_accel_group(accelgroup)

        # Создаём действие для автосохранения и выхода из программы
        auto_save = gtk.Action("Auto-Save", None, None, gtk.STOCK_SAVE)

        # Connect a callback to the action
        auto_save.connect('activate', self.save_report)

        # Создаём группу действий под названием SimpleAction
        actiongroup = gtk.ActionGroup('SimpleAction')

        # Добавляем в группу действие с ускорителем
        # None означает что мы используем stock item accelerator
        actiongroup.add_action_with_accel(auto_save, None)

        # Have the action use accelgroup
        auto_save.set_accel_group(accelgroup)

        # Подключаем ускоритель к действию
        auto_save.connect_accelerator()
        # Подключаем действие к доверенному виджету
        auto_save.connect_proxy(self.save_btn)

    def skip_report(self):
        with database.transaction():
            Report.create(
                created=self.datetime_create,
                is_missed=True
            )
        self.quit(self.window)

    def save_report(self, widget):
        text_buffer = self.report.get_buffer()
        report_data = text_buffer.get_text(*text_buffer.get_bounds())
        with database.transaction():
            Report.create(
                report=report_data,
                created=self.datetime_create
            )
        self.quit(self.window)

    def create_widgets(self):
        vbox = gtk.VBox()
        self.window.add(vbox)

        last_frame = gtk.Frame()
        label_frame = gtk.Label("<b>Прошлый отчет</b>")
        label_frame.set_use_markup(True)
        last_frame.set_label_widget(label_frame)
        last_vbox = gtk.VBox()
        last_frame.add(last_vbox)
        vbox.pack_start(last_frame, False)

        label_last_report_time = gtk.Label("<b>Cоздан:</b> {}".format(
            Report.get_last_report_time(self.date_format)))
        label_last_report_time.set_alignment(0, .5)
        label_last_report_time.set_use_markup(True)
        last_vbox.pack_start(label_last_report_time, False)

        label_last_report = gtk.Label("<b>Содержание:</b>")
        label_last_report.set_alignment(0, .5)
        label_last_report.set_use_markup(True)
        last_vbox.pack_start(label_last_report, False)

        last_report = gtk.Label(Report.get_last_report())
        last_report.set_alignment(0, .5)
        last_vbox.pack_start(last_report, False)

        label_created = gtk.Label("Текущий отчет: {}".format(
            self.datetime_create.strftime(self.date_format)))
        label_created.set_alignment(0, .5)
        vbox.pack_start(label_created, False, padding=self.padding)

        self.report = gtk.TextView()
        self.report.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        # self.report.connect('key-release-event', self.report_event)
        vbox.pack_start(self.report)

        self.save_btn = gtk.Button("Сохранить")
        self.save_btn.connect('clicked', self.save_report)
        vbox.pack_start(self.save_btn, False, padding=self.padding)

    def quit(self, widget):
        gtk.main_quit()

    def run(self):
        glib.timeout_add(1000 * 60 * 15, self.skip_report)
        gtk.main()


if __name__ == '__main__':
    application = Application("Добавить отчет о проделанной работе")
    application.run()
