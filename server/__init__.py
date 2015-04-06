# coding: utf-8
from __future__ import unicode_literals
from collections import OrderedDict
from datetime import datetime, time, date, timedelta
from flask import Flask, request, render_template, abort

from model import Report

app = Flask(__name__)
app.create_jinja_environment()

_format = "%d.%m.%Y"
filters = OrderedDict((
    ('today', {
        "title": "Сегодня",
        "from": datetime.combine(date.today(), time()),
        "to": datetime.now()
    }),
    ('yesterday', {
        "title": "Последние 2 дня",
        "from": datetime.combine(date.today(), time()) - timedelta(days=1),
        "to": datetime.combine(date.today(), time())
    }),
    ('week', {
        "title": "За неделю",
        "from": datetime.combine(date.today(), time()) - timedelta(days=7),
        "to": datetime.now()
    })
))


def _check(_date):
    if not isinstance(_date, datetime):
        if isinstance(_date, basestring):
            dates = _date.split('.')
            if all(i.isdigit() for i in dates):
                if len(dates) == 1:
                    _date = '{}.{}.{}'.format(_date, date.today().month, date.today().year)
                elif len(dates) == 2:
                    _date = '{}.{}'.format(_date, date.today().year)
        try:
            _date = datetime.strptime(_date, _format)
        except (TypeError, ValueError):
            raise abort(400, description='Incorrect date: {}'.format(_date))
    return _date


@app.template_filter('dtformat')
def dtformat_filter(value, format='%d.%m.%Y %H:%M '):
    return value.strftime(format)


@app.route('/')
def index():
    _from = request.args.get('from') or "today"
    _to = request.args.get('to') or datetime.now()
    default_filter = filters.get(_from)
    if default_filter:
        _from = default_filter['from']
        _to = default_filter['to']
    _from, _to = _check(_from), _check(_to)

    if _from > _to:
        return abort(400, description='Incorrect range date: from {} to {}'.format(_from, _to))
    reports = Report.select().where((Report.created > _from) & (Report.created < _to))
    return render_template(
        "index.html",
        reports=reports,
        filters=((title['title'], value) for value, title in filters.iteritems()),
        today=date.today().strftime(_format)
    )


if __name__ == '__main__':
    app.run(port=12321, debug=True)
