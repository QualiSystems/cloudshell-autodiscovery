import collections

from autodiscovery.reports.base import AbstractEntry
from autodiscovery.reports.base import AbstractReport


class AbstractDiscoveryReport(AbstractReport):
    IP_HEADER = "IP"
    VENDOR_HEADER = "VENDOR"
    SYS_OBJ_ID_HEADER = "sysObjectID"
    DESCRIPTION_HEADER = "DESCRIPTION"
    SNMP_READ_COMMUNITY_HEADER = "SNMP READ COMMUNITY"
    MODEL_TYPE_HEADER = "MODEL_TYPE"
    DEVICE_NAME_HEADER = "DEVICE_NAME"
    DOMAIN_HEADER = "DOMAIN"
    FOLDER_HEADER = "FOLDER"
    ATTRIBUTES_HEADER = "ATTRIBUTES"
    ADDED_TO_CLOUDSHELL_HEADER = "ADDED TO CLOUDSHELL"
    COMMENT_HEADER = "COMMENT"

    @property
    def entry_class(self):
        return Entry

    @property
    def _header_entry_map(self):
        """Map between header and Entry attribute name

        :return:
        """
        return collections.OrderedDict([(self.IP_HEADER, "ip"),
                                        (self.VENDOR_HEADER, "vendor"),
                                        (self.SYS_OBJ_ID_HEADER, "sys_object_id"),
                                        (self.DESCRIPTION_HEADER, "description"),
                                        (self.SNMP_READ_COMMUNITY_HEADER, "snmp_community"),
                                        (self.MODEL_TYPE_HEADER, "model_type"),
                                        (self.DEVICE_NAME_HEADER, "device_name"),
                                        (self.DOMAIN_HEADER, "domain"),
                                        (self.FOLDER_HEADER, "folder_path"),
                                        (self.ATTRIBUTES_HEADER, "formatted_attrs"),
                                        (self.ADDED_TO_CLOUDSHELL_HEADER, "status"),
                                        (self.COMMENT_HEADER, "comment")])

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

        return super(AbstractDiscoveryReport, self).add_entry(ip=ip, domain=domain, status=status)


class Entry(AbstractEntry):
    SKIPPED_STATUS = "Skipped"
    ATTRIBUTES_SEPARATOR = ";"

    def __init__(self, ip, status, domain, vendor="", device_name="", model_type="", sys_object_id="",
                 snmp_community="", description="", comment="", folder_path="", attributes=None, formatted_attrs=None):
        super(Entry, self).__init__(status=status)
        self.ip = ip
        self.domain = domain
        self.vendor = vendor
        self.device_name = device_name
        self.model_type = model_type
        self.sys_object_id = sys_object_id
        self.snmp_community = snmp_community
        self.description = description
        self.comment = comment
        self.folder_path = folder_path

        if formatted_attrs is not None:
            attributes = self.parse_formatted_attrs(formatted_attrs)
        elif attributes is None:
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
