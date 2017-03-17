from autodiscovery.exceptions import ReportableException


class AbstractReport(object):
    HEADER = ("IP", "VENDOR", "sysObjectID", "DESCRIPTION", "SNMP READ COMMUNITY", "USER", "PASSWORD",
              "ENABLE PASSWORD", "MODEL_TYPE", "DEVICE_NAME", "ADDED TO CLOUDSHELL", "COMMENT")

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
        """Generate report for all discovered devices (entries)

        :return:
        """
        raise NotImplementedError("Class {} must implement method 'generate'".format(type(self)))

    def parse_entries_from_file(self, report_file):
        """Parse all discovered devices (entries) from a given file

        :param str report_file: file path to the generated report
        :rtype: list[Entry]
        """
        raise NotImplementedError("Class {} must implement method 'parse_entries_from_file'".format(type(self)))


class Entry(object):
    SUCCESS_STATUS = "Success"
    FAILED_STATUS = "Failed"
    SKIPPED_STATUS = "Skipped"

    def __init__(self, ip, status, vendor="", device_name="", model_type="", sys_object_id="", snmp_community="",
                 user="", password="", enable_password="", description="", comment=""):
        self.ip = ip
        self.status = status
        self.vendor = vendor
        self.device_name = device_name
        self.model_type = model_type
        self.sys_object_id = sys_object_id
        self.snmp_community = snmp_community
        self.user = user
        self.password = password
        self.enable_password = enable_password
        self.description = description
        self.comment = comment

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.status = self.FAILED_STATUS
            if isinstance(exc_val, ReportableException):
                self.comment = str(exc_val)
