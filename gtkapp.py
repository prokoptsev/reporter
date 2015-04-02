#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals
import locale
from datetime import datetime

import gtk
import glib

from model import Report, database


class Application(object):
    pagging = 10
    date_format = "%d %b %H:%M"

    def __init__(self, title, width=400, height=300):
        locale.setlocale(locale.LC_ALL, '')
        self.datetime_create = datetime.now()
        Report.create_table_if_not_exist()

        self.window = gtk.Window()
        self.window.connect("destroy", self.quit)
        self.window.set_size_request(width, height)
        self.window.set_border_width(self.pagging)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_title(title)
        self.create_widgets()
        self.window.show_all()

    def skip_report(self):
        with database.transaction():
            Report.create(
                created=self.datetime_create,
                is_missed=True
            )
        self.quit(self.window)

    def save_report(self, widget):
        textbuffer = self.report.get_buffer()
        report_data = textbuffer.get_text(*textbuffer.get_bounds())
        with database.transaction():
            Report.create(
                report=report_data,
                created=self.datetime_create
            )
        self.quit(self.window)

    def create_widgets(self):
        vbox = gtk.VBox()
        self.window.add(vbox)

        label_created = gtk.Label("Время создания отчета: {}".format(
            self.datetime_create.strftime(self.date_format)))
        vbox.pack_start(label_created, False)

        label_last_report = gtk.Label("Последний отчет создан: {}".format(
            Report.get_last_report_time(self.date_format)))
        vbox.pack_start(label_last_report, False, padding=self.pagging)

        self.report = gtk.TextView()
        self.report.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        vbox.pack_start(self.report)

        save_btn = gtk.Button("Сохранить")
        save_btn.connect('clicked', self.save_report)
        vbox.pack_start(save_btn, False, padding=self.pagging)

    def quit(self, widget):
        gtk.main_quit()

    def run(self):
        glib.timeout_add(1000 * 60 * 15, self.skip_report)
        gtk.main()


if __name__ == '__main__':
    application = Application("Добавить отчет о проделанной работе")
    application.run()
