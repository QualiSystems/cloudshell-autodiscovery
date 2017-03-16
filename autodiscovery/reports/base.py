from autodiscovery.exceptions import ReportableException


class AbstractReport(object):
    HEADER = ("IP", "VENDOR", "sysObjectID", "DESCRIPTION", "SNMP READ COMMUNITY", "USER", "PASSWORD",
              "ENABLE PASSWORD", "ADDED TO CLOUDSHELL", "COMMENT")

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
                self.comment = str(exc_val)
