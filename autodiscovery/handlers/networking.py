from autodiscovery.common.consts import ResourceModelsAttributes
from autodiscovery.exceptions import ReportableException
from autodiscovery.handlers.base import AbstractHandler


class NetworkingTypeHandler(AbstractHandler):
    def discover(self, entry, vendor, vendor_settings):
        """Discover device attributes.

        :param autodiscovery.reports.base.Entry entry:
        :param autodiscovery.models.vendor.NetworkingVendorDefinition vendor:
        :param autodiscovery.models.VendorSettingsCollection vendor_settings:
        :rtype: autodiscovery.reports.base.Entry
        """
        device_os = vendor.get_device_os(entry.description)
        if device_os is None:
            raise ReportableException("Unable to determine device OS")

        model_type = device_os.get_device_model_type(
            system_description=entry.description
        )
        if model_type is None:
            raise ReportableException("Unable to determine device model type")

        entry.folder_path = vendor_settings.get_folder_path_by_vendor(vendor)
        entry.model_type = model_type


        cli_creds = self._get_cli_credentials(
            vendor=vendor, vendor_settings=vendor_settings, device_ip=entry.ip
        )

        entry.add_attribute(ResourceModelsAttributes.ENABLE_SNMP, "False")
        entry.add_attribute(
            ResourceModelsAttributes.SNMP_READ_COMMUNITY, entry.snmp_community
        )

        if cli_creds is None:
            entry.comment = "Unable to discover device user/password/enable password"
        else:
            entry.add_attribute(ResourceModelsAttributes.USER, cli_creds.user)
            entry.add_attribute(ResourceModelsAttributes.PASSWORD, cli_creds.password)
            entry.add_attribute(
                ResourceModelsAttributes.ENABLE_PASSWORD, cli_creds.enable_password
            )

        return entry

    async def upload(self, entry, vendor, cs_session):
        """Upload discovered device on the CloudShell.

        :param autodiscovery.reports.base.Entry entry:
        :param autodiscovery.models.vendor.NetworkingVendorDefinition vendor:
        :param autodiscovery.common.async_cloudshell_api.AsyncCloudShellAPISession cs_session:
        :return:
        """
        device_os = vendor.get_device_os(entry.description)
        if device_os is None:
            raise ReportableException("Unable to determine device OS")

        family_data = device_os.families.get(entry.model_type)

        driver_name = family_data["driver_name"]
        resource_name = await self._upload_resource(
            cs_session=cs_session,
            entry=entry,
            resource_family=family_data["family_name"],
            resource_model=family_data["model_name"],
            driver_name=driver_name,
            attribute_prefix=f"{family_data['model_name']}.",
        )

        if not resource_name:
            raise ReportableException(f"Shell {driver_name} is not installed")
