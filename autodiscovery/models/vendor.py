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
            if os.aliases:
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
