# coding: utf-8
from __future__ import unicode_literals
import peewee as pw

database = pw.SqliteDatabase('database.db')


class Report(pw.Model):
    created = pw.DateTimeField()
    is_missed = pw.BooleanField(default=False)
    report = pw.TextField(null=True)

    class Meta:
        database = database
        db_table = 'reports'
        order_by = ('-created',)

    @classmethod
    def create_table_if_not_exist(cls):
        try:
            cls.create_table()
        except pw.OperationalError:
            pass

    @classmethod
    def get_last_report_time(cls, date_format):
        last_report = cls.select().first()
        return last_report and last_report.created.strftime(date_format) or '--'