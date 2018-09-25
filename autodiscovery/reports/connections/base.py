from autodiscovery.exceptions import ReportableException


class AbstractReport(object):
    HEADER = ("Source Port Full Name", "Target Port Full Name", "Domain", "Connection Status", "Comment")

    def __init__(self):
        self._entries = []

    def add_entry(self, source_port, target_port, domain):
        """Add new Entry for the device with given IP

        :param str source_port: full address of the source port
        :param str target_port: full address of the source port
        :param str domain: domain on the CloudShell
        :rtype: Entry
        """
        entry = Entry(source_port=source_port, target_port=target_port, domain=domain)
        self._entries.append(entry)

        return entry

    def edit_entry(self, entry):
        """Add new Entry for the device with given IP

        :param Entry entry:
        :rtype: Entry
        """
        self._entries.append(entry)
        return entry

    def get_current_entry(self):
        """Get last added entry to the report"""
        if self._entries:
            return self._entries[-1]

    def generate(self):
        """Generate report for all processed connections (entries)

        :return:
        """
        raise NotImplementedError("Class {} must implement method 'generate'".format(type(self)))

    def parse_entries_from_file(self, report_file):
        """Parse all connections (entries) from a given file

        :param str report_file: file path to the generated report
        :rtype: list[Entry]
        """
        raise NotImplementedError("Class {} must implement method 'parse_entries_from_file'".format(type(self)))


class Entry(object):
    SUCCESS_STATUS = "Success"
    FAILED_STATUS = "Failed"
    SKIPPED_STATUS = "Skipped"

    def __init__(self, source_port, target_port, domain, status=SUCCESS_STATUS, comment=""):
        """

        :param source_port:
        :param target_port:
        :param domain:
        :param status:
        :param comment:
        """
        self.source_port = source_port
        self.target_port = target_port
        self.domain = domain
        self.status = status
        self.comment = comment

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.status = self.FAILED_STATUS
            if isinstance(exc_val, ReportableException):
                self.comment = str(exc_val)
