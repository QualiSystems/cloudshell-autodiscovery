from autodiscovery.handlers.base import AbstractHandler

from autodiscovery.common.consts import ResourceModelsAttributes


class PDUTypeHandler(AbstractHandler):

    def discover(self, entry, vendor, cli_credentials):
        """Discover device attributes

        :param autodiscovery.reports.base.Entry entry:
        :param autodiscovery.models.vendor.PDUVendorDefinition vendor:
        :param autodiscovery.models.CLICredentialsCollection cli_credentials:
        :rtype: autodiscovery.reports.base.Entry
        """
        cli_creds = self._get_cli_credentials(vendor=vendor,
                                              cli_credentials=cli_credentials,
                                              device_ip=entry.ip)
        if cli_creds is None:
            entry.comment = "Unable to discover device user/password"
        else:
            entry.user = cli_creds.user
            entry.password = cli_creds.password

        return entry

    def upload(self, entry, vendor, cs_session):
        """Upload discovered device on the CloudShell

        :param autodiscovery.reports.base.Entry entry:
        :param autodiscovery.models.vendor.PDUVendorDefinition vendor:
        :param cloudshell.api.cloudshell_api.CloudShellAPISession cs_session:
        :return:
        """
        attributes = {
            ResourceModelsAttributes.USER: entry.user,
            ResourceModelsAttributes.PASSWORD: entry.password,
        }

        resource_name = self._create_cs_resource(cs_session=cs_session,
                                                 resource_name=entry.device_name,
                                                 resource_family=vendor.family_name,
                                                 resource_model=vendor.model_name,
                                                 driver_name=vendor.driver_name,
                                                 device_ip=entry.ip,
                                                 attributes=attributes)

        cs_session.AutoLoad(resource_name)
