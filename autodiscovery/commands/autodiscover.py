import re

from cloudshell.api.cloudshell_api import AttributeNameValue
from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.api.cloudshell_api import ResourceAttributesUpdateRequest
from cloudshell.api.common_cloudshell_api import CloudShellAPIError
from cloudshell.snmp.quali_snmp import QualiSnmp
from cloudshell.snmp.snmp_parameters import SNMPV2Parameters

from autodiscovery.exceptions import AutoDiscoveryException
from autodiscovery.exceptions import ReportableException
from autodiscovery.cli_sessions import TelnetDiscoverySession
from autodiscovery.cli_sessions import SSHDiscoverySession


class ResourceModelsAttributes(object):
    """Container for the CloudShell Resource Model Attributes names"""
    ENABLE_SNMP = "Enable SNMP"
    SNMP_READ_COMMUNITY = "SNMP Read Community"
    USER = "User"
    PASSWORD = "Password"
    ENABLE_PASSWORD = "Enable Password"


class CloudshellAPIErrorCodes(object):
    """Container for the CloudShell API error codes"""
    RESOURCE_ALREADY_EXISTS = "114"
    UNABLE_TO_LOCATE_DRIVER = "129"


class AutoDiscoverCommand(object):
    def __init__(self, data_processor, report, logger):
        """

        :param autodiscovery.data_processors.JsonDataProcessor data_processor:
        :param autodiscovery.reports.ConsoleReport report:
        :param logging.Logger logger:
        """
        self.data_processor = data_processor
        self.report = report
        self.logger = logger

        self.vendor_type_handlers_map = {
            "networking": self._networking_type_handler,
            "layer1": self._layer1_type_handler,
            "traffic_generator": self._traffic_generator_type_handler,
            "pdu": self._pdu_type_handler,
        }

    def _parse_vendor_number(self, sys_obj_id):
        """Get device vendor number from SNMPv2 mib

        :param: str sys_obj_id:
        :return: device vendor number
        :rtype: str
        """
        match_name = re.search(r'::enterprises\.(?P<vendor>[0-9]*)\..*$', sys_obj_id)
        if match_name:
            return match_name.group("vendor")

    def _pdu_type_handler(self, cs_session, device_ip, resource_name, vendor, system_description,
                          snmp_community_string, cli_credentials):
        """

        :param CloudShellAPISession cs_session:
        :param str device_ip:
        :param str resource_name:
        :param autodiscovery.models.VendorDefinition vendor:
        :param str system_description:
        :param str snmp_community_string:
        :param autodiscovery.models.CLICredentialsCollection cli_credentials:
        :return:
        """
        pass

    def _traffic_generator_type_handler(self, cs_session, device_ip, resource_name, vendor, system_description,
                                        snmp_community_string, cli_credentials):
        """

        :param CloudShellAPISession cs_session:
        :param str device_ip:
        :param str resource_name:
        :param autodiscovery.models.VendorDefinition vendor:
        :param str system_description:
        :param str snmp_community_string:
        :param autodiscovery.models.CLICredentialsCollection cli_credentials:
        :return:
        """
        pass

    def _layer1_type_handler(self, cs_session, device_ip, resource_name, vendor, system_description,
                             snmp_community_string, cli_credentials):
        """

        :param CloudShellAPISession cs_session:
        :param str device_ip:
        :param str resource_name:
        :param autodiscovery.models.VendorDefinition vendor:
        :param str system_description:
        :param str snmp_community_string:
        :param autodiscovery.models.CLICredentialsCollection cli_credentials:
        :return:
        """
        pass

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

                    vendor_cli_creds.update_valid_creds(valid_creds)
                    return valid_creds

                except Exception:
                    self.logger.warning("{} Credentials aren't valid for the device with IP {}"
                                        .format(session.SESSION_TYPE, device_ip), exc_info=True)

    def _networking_type_handler(self, cs_session, device_ip, resource_name, vendor, system_description,
                                 snmp_community_string, cli_credentials):
        """

        :param CloudShellAPISession cs_session:
        :param str device_ip:
        :param str resource_name:
        :param autodiscovery.models.VendorDefinition vendor:
        :param str system_description:
        :param str snmp_community_string:
        :param autodiscovery.models.CLICredentialsCollection cli_credentials:
        :return:
        """
        device_os = vendor.get_device_os(system_description)
        if device_os is None:
            raise ReportableException("Unable to determine device OS")

        model_type = device_os.get_device_model_type(system_description=system_description)
        if model_type is None:
            raise ReportableException("Unable to determine device model type")

        resource_family = device_os.get_resource_family(model_type)
        resource_model = device_os.get_resource_model(model_type)

        attributes = {
            ResourceModelsAttributes.SNMP_READ_COMMUNITY: snmp_community_string,
            ResourceModelsAttributes.ENABLE_SNMP: "False"
        }

        cli_creds = self._get_cli_credentials(vendor=vendor,
                                              cli_credentials=cli_credentials,
                                              device_ip=device_ip)

        if cli_creds is None:
            entry = self.report.get_current_entry()
            entry.comment = "Unable to discover device user/password"
        else:
            if cli_creds.user is not None:
                attributes[ResourceModelsAttributes.USER] = cli_creds.user
            if cli_creds.password is not None:
                attributes[ResourceModelsAttributes.PASSWORD] = cli_creds.password
            if cli_creds.enable_password is not None:
                attributes[ResourceModelsAttributes.ENABLE_PASSWORD] = cli_creds.enable_password

        try:
            resource_name = self._create_cs_resource(cs_session=cs_session,
                                                     device_ip=device_ip,
                                                     resource_family=resource_family,
                                                     resource_model=resource_model,
                                                     resource_name=resource_name,
                                                     attributes=attributes)
        except CloudShellAPIError:
            raise ReportableException("Shell '{}' not installed".format(device_os.get_driver_name_2nd_gen(model_type)))

        self._add_resource_driver(cs_session=cs_session,
                                  resource_name=resource_name,
                                  device_os=device_os,
                                  model_type=model_type)

        cs_session.AutoLoad(resource_name)

    def _add_resource_driver(self, cs_session, resource_name, device_os, model_type):
        """Add appropriate driver to the created CloudShell resource

        :param CloudShellAPISession cs_session:
        :param str resource_name:
        :param autodiscovery.models.OperationSystem device_os:
        :param str model_type:
        :return:
        """
        for driver_name in (device_os.get_driver_name_2nd_gen(model_type), device_os.get_driver_name_1st_gen()):
            try:
                cs_session.UpdateResourceDriver(resourceFullPath=resource_name,
                                                driverName=driver_name)
            except CloudShellAPIError as e:
                if e.code == CloudshellAPIErrorCodes.UNABLE_TO_LOCATE_DRIVER:
                    continue
            else:
                return

        raise ReportableException("Shell {} is not installed on the CloudShell".format(
            device_os.get_driver_name_2nd_gen(model_type)))

    def _get_snmp_handler(self, device_ip, snmp_comunity_strings):
        """Get SNMP Handler and valid community string for the device

        :param str device_ip:
        :param list[str] snmp_comunity_strings:
        :return: tuple with QualiSnmp instance and valid SNMP community string
        :rtype: (QualiSnmp, str)
        """
        for snmp_community in snmp_comunity_strings:
            self.logger.info("Trying community string '{}' for device with IP {}".format(snmp_community, device_ip))
            snmp_parameters = SNMPV2Parameters(ip=device_ip, snmp_community=snmp_community)

            try:
                return QualiSnmp(snmp_parameters, self.logger), snmp_community
            except Exception:
                self.logger.warning("SNMP Community string '{}' is not valid for device with IP {}"
                                    .format(snmp_community, device_ip))

        raise ReportableException("SNMP timeout - no resource detected")

    def _create_cs_resource(self, cs_session, device_ip, resource_family, resource_model,
                            resource_name, attributes):
        """Create Resource on CloudShell with appropriate attributes

        :param CloudShellAPISession cs_session:
        :param str device_ip:
        :param str resource_family:
        :param str resource_model:
        :param str resource_name:
        :param dict attributes:
        :return: name for the created Resource
        :rtype: str
        """
        try:
            cs_session.CreateResource(resourceFamily=resource_family,
                                      resourceModel=resource_model,
                                      resourceName=resource_name,
                                      resourceAddress=device_ip)
        except CloudShellAPIError as e:
            if e.code == CloudshellAPIErrorCodes.RESOURCE_ALREADY_EXISTS:
                resource_name = "{}-1".format(resource_name)
                cs_session.CreateResource(resourceFamily=resource_family,
                                          resourceModel=resource_model,
                                          resourceName=resource_name,
                                          resourceAddress=device_ip)
            else:
                raise

        attributes = [AttributeNameValue(key, value) for key, value in attributes.iteritems()]
        cs_session.SetAttributesValues([ResourceAttributesUpdateRequest(resource_name, attributes)])

        return resource_name

    def execute(self, devices_ips, snmp_comunity_strings, cli_credentials, cs_ip, cs_user, cs_password,
                additional_vendors_data):
        """Execute Auto-discovery command

        :param list devices_ips: list of devices IPs to discover
        :param list snmp_comunity_strings: list of possible SNMP read community strings for the given devices
        :param dict cli_credentials: dict of possible CLI credentials to the device {"username": "password"}
        :param str cs_ip: IP address of the CloudShell API
        :param str cs_user: user for the CloudShell API
        :param str cs_password: password for the CloudShell API
        :param list[dict] additional_vendors_data: additional vendors configuration
        :return:
        """
        vendor_config = self.data_processor.load_vendor_config(additional_vendors_data=additional_vendors_data)
        vendor_enterprise_numbers = self.data_processor.load_vendor_enterprise_numbers()

        try:
            cs_session = CloudShellAPISession(host=cs_ip, username=cs_user, password=cs_password)
        except Exception:  # TODO: handle both cases
            # 1) cloudshell server unreachable
            # 2) wrong cloudshell user/pass
            self.logger.exception("Unable to connect to the CloudShell API")
            raise AutoDiscoveryException("CloudShell server is unreachable")

        for device_ip in devices_ips:
            try:
                with self.report.add_entry(ip=device_ip) as entry:
                    snmp_handler, snmp_community = self._get_snmp_handler(device_ip=device_ip,
                                                                          snmp_comunity_strings=snmp_comunity_strings)
                    # set valid SNMP string to be first in the list
                    snmp_comunity_strings.remove(snmp_community)
                    snmp_comunity_strings.insert(0, snmp_community)

                    sys_obj_id = snmp_handler.get_property('SNMPv2-MIB', 'sysObjectID', '0')
                    entry.sys_object_id = sys_obj_id
                    system_description = snmp_handler.get_property('SNMPv2-MIB', 'sysDescr', '0')
                    entry.description = system_description
                    resource_name = snmp_handler.get_property('SNMPv2-MIB', 'sysName', '0')
                    vendor_number = self._parse_vendor_number(sys_obj_id)
                    vendor_name = vendor_enterprise_numbers[vendor_number]
                    entry.vendor = vendor_name
                    vendor = vendor_config.get_vendor(vendor_name=vendor_name)

                    if vendor is None:
                        raise ReportableException("Unsupported vendor {}".format(vendor_name))

                    try:
                        handler = self.vendor_type_handlers_map[vendor.vendor_type.lower()]
                    except KeyError:
                        raise ReportableException("Invalid vendor type '{}'. Possible values are: {}"
                                                  .format(vendor.vendor_type, self.vendor_type_handlers_map.keys()))
                    handler(cs_session=cs_session,
                            device_ip=device_ip,
                            resource_name=resource_name,
                            vendor=vendor,
                            system_description=system_description,
                            snmp_community_string=snmp_community,
                            cli_credentials=cli_credentials)

            except Exception:
                self.logger.exception("Failed to discover {} device due to:".format(device_ip))

        self.report.generate()
