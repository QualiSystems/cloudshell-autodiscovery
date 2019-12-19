from dataclasses import dataclass
from typing import List

from autodiscovery.config import DEFAULT_CLOUDSHELL_DOMAIN, DEFAULT_RESOURCE_FOLDER_PATH


class VendorSettingsCollection(object):
    def __init__(self, vendor_settings):
        """Init command.

        :param dict vendor_settings:
        """
        self._cli_creds = []
        self._folder_paths = {}

        default_settings = vendor_settings.pop("default", {})
        default_creds = [
            CLICredentials(
                user=creds.get("user"),
                password=creds.get("password"),
                enable_password=creds.get("enable password"),
            )
            for creds in default_settings.get("cli-credentials", [])
        ]

        self._default_creds = VendorCLICredentials(
            name="default", cli_credentials=default_creds
        )
        self._default_folder = default_settings.get(
            "folder-path", DEFAULT_RESOURCE_FOLDER_PATH
        )

        for vendor_name, vendor_settings in vendor_settings.items():
            vendor_creds = vendor_settings.get("cli-credentials", [])
            cli_creds = [
                CLICredentials(
                    user=creds.get("user"),
                    password=creds.get("password"),
                    enable_password=creds.get("enable password"),
                )
                for creds in vendor_creds
            ]
            cli_creds.extend(default_creds)
            self._cli_creds.append(
                VendorCLICredentials(name=vendor_name, cli_credentials=cli_creds)
            )

            folder_path = vendor_settings.get("folder-path")
            if folder_path is not None:
                self._folder_paths[vendor_name] = folder_path

    def get_creds_by_vendor(self, vendor):
        """Get CLI credentials by given vendor.

        :param VendorDefinition vendor:
        :rtype: VendorCLICredentials
        """
        for vendor_creds in self._cli_creds:
            if vendor.check_vendor_name(vendor_creds.name):
                return vendor_creds

        return self._default_creds

    def get_folder_path_by_vendor(self, vendor):
        """Get folder path by given vendor.

        :param VendorDefinition vendor:
        :rtype: str
        """
        for vendor_name, folder_path in self._folder_paths.items():
            if vendor.check_vendor_name(vendor_name):
                return folder_path

        return self._default_folder


@dataclass
class CLICredentials:
    user: str = None
    password: str = None
    enable_password: str = None


@dataclass
class VendorCLICredentials:
    name: str
    cli_credentials: List[CLICredentials]

    def update_valid_creds(self, valid_creds):
        """Set valid credentials to be first in the list of possible CLI credentials.

        :param CLICredentials valid_creds:
        :return:
        """
        if valid_creds in self.cli_credentials:
            self.cli_credentials.remove(valid_creds)

        self.cli_credentials.insert(0, valid_creds)


@dataclass
class DeviceIPRange:
    ip_range: List[str]
    domain: str = DEFAULT_CLOUDSHELL_DOMAIN

    def __post_init__(self):
        if self.domain is None:
            self.domain = DEFAULT_CLOUDSHELL_DOMAIN


@dataclass
class InputDataModel:
    devices_ips: List[DeviceIPRange]
    cs_ip: str
    cs_user: str
    cs_password: str
    snmp_community_strings: List[str]
    vendor_settings: VendorSettingsCollection
