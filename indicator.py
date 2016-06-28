#!/usr/bin/env python
import sys
import signal

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gtk
from gi.repository import AppIndicator3 as appindicator

from reporter import ReporterWindow


class Indicator(object):
    def __init__(self):
        indicator = appindicator.Indicator.new(
            "IndicatorWorkLogger", Gtk.STOCK_EDIT,
            appindicator.IndicatorCategory.SYSTEM_SERVICES)
        indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        indicator.set_menu(self.build_menu())

    def build_menu(self):
        menu = Gtk.Menu()
        make_report = Gtk.MenuItem('Создать отчет')
        make_report.connect('activate', self.open_reporter)

        item_quit = Gtk.MenuItem('Выход')
        item_quit.connect('activate', self.quit)

        menu.append(make_report)
        menu.append(item_quit)
        menu.show_all()
        return menu

    def quit(self, *ignor):
        Gtk.main_quit()

    def open_reporter(self, *ignor):
        # ReporterWindow()
        pass

    @classmethod
    def run(cls):
        sys.stdout.write("Start indicator")
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        cls()
        Gtk.main()


if __name__ == '__main__':
    Indicator.run()