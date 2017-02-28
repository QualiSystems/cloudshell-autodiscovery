from textwrap import wrap

import click
from terminaltables import AsciiTable


class Entry(object):
    SUCCESS_STATUS = "Success"
    FAILED_STATUS = "Failed"

    def __init__(self, ip):
        self.ip = ip
        self.vendor = ""
        self.sys_object_id = ""
        self.description = ""
        self.status = self.SUCCESS_STATUS
        self.comment = ""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.status = self.FAILED_STATUS
            # todo: set only ReportableException exceptions as messages
            self.comment = exc_val


class AbstractReport(object):
    def __init__(self):
        self._entries = []

    def add_entry(self, ip):
        entry = Entry(ip)
        self._entries.append(entry)

        return entry

    def get_current_entry(self):
        if self._entries:
            return self._entries[-1]

    def generate(self):
        raise NotImplementedError("Class {} must implement method 'generate'".format(type(self)))


class ConsoleReport(AbstractReport):
    DESCRIPTION_COLUMN_WIDTH = 60
    COMMENT_COLUMN_WIDTH = 40

    def generate(self):
        table_data = [("IP", "VENDOR", "sysObjectID", "DESCRIPTION", "ADDED TO CLOUDSHELL", "COMMENT")]

        for entry in self._entries:
            description = '\n'.join(wrap(str(entry.description), self.DESCRIPTION_COLUMN_WIDTH))
            comment = '\n'.join(wrap(str(entry.comment), self.COMMENT_COLUMN_WIDTH))
            table_data.extend([(entry.ip, entry.vendor, entry.sys_object_id, description, entry.status, comment),
                               ("", "", "", "", "", "")])  # add an empty row between records

        table = AsciiTable(table_data)
        click.echo(table.table)
