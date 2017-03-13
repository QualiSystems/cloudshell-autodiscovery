class AutoDiscoveryException(Exception):
    """Base Exception for all auto discovery errors"""
    pass


class ReportableException(AutoDiscoveryException):
    """Exception that can be added to the report"""
    pass
