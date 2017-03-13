from textwrap import wrap

from terminaltables import AsciiTable

from autodiscovery.exceptions import ReportableException


class Entry(object):
    SUCCESS_STATUS = "Success"
    FAILED_STATUS = "Failed"
    SKIPPED_STATUS = "Skipped"

    def __init__(self, ip, status):
        self.ip = ip
        self.status = status
        self.vendor = ""
        self.sys_object_id = ""
        self.snmp_community = ""
        self.user = ""
        self.password = ""
        self.enable_password = ""
        self.description = ""
        self.comment = ""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.status = self.FAILED_STATUS
            if isinstance(exc_val, ReportableException):
                self.comment = exc_val


class AbstractReport(object):
    def __init__(self):
        self._entries = []

    def add_entry(self, ip, offline):
        """Add new Entry for the device with given IP

        :param str ip: IP address of the discovered device
        :param bool offline:
        :rtype: Entry
        """
        if offline:
            status = Entry.SKIPPED_STATUS
        else:
            status = Entry.SUCCESS_STATUS

        entry = Entry(ip=ip, status=status)
        self._entries.append(entry)

        return entry

    def get_current_entry(self):
        """Get last added entry to the report"""
        if self._entries:
            return self._entries[-1]

    def generate(self):
        """Generate report for all discovered devices (entries)

        :return:
        """
        raise NotImplementedError("Class {} must implement method 'generate'".format(type(self)))


class FileReport(AbstractReport):
    DESCRIPTION_COLUMN_WIDTH = 60
    COMMENT_COLUMN_WIDTH = 40
    DEFAULT_REPORT_FILE = "report.txt"

    def __init__(self, file_name=None):
        """

        :param str file_name:
        """
        super(FileReport, self).__init__()
        if file_name is None:
            file_name = self.DEFAULT_REPORT_FILE

        self.file_name = file_name

    def generate(self):
        """Print report for all discovered devices to the console"""
        table_header = ("IP", "VENDOR", "sysObjectID", "DESCRIPTION", "SNMP READ COMMUNITY", "USER", "PASSWORD",
                        "ENABLE PASSWORD", "ADDED TO CLOUDSHELL", "COMMENT")
        empty_row = ("",) * len(table_header)
        table_data = [table_header]

        for entry in self._entries:
            description = '\n'.join(wrap(str(entry.description), self.DESCRIPTION_COLUMN_WIDTH))
            comment = '\n'.join(wrap(str(entry.comment), self.COMMENT_COLUMN_WIDTH))
            table_data.extend([(entry.ip, entry.vendor, entry.sys_object_id, description, entry.snmp_community,
                                entry.user, entry.password, entry.enable_password, entry.status, comment),
                               empty_row])  # add an empty row between records

        table = AsciiTable(table_data)

        with open(self.file_name, "w") as report_file:
            report_file.write(table.table)
