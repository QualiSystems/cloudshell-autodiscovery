import csv

from autodiscovery.reports.base import AbstractParsableReport


class AbstractCSVReport(AbstractParsableReport):
    FILE_EXTENSION = "csv"

    def generate(self):
        """Save report for all discovered devices into the CSV file"""
        with open(self.file_name, "w") as report_file:
            writer = csv.DictWriter(report_file, fieldnames=self._header)
            writer.writeheader()

            for entry in self._entries:
                entry_row = {header: getattr(entry, entry_attr) for header, entry_attr
                             in self._header_entry_map.iteritems()}

                writer.writerow(entry_row)

    def parse_entries_from_file(self, report_file):
        """

        :param str report_file: path to the report file
        :rtype: list[Entry]
        """
        with open(self.file_name, "r") as report_file:
            reader = csv.DictReader(report_file, fieldnames=self._header)

            for row in list(reader)[1:]:  # first row is a header
                entry_attrs = {}
                for header, entry_attr in self._header_entry_map.iteritems():
                    entry_attrs[entry_attr] = row[header]

                entry = self.entry_class(**entry_attrs)
                self._entries.append(entry)
