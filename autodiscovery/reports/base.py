from collections import Counter

from autodiscovery.exceptions import ReportableException


class AbstractReport(object):
    DEFAULT_REPORT_NAME = "report"
    FILE_EXTENSION = "*"

    def __init__(self, file_name=None):
        """Init command.

        :param str file_name:
        """
        self._entries = []

        if file_name is None:
            file_name = self.DEFAULT_REPORT_NAME

        file_extension = f".{self.FILE_EXTENSION}"

        if not file_name.lower().endswith(file_extension):
            file_name += file_extension

        self.file_name = file_name

    @property
    def entries(self):
        return self._entries

    def get_failed_entries_count(self):
        """

        :return:
        """
        counter = Counter(getattr(entry, "status") for entry in self._entries)
        return counter[self.entry_class.FAILED_STATUS]

    def add_entry(self, *args, **kwargs):
        """Add new Entry to the Report.

        :rtype: Entry
        """
        entry = self.entry_class(*args, **kwargs)
        self._entries.append(entry)
        return entry

    @property
    def _header(self):
        return self._header_entry_map.keys()

    @property
    def _header_entry_map(self):
        raise NotImplementedError(
            f"Class {type(self)} must implement property '_header_entry_map'"
        )

    @property
    def entry_class(self):
        raise NotImplementedError(
            f"Class {type(self)} must implement property 'entry_class'"
        )

    def generate(self):
        """Generate Report with all entries.

        :return:
        """
        raise NotImplementedError("Class {type(self)} must implement method 'generate'")


class AbstractParsableReport(AbstractReport):
    def parse_entries_from_file(self, report_file):
        """Parse all discovered devices (entries) from a given file.

        :param str report_file: file path to the generated report
        :rtype: list[Entry]
        """
        raise NotImplementedError(
            f"Class {type(self)} must implement method 'parse_entries_from_file'"
        )


class AbstractEntry(object):
    SUCCESS_STATUS = "Success"
    FAILED_STATUS = "Failed"

    def __init__(self, status=SUCCESS_STATUS, comment="", *args, **kwargs):
        """Init command.

        :param status:
        :param comment:
        :param args:
        :param kwargs:
        """
        self.status = status
        self.comment = comment

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.status = self.FAILED_STATUS
            if isinstance(exc_val, ReportableException):
                self.comment = str(exc_val)
