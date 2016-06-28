#!/usr/bin/env python
import locale
from datetime import datetime

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gtk, Gdk

from model import Report, database


class ReporterWindow(Gtk.Window):
    padding = 10
    title = "Добавить отчет о проделаной работе."
    date_format = "%d %b %H:%M"

    def __init__(self, width=400, height=300, *args, **kwargs):
        super(ReporterWindow, self).__init__(*args, **kwargs)
        locale.setlocale(locale.LC_ALL, '')
        self.datetime_create = datetime.now()
        Report.create_table_if_not_exist()

        self.set_size_request(width, height)
        self.set_border_width(self.padding)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_title(self.title)

        self.create_widgets()
        self.connect('key-press-event', self.handle_keys)

        self.show_all()

    @property
    def ctrl_keys_bind(self):
        return {
            Gdk.KEY_q: self.quit,
            Gdk.KEY_s: self.save_report,
        }

    def handle_keys(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.quit()

        modifiers = Gtk.accelerator_get_default_mod_mask()
        ctrl = (event.state & modifiers) == Gdk.ModifierType.CONTROL_MASK
        if ctrl and event.keyval in self.ctrl_keys_bind.keys():
            self.ctrl_keys_bind[event.keyval]()

    def save_report(self, *ignore):
        text_buffer = self.report.get_buffer()
        report_data = text_buffer.get_text(
            text_buffer.get_start_iter(),
            text_buffer.get_end_iter(),
            False)
        with database.transaction():
            Report.create(
                report=report_data,
                created=self.datetime_create
            )
        self.quit(self)

    def create_widgets(self):
        vbox = Gtk.VBox()
        self.add(vbox)

        last_frame = Gtk.Frame()
        label_frame = Gtk.Label("<b>Прошлый отчет</b>")
        label_frame.set_use_markup(True)
        last_frame.set_label_widget(label_frame)
        last_vbox = Gtk.VBox()
        last_frame.add(last_vbox)
        vbox.pack_start(last_frame, False, False, 0)

        label_last_report_time = Gtk.Label("<b>Cоздан:</b> {}".format(
            Report.get_last_report_time(self.date_format)))
        label_last_report_time.set_alignment(0, .5)
        label_last_report_time.set_use_markup(True)
        last_vbox.pack_start(label_last_report_time, False, False, 0)

        label_last_report = Gtk.Label("<b>Содержание:</b>")
        label_last_report.set_alignment(0, .5)
        label_last_report.set_use_markup(True)
        last_vbox.pack_start(label_last_report, False, False, 0)

        last_report = Gtk.Label(Report.get_last_report())
        last_report.set_alignment(0, .5)
        last_vbox.pack_start(last_report, False, False, 0)

        label_created = Gtk.Label("Текущий отчет: {}".format(
            self.datetime_create.strftime(self.date_format)))
        label_created.set_alignment(0, .5)
        vbox.pack_start(label_created, False, False, self.padding)

        self.report = Gtk.TextView()
        self.report.set_wrap_mode(Gtk.WrapMode.WORD)
        # self.report.connect('key-release-event', self.report_event)
        vbox.pack_start(self.report, False, False, 0)

        self.save_btn = Gtk.Button("Сохранить")
        self.save_btn.connect('clicked', self.save_report)
        vbox.pack_start(self.save_btn, False, False, padding=self.padding)

    def quit(self, *ignore):
        Gtk.main_quit()

    @classmethod
    def run(cls):
        window = cls()
        window.connect("delete-event", window.quit)
        Gtk.main()


if __name__ == '__main__':
    ReporterWindow.run()
