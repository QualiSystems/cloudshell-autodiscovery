from autodiscovery.exceptions import ReportableException


class AbstractReport(object):
    DEFAULT_REPORT_NAME = "report"
    FILE_EXTENSION = "*"

    def __init__(self, file_name=None):
        """

        :param str file_name:
        """
        self._entries = []

        if file_name is None:
            file_name = self.DEFAULT_REPORT_NAME

        file_extension = ".{}".format(self.FILE_EXTENSION)

        if not file_name.lower().endswith(file_extension):
            file_name += file_extension

        self.file_name = file_name

    @property
    def entries(self):
        return self._entries

    def add_entry(self, *args, **kwargs):
        """Add new Entry to the Report

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
        raise NotImplementedError("Class {} must implement property '_header_entry_map'".format(type(self)))

    @property
    def entry_class(self):
        raise NotImplementedError("Class {} must implement property 'entry_class'".format(type(self)))

    def generate(self):
        """Generate Report with all entries

        :return:
        """
        raise NotImplementedError("Class {} must implement method 'generate'".format(type(self)))


class AbstractParsableReport(AbstractReport):
    def parse_entries_from_file(self, report_file):
        """Parse all discovered devices (entries) from a given file

        :param str report_file: file path to the generated report
        :rtype: list[Entry]
        """
        raise NotImplementedError("Class {} must implement method 'parse_entries_from_file'".format(type(self)))


class AbstractEntry(object):
    SUCCESS_STATUS = "Success"
    FAILED_STATUS = "Failed"

    def __init__(self, status=SUCCESS_STATUS, comment="", *args, **kwargs):
        """

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
