import collections

from autodiscovery.reports.base import AbstractEntry
from autodiscovery.reports.base import AbstractReport


class AbstractConnectionsReport(AbstractReport):
    DEFAULT_REPORT_NAME = "connections-report"
    RESOURCE_NAME_HEADER = "Resource Name"
    SOURCE_PORT_HEADER = "Source Port Full Name"
    ADJACENT_HEADER = "Adjacent"
    TARGET_PORT_HEADER = "Target Port Full Name"
    DOMAIN_HEADER = "Domain"
    STATUS_HEADER = "Connection Status"
    COMMENT_HEADER = "Comment"

    @property
    def entry_class(self):
        return Entry

    @property
    def _header_entry_map(self):
        """Map between header and Entry attribute name

        :return:
        """
        return collections.OrderedDict([(self.RESOURCE_NAME_HEADER, "resource_name"),
                                        (self.SOURCE_PORT_HEADER, "source_port"),
                                        (self.ADJACENT_HEADER, "adjacent"),
                                        (self.TARGET_PORT_HEADER, "target_port"),
                                        (self.DOMAIN_HEADER, "domain"),
                                        (self.STATUS_HEADER, "status"),
                                        (self.COMMENT_HEADER, "comment")])

    def add_entry(self, offline, **kwargs):
        """

        :param bool offline:
        :rtype: Entry
        """
        if offline:
            status = Entry.SKIPPED_STATUS
        else:
            status = Entry.SUCCESS_STATUS

        kwargs["status"] = status
        return super(AbstractConnectionsReport, self).add_entry(**kwargs)


class Entry(AbstractEntry):
    SKIPPED_STATUS = "Skipped"

    def __init__(self, resource_name, source_port, adjacent, target_port, domain,
                 status, comment=""):
        """

        :param resource_name:
        :param source_port:
        :param adjacent:
        :param target_port:
        :param domain:
        :param comment:
        """
        super(Entry, self).__init__(status=status)
        self.resource_name = resource_name
        self.source_port = source_port
        self.adjacent = adjacent
        self.target_port = target_port
        self.domain = domain
        self.comment = comment
