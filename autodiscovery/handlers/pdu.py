from autodiscovery.common.async_cloudshell_api import AsyncCloudShellAPISession
from autodiscovery.common.consts import ResourceModelsAttributes
from autodiscovery.exceptions import ReportableException
from autodiscovery.handlers.base import AbstractHandler
from autodiscovery.models import PDUVendorDefinition
from autodiscovery.reports.discovery.base import Entry


class PDUTypeHandler(AbstractHandler):
    def discover(self, entry, vendor, vendor_settings):
        """Discover device attributes.

        :param autodiscovery.reports.base.Entry entry:
        :param autodiscovery.models.vendor.PDUVendorDefinition vendor:
        :param autodiscovery.models.VendorSettingsCollection vendor_settings:
        :rtype: autodiscovery.reports.base.Entry
        """
        cli_creds = self._get_cli_credentials(
            vendor=vendor, vendor_settings=vendor_settings, device_ip=entry.ip
        )
        if cli_creds is None:
            entry.comment = "Unable to discover device user/password"
        else:
            entry.add_attribute(ResourceModelsAttributes.USER, entry.user)
            entry.add_attribute(ResourceModelsAttributes.PASSWORD, entry.password)

        return entry

    async def upload(
        self,
        entry: Entry,
        vendor: PDUVendorDefinition,
        cs_session: AsyncCloudShellAPISession,
    ):
        """Upload discovered device on the CloudShell."""
        resource_name = await self._upload_resource(
            cs_session=cs_session,
            entry=entry,
            resource_family=vendor.family_name,
            resource_model=vendor.model_name,
            driver_name=vendor.driver_name,
        )

        if not resource_name:
            raise ReportableException(f"Shell {vendor.driver_name} is not installed")
