from cloudshell.api.common_cloudshell_api import CloudShellAPIError

from autodiscovery.cli_sessions import SSHDiscoverySession
from autodiscovery.cli_sessions import TelnetDiscoverySession
from autodiscovery.common.consts import CloudshellAPIErrorCodes
from autodiscovery.common.consts import ResourceModelsAttributes
from autodiscovery.exceptions import ReportableException
from autodiscovery.handlers.base import AbstractHandler


class NetworkingTypeHandler(AbstractHandler):

    def _get_cli_credentials(self, vendor, cli_credentials, device_ip):
        """

        :param autodiscovery.models.VendorDefinition vendor:
        :param autodiscovery.models.CLICredentialsCollection cli_credentials:
        :param str device_ip:
        :return:
        """
        vendor_cli_creds = cli_credentials.get_creds_by_vendor(vendor)

        if vendor_cli_creds:
            for session in (SSHDiscoverySession(device_ip), TelnetDiscoverySession(device_ip)):
                try:
                    valid_creds = session.check_credentials(cli_credentials=vendor_cli_creds,
                                                            default_prompt=vendor.default_prompt,
                                                            enable_prompt=vendor.enable_prompt,
                                                            logger=self.logger)
                except Exception:
                    self.logger.warning("{} Credentials aren't valid for the device with IP {}"
                                        .format(session.SESSION_TYPE, device_ip), exc_info=True)
                else:
                    vendor_cli_creds.update_valid_creds(valid_creds)
                    return valid_creds

    def discover(self, entry, vendor, cli_credentials):
        """

        :param entry:
        :param vendor:
        :param cli_credentials:
        :return:
        """
        device_os = vendor.get_device_os(entry.description)
        if device_os is None:
            raise ReportableException("Unable to determine device OS")

        model_type = device_os.get_device_model_type(system_description=entry.description)
        if model_type is None:
            raise ReportableException("Unable to determine device model type")

        entry.model_type = model_type

        cli_creds = self._get_cli_credentials(vendor=vendor,
                                              cli_credentials=cli_credentials,
                                              device_ip=entry.ip)
        if cli_creds:
            entry.user = cli_creds.user
            entry.password = cli_creds.password
            entry.enable_password = cli_creds.enable_password

        return entry

    def upload(self, entry, vendor, cs_session):
        """

        :param entry:
        :param vendor:
        :param cs_session:
        :return:
        """
        self.cs_session = cs_session

        attributes = {
            ResourceModelsAttributes.ENABLE_SNMP: "False",
            ResourceModelsAttributes.SNMP_READ_COMMUNITY: entry.snmp_community,
            ResourceModelsAttributes.USER: entry.user,
            ResourceModelsAttributes.PASSWORD: entry.password,
            ResourceModelsAttributes.ENABLE_PASSWORD: entry.enable_password
        }

        device_os = vendor.get_device_os(entry.description)
        if device_os is None:
            raise ReportableException("Unable to determine device OS")

        familes_data = device_os.families.get(entry.model_type)

        if "second_gen" in familes_data:
            second_gen = familes_data["second_gen"]
            try:
                resource_name = self._create_cs_resource(resource_name=entry.device_name,
                                                         resource_family=second_gen["family_name"],
                                                         resource_model=second_gen["model_name"],
                                                         driver_name=second_gen["driver_name"],
                                                         device_ip=entry.ip,
                                                         attributes=attributes,
                                                         attribute_prefix="{}.".format(second_gen["model_name"]))
            except CloudShellAPIError as e:
                if e.code == CloudshellAPIErrorCodes.UNABLE_TO_LOCATE_FAMILY_OR_MODEL:
                    if "first_gen" in familes_data:
                        first_gen = familes_data["first_gen"]
                        resource_name = self._create_cs_resource(resource_name=entry.device_name,
                                                                 resource_family=first_gen["family_name"],
                                                                 resource_model=first_gen["model_name"],
                                                                 driver_name=first_gen["driver_name"],
                                                                 device_ip=entry.ip,
                                                                 attributes=attributes,
                                                                 attribute_prefix="")
                    else:
                        raise
                else:
                    raise
        else:
            first_gen = familes_data["first_gen"]
            resource_name = self._create_cs_resource(resource_name=entry.device_name,
                                                     resource_family=first_gen["family_name"],
                                                     resource_model=first_gen["model_name"],
                                                     driver_name=first_gen["driver_name"],
                                                     device_ip=entry.ip,
                                                     attributes=attributes,
                                                     attribute_prefix="")

        self.cs_session.AutoLoad(resource_name)
