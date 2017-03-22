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


class BaseVendorDefinition(object):
    def __init__(self, name, aliases, vendor_type, default_prompt, enable_prompt, *args, **kwargs):
        """

        :param str name:
        :param list aliases:
        :param str vendor_type:
        :param str default_prompt:
        :param str enable_prompt:
        """
        self.name = name
        self.aliases = aliases
        self.vendor_type = vendor_type
        self.default_prompt = default_prompt
        self.enable_prompt = enable_prompt

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


class NetworkingVendorDefinition(BaseVendorDefinition):
    def __init__(self, name, aliases, vendor_type, default_prompt, enable_prompt, default_os, operation_systems):
        """

        :param str name:
        :param list aliases:
        :param str vendor_type:
        :param str default_prompt:
        :param str enable_prompt:
        :param str default_os:
        :param list[OperationSystem] operation_systems:
        """
        super(NetworkingVendorDefinition, self).__init__(name, aliases, vendor_type, default_prompt, enable_prompt)
        self.default_os = default_os
        self.operation_systems = operation_systems

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


class PDUVendorDefinition(BaseVendorDefinition):
    def __init__(self, name, aliases, vendor_type, default_prompt, enable_prompt, family_name, model_name, driver_name):
        """

        :param str name:
        :param list aliases:
        :param str vendor_type:
        :param str default_prompt:
        :param str enable_prompt:
        :param str family_name:
        :param str model_name:
        :param str driver_name:
        """
        super(PDUVendorDefinition, self).__init__(name, aliases, vendor_type, default_prompt, enable_prompt)
        self.family_name = family_name
        self.model_name = model_name
        self.driver_name = driver_name


class OperationSystem(object):
    def __init__(self, name, aliases, default_model, models_map, families):
        """

        :param str name:
        :param list aliases:
        :param str default_model:
        :param list[dict] models_map:
        :param dict families:
        """
        self.name = name
        self.aliases = aliases
        self.default_model = default_model
        self.models_map = models_map
        self.families = families

    def get_device_model_type(self, system_description):
        """Find device model (switch, router, etc.) by device system description

        :param str system_description: device system description from SNMPv2-MIB.sysDescr
        :return:
        """
        for model_map in self.models_map:
            aliases_regexp = r"({})".format("|".join(model_map["aliases"]))
            if re.search(aliases_regexp, system_description, flags=re.DOTALL):
                return model_map["model"]

        return self.default_model

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
        default_creds = [CLICredentials(user=creds.get("user"),
                                        password=creds.get("password"),
                                        enable_password=creds.get("enable password"))
                         for creds in cli_credentials.pop("default", [])]

        self._default_creds = VendorCLICredentials(name="default", cli_credentials=default_creds)

        for vendor_name, vendor_creds in cli_credentials.iteritems():
            cli_creds = [CLICredentials(user=creds.get("user"),
                                        password=creds.get("password"),
                                        enable_password=creds.get("enable password"))
                         for creds in vendor_creds]
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
