class AutoDiscoveryException(Exception):
    """Base Exception for all auto discovery errors."""


class ReportableException(AutoDiscoveryException):
    """Exception that can be added to the report."""
