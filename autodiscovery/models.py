import re


class VendorDefinitionCollection(object):
    def __init__(self, vendors):
        """

        :param list[VendorDefinition] vendors:
        """
        self._vendors = vendors

    def get_vendor(self, vendor_name):
        """Find vendor by it name/aliases

        :param str vendor_name: vendor name from the PEN data file
        :rtype: VendorDefinition
        """
        for vendor in self._vendors:
            if vendor.check_vendor_name(vendor_name):
                return vendor


class VendorDefinition(object):
    def __init__(self, name, aliases, vendor_type, default_os, default_prompt, enable_prompt, operation_systems):
        """

        :param str name:
        :param list aliases:
        :param str vendor_type:
        :param str default_os:
        :param str default_prompt:
        :param str enable_prompt:
        :param list[OperationSystem] operation_systems:
        """
        self.name = name
        self.aliases = aliases
        self.vendor_type = vendor_type
        self.default_os = default_os
        self.default_prompt = default_prompt
        self.enable_prompt = enable_prompt
        self.operation_systems = operation_systems

    def check_in_aliases(self, vendor_name):
        """Check in given vendor name is in aliases for current Vendor

        :param str vendor_name: vendor name from the PEN data file
        :rtype: bool
        """
        aliases_regexp = r"({})".format("|".join(self.aliases))
        return bool(re.search(aliases_regexp, vendor_name, flags=re.DOTALL))

    def check_vendor_name(self, vendor_name):
        """Check if given name is a name for the Vendor

        :param str vendor_name: vendor name from the PEN data file
        :rtype: bool
        """
        return self.name.lower() == vendor_name.lower() or self.check_in_aliases(vendor_name)

    def get_device_os(self, system_description):
        """Find device Operation System by its system description

        :param str system_description: device system description from SNMPv2-MIB.sysDescr
        :rtype: OperationSystem
        """
        for os in self.operation_systems:
            aliases_regexp = r"({})".format("|".join(os.aliases))
            if re.search(aliases_regexp, system_description, flags=re.DOTALL):
                return os

        return self.get_default_device_os()

    def get_default_device_os(self):
        """Get default Operation System for Vendor

        :rtype: OperationSystem
        """
        if self.default_os is None:
            return

        for os in self.operation_systems:
            if os.name == self.default_os:
                return os


class OperationSystem(object):
    def __init__(self, name, aliases, multi_models, default_model, models_map, families, first_gen, second_gen):
        """

        :param str name:
        :param list aliases:
        :param bool multi_models:
        :param str default_model:
        :param list[dict] models_map:
        :param dict families:
        :param dict first_gen:
        :param dict second_gen:
        """
        self.name = name
        self.aliases = aliases
        self.multi_models = multi_models
        self.default_model = default_model
        self.models_map = models_map
        self.families = families
        self.first_gen = first_gen
        self.second_gen = second_gen

    def get_device_model_type(self, system_description):
        """Find device model (switch, router, etc.) by device system description

        :param str system_description: device system description from SNMPv2-MIB.sysDescr
        :return:
        """
        for model_map in self.models_map:
            aliases_regexp = r"({})".format("|".join(model_map["aliases"]))
            if re.search(aliases_regexp, system_description, flags=re.DOTALL):
                return model_map["model"]

    def get_resource_family(self, model_type):
        """Get Resource Family for the given model type

        :param str model_type:
        :rtype: str
        """
        return self.families[model_type]["family_name"]

    def get_resource_model(self, model_type):
        """Get Resource Model for the given model type

        :param str model_type:
        :rtype: str
        """
        return self.families[model_type]["model_name"]

    def get_driver_name_1st_gen(self):
        """Get Driver Name for the 1-st generation shells (CloudShell version < 8.0)

        :rtype: str
        """
        return self.first_gen["driver_name"]

    def get_driver_name_2nd_gen(self, model_type):
        """Get Driver Name for the 2-nd generation shells (CloudShell version > 8.0)

        :param str model_type:
        :rtype: str
        """
        return self.second_gen[model_type]["driver_name"]


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


class CLICredentialsCollection(object):
    def __init__(self, cli_credentials):
        """

        :param dict cli_credentials:
        """
        self._cli_creds = []
        default_creds = [CLICredentials(**creds) for creds in cli_credentials.pop("default", [])]
        self._default_creds = VendorCLICredentials(name="default", cli_credentials=default_creds)

        for vendor_name, vendor_creds in cli_credentials.iteritems():
            cli_creds = [CLICredentials(**creds) for creds in vendor_creds]
            cli_creds.extend(default_creds)
            self._cli_creds.append(VendorCLICredentials(name=vendor_name, cli_credentials=cli_creds))

    def get_creds_by_vendor(self, vendor):
        """Get CLI credentials by given vendor

        :param VendorDefinition vendor:
        :rtype: VendorCLICredentials
        """
        for vendor_creds in self._cli_creds:
            if vendor.check_vendor_name(vendor_creds.name):
                return vendor_creds

        return self._default_creds


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
