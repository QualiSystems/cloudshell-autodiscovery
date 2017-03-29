from cloudshell.api.common_cloudshell_api import CloudShellAPIError

from autodiscovery.common.consts import CloudshellAPIErrorCodes
from autodiscovery.common.consts import ResourceModelsAttributes
from autodiscovery.exceptions import ReportableException
from autodiscovery.handlers.base import AbstractHandler


class NetworkingTypeHandler(AbstractHandler):

    def discover(self, entry, vendor, vendor_settings):
        """Discover device attributes

        :param autodiscovery.reports.base.Entry entry:
        :param autodiscovery.models.vendor.NetworkingVendorDefinition vendor:
        :param autodiscovery.models.VendorSettingsCollection vendor_settings:
        :rtype: autodiscovery.reports.base.Entry
        """
        device_os = vendor.get_device_os(entry.description)
        if device_os is None:
            raise ReportableException("Unable to determine device OS")

        model_type = device_os.get_device_model_type(system_description=entry.description)
        if model_type is None:
            raise ReportableException("Unable to determine device model type")

        entry.model_type = model_type

        cli_creds = self._get_cli_credentials(vendor=vendor,
                                              vendor_settings=vendor_settings,
                                              device_ip=entry.ip)
        if cli_creds is None:
            entry.comment = "Unable to discover device user/password/enable password"
        else:
            entry.user = cli_creds.user
            entry.password = cli_creds.password
            entry.enable_password = cli_creds.enable_password

        entry.folder_path = vendor_settings.get_folder_path_by_vendor(vendor)
        return entry

    def upload(self, entry, vendor, cs_session):
        """Upload discovered device on the CloudShell

        :param autodiscovery.reports.base.Entry entry:
        :param autodiscovery.models.vendor.NetworkingVendorDefinition vendor:
        :param cloudshell.api.cloudshell_api.CloudShellAPISession cs_session:
        :return:
        """
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

        # todo(A.Piddubny): simplify it
        if "second_gen" in familes_data:
            second_gen = familes_data["second_gen"]
            try:
                resource_name = self._create_cs_resource(cs_session=cs_session,
                                                         resource_name=entry.device_name,
                                                         resource_family=second_gen["family_name"],
                                                         resource_model=second_gen["model_name"],
                                                         driver_name=second_gen["driver_name"],
                                                         device_ip=entry.ip,
                                                         folder_path=entry.folder_path,
                                                         attributes=attributes,
                                                         attribute_prefix="{}.".format(second_gen["model_name"]))
            except CloudShellAPIError as e:
                if e.code == CloudshellAPIErrorCodes.UNABLE_TO_LOCATE_FAMILY_OR_MODEL:
                    self.logger.info("2-nd generation shell {} is not installed... trying 1-st generation one"
                                     .format(second_gen["driver_name"]))

                    if "first_gen" in familes_data:
                        first_gen = familes_data["first_gen"]
                        try:
                            resource_name = self._create_cs_resource(cs_session=cs_session,
                                                                     resource_name=entry.device_name,
                                                                     resource_family=first_gen["family_name"],
                                                                     resource_model=first_gen["model_name"],
                                                                     driver_name=first_gen["driver_name"],
                                                                     device_ip=entry.ip,
                                                                     folder_path=entry.folder_path,
                                                                     attributes=attributes)
                        except CloudShellAPIError as e:
                            if e.code == CloudshellAPIErrorCodes.UNABLE_TO_LOCATE_FAMILY_OR_MODEL:
                                entry.comment = "Shell {} is not installed".format(second_gen["driver_name"])
                            else:
                                raise
                        else:
                            cs_session.AutoLoad(resource_name)
                    else:
                        raise
                else:
                    raise
            else:
                cs_session.AutoLoad(resource_name)
        else:
            first_gen = familes_data["first_gen"]
            try:
                resource_name = self._create_cs_resource(cs_session=cs_session,
                                                         resource_name=entry.device_name,
                                                         resource_family=first_gen["family_name"],
                                                         resource_model=first_gen["model_name"],
                                                         driver_name=first_gen["driver_name"],
                                                         device_ip=entry.ip,
                                                         folder_path=entry.folder_path,
                                                         attributes=attributes)
            except CloudShellAPIError as e:
                if e.code == CloudshellAPIErrorCodes.UNABLE_TO_LOCATE_FAMILY_OR_MODEL:
                    entry.comment = "Shell {} is not installed".format(first_gen["driver_name"])
                else:
                    raise
            else:
                cs_session.AutoLoad(resource_name)
