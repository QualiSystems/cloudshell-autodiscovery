import re
from dataclasses import dataclass
from typing import List


@dataclass
class OperationSystem(object):
    name: str
    aliases: List[str]
    default_model: str
    models_map: List[dict]
    families: dict

    def get_device_model_type(self, system_description):
        """Find device model (switch, router, etc.) by device sys description.

        :param system_description: device system description from SNMPv2-MIB.sysDescr
        :type system_description: str
        :return:
        """
        for model_map in self.models_map:
            aliases_regexp = fr"({'|'.join(model_map['aliases'])})"
            if re.search(aliases_regexp, system_description, flags=re.DOTALL):
                return model_map["model"]

        return self.default_model

    def get_resource_family(self, model_type):
        """Get Resource Family for the given model type.

        :param str model_type:
        :rtype: str
        """
        return self.families[model_type]["family_name"]

    def get_resource_model(self, model_type):
        """Get Resource Model for the given model type.

        :param str model_type:
        :rtype: str
        """
        return self.families[model_type]["model_name"]


@dataclass
class BaseVendorDefinition:
    name: str
    aliases: List[str]
    vendor_type: str
    default_prompt: str
    enable_prompt: str

    def check_in_aliases(self, vendor_name):
        """Check in given vendor name is in aliases for current Vendor.

        :param str vendor_name: vendor name from the PEN data file
        :rtype: bool
        """
        aliases_regexp = fr"({'|'.join(self.aliases)})"
        return bool(re.search(aliases_regexp, vendor_name, flags=re.DOTALL))

    def check_vendor_name(self, vendor_name):
        """Check if given name is a name for the Vendor.

        :param str vendor_name: vendor name from the PEN data file
        :rtype: bool
        """
        return self.name.lower() == vendor_name.lower() or self.check_in_aliases(
            vendor_name
        )


@dataclass
class NetworkingVendorDefinition(BaseVendorDefinition):
    default_os: str
    operation_systems: List[OperationSystem]

    def get_device_os(self, system_description):
        """Find device Operation System by its system description.

        :param system_description: device system description from SNMPv2-MIB.sysDescr
        :type system_description: str
        :rtype: OperationSystem
        """
        for os in self.operation_systems:
            if os.aliases:
                aliases_regexp = fr"({'|'.join(os.aliases)})"
                if re.search(aliases_regexp, system_description, flags=re.DOTALL):
                    return os

        return self.get_default_device_os()

    def get_default_device_os(self):
        """Get default Operation System for Vendor.

        :rtype: OperationSystem
        """
        if self.default_os is None:
            return

        for os in self.operation_systems:
            if os.name == self.default_os:
                return os


@dataclass
class PDUVendorDefinition(BaseVendorDefinition):
    family_name: str
    model_name: str
    driver_name: str


@dataclass
class VendorDefinitionCollection:
    vendors: List[BaseVendorDefinition]

    def get_vendor(self, vendor_name):
        """Find vendor by it name/aliases.

        :param str vendor_name: vendor name from the PEN data file
        :rtype: BaseVendorDefinition
        """
        for vendor in self.vendors:
            if vendor.check_vendor_name(vendor_name):
                return vendor
