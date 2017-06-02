from cloudshell.api.cloudshell_api import AttributeNameValue
from cloudshell.api.cloudshell_api import ResourceAttributesUpdateRequest
from cloudshell.api.common_cloudshell_api import CloudShellAPIError

from autodiscovery.cli_sessions import SSHDiscoverySession
from autodiscovery.cli_sessions import TelnetDiscoverySession
from autodiscovery.common.consts import CloudshellAPIErrorCodes
from autodiscovery.exceptions import ReportableException


class AbstractHandler(object):
    def __init__(self, logger, autoload):
        """

        :param logging.Logger logger:
        :param bool autoload:
        """
        self.logger = logger
        self.autoload = autoload

    def discover(self, entry, vendor, vendor_settings):
        """Discover device attributes

        :param autodiscovery.reports.base.Entry entry:
        :param autodiscovery.models.vendor.BaseVendorDefinition vendor:
        :param autodiscovery.models.VendorSettingsCollection vendor_settings:
        :rtype: autodiscovery.reports.base.Entry
        """
        raise NotImplementedError("Class {} must implement method 'discover'".format(type(self)))

    def upload(self, entry, vendor, cs_session):
        """Upload discovered device on the CloudShell

        :param autodiscovery.reports.base.Entry entry:
        :param autodiscovery.models.vendor.BaseVendorDefinition vendor:
        :param cloudshell.api.cloudshell_api.CloudShellAPISession cs_session:
        :return:
        """
        raise NotImplementedError("Class {} must implement method 'upload'".format(type(self)))

    def _get_cli_credentials(self, vendor, vendor_settings, device_ip):
        """

        :param autodiscovery.models.VendorDefinition vendor:
        :param autodiscovery.models.VendorSettingsCollection vendor_settings:
        :param str device_ip:
        :return:
        """
        vendor_cli_creds = vendor_settings.get_creds_by_vendor(vendor)

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

    def _add_resource_driver(self, cs_session, resource_name, driver_name):
        """Add appropriate driver to the created CloudShell resource

        :param cloudshell.api.cloudshell_api.CloudShellAPISession cs_session:
        :param str resource_name:
        :param str driver_name:
        :return:
        """
        try:
            cs_session.UpdateResourceDriver(resourceFullPath=resource_name,
                                            driverName=driver_name)
        except CloudShellAPIError as e:
            if e.code == CloudshellAPIErrorCodes.UNABLE_TO_LOCATE_DRIVER:
                self.logger.exception("Unable to locate driver {}".format(driver_name))
                raise ReportableException("Shell {} is not installed on the CloudShell".format(driver_name))
            raise

    def _create_cs_resource(self, cs_session, resource_name, resource_family, resource_model, device_ip, folder_path):
        """Create Resource on CloudShell with appropriate attributes

        :param cloudshell.api.cloudshell_api.CloudShellAPISession cs_session:
        :param str resource_name:
        :param str resource_family:
        :param str resource_model:
        :param str device_ip:
        :param str folder_path:
        :return: name for the created Resource
        :rtype: str
        """
        try:
            cs_session.CreateResource(resourceFamily=resource_family,
                                      resourceModel=resource_model,
                                      resourceName=resource_name,
                                      resourceAddress=device_ip,
                                      folderFullPath=folder_path)
        except CloudShellAPIError as e:
            if e.code == CloudshellAPIErrorCodes.RESOURCE_ALREADY_EXISTS:
                resource_name = "{}-1".format(resource_name)
                cs_session.CreateResource(resourceFamily=resource_family,
                                          resourceModel=resource_model,
                                          resourceName=resource_name,
                                          resourceAddress=device_ip,
                                          folderFullPath=folder_path)
            else:
                self.logger.exception("Unable to locate Shell with Resource Family/Name: {}/{}"
                                      .format(resource_family, resource_model))
                raise

        return resource_name

    def _upload_resource(self, cs_session, entry, resource_family, resource_model, driver_name, attribute_prefix=""):
        """

        :param cs_session:
        :param entry:
        :param resource_family:
        :param resource_model:
        :param driver_name:
        :param attribute_prefix:
        :return:
        """
        if entry.folder_path != "":
            # create folder before uploading resource. If folder was already created it will return successful result
            cs_session.CreateFolder(folderFullPath=entry.folder_path)

        try:
            resource_name = self._create_cs_resource(cs_session=cs_session,
                                                     resource_name=entry.device_name,
                                                     resource_family=resource_family,
                                                     resource_model=resource_model,
                                                     device_ip=entry.ip,
                                                     folder_path=entry.folder_path)
        except CloudShellAPIError as e:
            if e.code == CloudshellAPIErrorCodes.UNABLE_TO_LOCATE_FAMILY_OR_MODEL:
                return
            else:
                raise

        self.logger.info("Adding attributes to the resource {}".format(resource_name))
        attributes = [AttributeNameValue("{}{}".format(attribute_prefix, key), value)
                      for key, value in entry.attributes.iteritems()]

        cs_session.SetAttributesValues([ResourceAttributesUpdateRequest(resource_name, attributes)])

        self.logger.info("Attaching driver to the resource {}".format(resource_name))
        self._add_resource_driver(cs_session=cs_session,
                                  resource_name=resource_name,
                                  driver_name=driver_name)

        if self.autoload:
            self.logger.info("Autoloading resource {}".format(resource_name))
            cs_session.AutoLoad(resource_name)

        return resource_name
