from autodiscovery.config import DEFAULT_CLOUDSHELL_DOMAIN
from autodiscovery.config import DEFAULT_RESOURCE_FOLDER_PATH


class InputDataModel(object):
    def __init__(self, devices_ips, cs_ip, cs_user, cs_password, snmp_community_strings, vendor_settings):
        """

        :param list[DeviceIPRange] devices_ips:
        :param str cs_ip:
        :param str cs_user:
        :param str cs_password:
        :param list[str] snmp_community_strings:
        :param autodiscovery.models.VendorSettingsCollection vendor_settings:
        """
        self.devices_ips = devices_ips
        self.cs_ip = cs_ip
        self.cs_user = cs_user
        self.cs_password = cs_password
        self.snmp_community_strings = snmp_community_strings
        self.vendor_settings = vendor_settings


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


class CLICredentials(object):
    def __init__(self, user=None, password=None, enable_password=None):
        """

        :param str user:
        :param str password:
        :param str enable_password:
        """
        self.user = user
        self.password = password
        self.enable_password = enable_password

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return all([self.user == other.user,
                        self.password == other.password,
                        self.enable_password == other.enable_password])

        return False


class VendorCLICredentials(object):
    def __init__(self, name, cli_credentials):
        """

        :param str name: vendor name
        :param list[CLICredentials] cli_credentials:
        """
        self.name = name
        self.cli_credentials = cli_credentials

    def update_valid_creds(self, valid_creds):
        """Set valid credentials to be first in the list of possible CLI credentials for the Vendor

        :param CLICredentials valid_creds:
        :return:
        """
        if valid_creds in self.cli_credentials:
            self.cli_credentials.remove(valid_creds)

        self.cli_credentials.insert(0, valid_creds)


class VendorSettingsCollection(object):
    def __init__(self, vendor_settings):
        """

        :param dict vendor_settings:
        """
        self._cli_creds = []
        self._folder_paths = {}

        default_settings = vendor_settings.pop("default", {})
        default_creds = [CLICredentials(user=creds.get("user"),
                                        password=creds.get("password"),
                                        enable_password=creds.get("enable password"))
                         for creds in default_settings.get("cli-credentials", [])]

        self._default_creds = VendorCLICredentials(name="default", cli_credentials=default_creds)
        self._default_folder = default_settings.get("folder-path", DEFAULT_RESOURCE_FOLDER_PATH)

        for vendor_name, vendor_settings in vendor_settings.iteritems():
            vendor_creds = vendor_settings.get("cli-credentials", [])
            cli_creds = [CLICredentials(user=creds.get("user"),
                                        password=creds.get("password"),
                                        enable_password=creds.get("enable password"))
                         for creds in vendor_creds]
            cli_creds.extend(default_creds)
            self._cli_creds.append(VendorCLICredentials(name=vendor_name, cli_credentials=cli_creds))

            folder_path = vendor_settings.get("folder-path")
            if folder_path is not None:
                self._folder_paths[vendor_name] = folder_path

    def get_creds_by_vendor(self, vendor):
        """Get CLI credentials by given vendor

        :param VendorDefinition vendor:
        :rtype: VendorCLICredentials
        """
        for vendor_creds in self._cli_creds:
            if vendor.check_vendor_name(vendor_creds.name):
                return vendor_creds

        return self._default_creds

    def get_folder_path_by_vendor(self, vendor):
        """Get folder path by given vendor

        :param VendorDefinition vendor:
        :rtype: str
        """
        for vendor_name, folder_path in self._folder_paths.iteritems():
            if vendor.check_vendor_name(vendor_name):
                return folder_path

        return self._default_folder
