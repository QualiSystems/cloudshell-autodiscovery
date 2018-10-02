from textwrap import wrap

from terminaltables import AsciiTable

from autodiscovery.reports.base import AbstractReport


class AbstractConsoleReport(AbstractReport):
    DESCRIPTION_COLUMN_WIDTH = 60
    COMMENT_COLUMN_WIDTH = 40
    DEFAULT_REPORT_FILE = "connections-report.txt"

    def __init__(self, file_name=None):
        """

        :param str file_name:
        """
        super(AbstractConsoleReport, self).__init__()
        if file_name is None:
            file_name = self.DEFAULT_REPORT_FILE

        self.file_name = file_name

    @property
    def _header_column_width_map(self):
        """"""
        return {}

    def _format_column_width(self, header, attr_value):
        """

        :param header:
        :param attr_value:
        :return:
        """
        if header in self._header_column_width_map:
            return '\n'.join(wrap(str(attr_value), self._header_column_width_map[header]))

        return attr_value

    def generate(self):
        """Print report for all discovered devices to the console"""
        empty_row = ("",) * len(self._header)
        table_data = [self._header]

        for entry in self._entries:
            entry_row = [self._format_column_width(header=header, attr_value=getattr(entry, attr))
                         for header, attr in self._header_entry_map.iteritems()]

            table_data.extend([entry_row, empty_row])  # add an empty row between records

        table = AsciiTable(table_data)

        with open(self.file_name, "w") as report_file:
            report_file.write(table.table)
