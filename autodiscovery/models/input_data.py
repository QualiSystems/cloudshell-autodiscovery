from autodiscovery.config import DEFAULT_CLOUDSHELL_DOMAIN


class InputDataModel(object):
    def __init__(self, devices_ips, cs_ip, cs_user, cs_password, snmp_community_strings, cli_credentials):
        """

        :param list[DeviceIPRange] devices_ips:
        :param str cs_ip:
        :param str cs_user:
        :param str cs_password:
        :param list[str] snmp_community_strings:
        :param CLICredentialsCollection cli_credentials:
        """
        self.devices_ips = devices_ips
        self.cs_ip = cs_ip
        self.cs_user = cs_user
        self.cs_password = cs_password
        self.snmp_community_strings = snmp_community_strings
        self.cli_credentials = cli_credentials


class DeviceIPRange(object):
    def __init__(self, ip_range, domain=None):
        """

        :param list[str] ip_range:
        :param str domain:
        """
        self.ip_range = ip_range
        if domain is None:
            domain = DEFAULT_CLOUDSHELL_DOMAIN

        self.domain = domain
