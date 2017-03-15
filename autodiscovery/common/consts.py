class ResourceModelsAttributes(object):
    """Container for the CloudShell Resource Model Attributes names"""
    ENABLE_SNMP = "Enable SNMP"
    SNMP_READ_COMMUNITY = "SNMP Read Community"
    USER = "User"
    PASSWORD = "Password"
    ENABLE_PASSWORD = "Enable Password"


class CloudshellAPIErrorCodes(object):
    """Container for the CloudShell API error codes"""
    INCORRECT_LOGIN = "100"
    INCORRECT_PASSWORD = "118"
    RESOURCE_ALREADY_EXISTS = "114"
    UNABLE_TO_LOCATE_DRIVER = "129"
    UNABLE_TO_LOCATE_FAMILY_OR_MODEL = "100"  # not a typo, same code as for incorrect login
