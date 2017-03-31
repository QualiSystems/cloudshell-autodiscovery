from autodiscovery.exceptions import ReportableException


class AbstractReport(object):
    HEADER = ("IP", "VENDOR", "sysObjectID", "DESCRIPTION", "SNMP READ COMMUNITY", "MODEL_TYPE", "DEVICE_NAME",
              "DOMAIN", "FOLDER", "ATTRIBUTES", "ADDED TO CLOUDSHELL", "COMMENT")

    def __init__(self):
        self._entries = []

    def add_entry(self, ip, domain, offline):
        """Add new Entry for the device with given IP

        :param str ip: IP address of the discovered device
        :param str domain: domain on the CloudShell
        :param bool offline:
        :rtype: Entry
        """
        if offline:
            status = Entry.SKIPPED_STATUS
        else:
            status = Entry.SUCCESS_STATUS

        entry = Entry(ip=ip, status=status, domain=domain)
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
    ATTRIBUTES_SEPARATOR = ";"

    def __init__(self, ip, status, domain, vendor="", device_name="", model_type="", sys_object_id="",
                 snmp_community="", description="", comment="", folder_path="", attributes=None):
        self.ip = ip
        self.status = status
        self.domain = domain
        self.vendor = vendor
        self.device_name = device_name
        self.model_type = model_type
        self.sys_object_id = sys_object_id
        self.snmp_community = snmp_community
        self.description = description
        self.comment = comment
        self.folder_path = folder_path
        if attributes is None:
            attributes = {}
        self.attributes = attributes

    def add_attribute(self, name, value):
        """

        :param str name:
        :param str value:
        :return:
        """
        self.attributes[name] = value

    @property
    def formatted_attrs(self):
        """Return formatted resource attributes

        :rtype: str
        """
        return self.ATTRIBUTES_SEPARATOR.join(["{}={}".format(key, val)
                                               for key, val in self.attributes.iteritems()])

    @staticmethod
    def parse_formatted_attrs(attributes):
        """Parse attributes from the formatted string

        :rtype: list[str]
        """
        return {key.strip(): val.strip() for key, val in
                (attr.split("=") for attr in attributes.split(Entry.ATTRIBUTES_SEPARATOR) if attr)}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.status = self.FAILED_STATUS
            if isinstance(exc_val, ReportableException):
                self.comment = str(exc_val)
