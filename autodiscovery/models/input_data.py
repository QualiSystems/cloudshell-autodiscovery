class InputDataModel(object):
    def __init__(self, devices_ips, cs_ip, cs_user, cs_password, snmp_community_strings, cli_credentials):
        """

        :param list[str] devices_ips:
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
