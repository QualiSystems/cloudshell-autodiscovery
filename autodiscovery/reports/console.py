from textwrap import wrap

from terminaltables import AsciiTable

from autodiscovery.reports.base import AbstractReport


class AbstractConsoleReport(AbstractReport):
    FILE_EXTENSION = "txt"

    @property
    def _header_column_width_map(self):
        return {}

    def _format_column_width(self, header, attr_value):
        if header in self._header_column_width_map:
            return "\n".join(
                wrap(str(attr_value), self._header_column_width_map[header])
            )

        return attr_value

    def generate(self):
        """Print report for all discovered devices to the console."""
        empty_row = ("",) * len(self._header)
        table_data = [self._header]

        for entry in self._entries:
            entry_row = [
                self._format_column_width(
                    header=header, attr_value=getattr(entry, attr)
                )
                for header, attr in self._header_entry_map.items()
            ]

            table_data.extend(
                [entry_row, empty_row]
            )  # add an empty row between records

        table = AsciiTable(table_data)

        with open(self.file_name, "w") as report_file:
            report_file.write(table.table)
