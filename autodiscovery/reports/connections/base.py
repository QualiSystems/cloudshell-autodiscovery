import collections

from autodiscovery.reports.base import AbstractEntry
from autodiscovery.reports.base import AbstractReport


class AbstractConnectionsReport(AbstractReport):
    SOURCE_PORT_HEADER = "Source Port Full Name"
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
        return collections.OrderedDict([(self.SOURCE_PORT_HEADER, "source_port"),
                                        (self.TARGET_PORT_HEADER, "target_port"),
                                        (self.DOMAIN_HEADER, "domain"),
                                        (self.STATUS_HEADER, "status"),
                                        (self.COMMENT_HEADER, "comment")])


class Entry(AbstractEntry):
    def __init__(self, source_port, target_port, domain, status=AbstractEntry.SUCCESS_STATUS, comment=""):
        """

        :param source_port:
        :param target_port:
        :param domain:
        :param comment:
        """
        super(Entry, self).__init__(status=status)
        self.source_port = source_port
        self.target_port = target_port
        self.domain = domain
        self.comment = comment
