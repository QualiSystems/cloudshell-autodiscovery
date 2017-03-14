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
    ENABLE_SNMP = "Enable SNMP"  # 2 Generation shells contains model name prefix for all attributes
    SNMP_READ_COMMUNITY = "SNMP Read Community"
    USER = "User"
    PASSWORD = "Password"
    ENABLE_PASSWORD = "Enable Password"


class CloudshellAPIErrorCodes(object):
    """Container for the CloudShell API error codes"""
    INCORRECT_LOGIN = "100"
    INCORRECT_PASSWORD = "118"
    RESOURCE_ALREADY_EXISTS = "114"
    UNABLE_TO_LOCATE_DRIVER = "129"
    UNABLE_TO_LOCATE_FAMILY_OR_MODEL = "100"  # not a typo, same code as for incorrect login


class AutoDiscoverCommand(object):
    def __init__(self, data_processor, report, offline, logger):
        """

        :param autodiscovery.data_processors.JsonDataProcessor data_processor:
        :param autodiscovery.reports.AbstractReport report:
        :param bool offline:
        :param logging.Logger logger:
        """
        self.data_processor = data_processor
        self.report = report
        self.logger = logger
        self.offline = offline
        self.cs_session = None

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

    def _pdu_type_handler(self, device_ip, resource_name, vendor, system_description,
                          snmp_community_string, cli_credentials):
        """

        :param str device_ip:
        :param str resource_name:
        :param autodiscovery.models.VendorDefinition vendor:
        :param str system_description:
        :param str snmp_community_string:
        :param autodiscovery.models.CLICredentialsCollection cli_credentials:
        :return:
        """
        pass

    def _traffic_generator_type_handler(self, device_ip, resource_name, vendor, system_description,
                                        snmp_community_string, cli_credentials):
        """

        :param str device_ip:
        :param str resource_name:
        :param autodiscovery.models.VendorDefinition vendor:
        :param str system_description:
        :param str snmp_community_string:
        :param autodiscovery.models.CLICredentialsCollection cli_credentials:
        :return:
        """
        pass

    def _layer1_type_handler(self, device_ip, resource_name, vendor, system_description,
                             snmp_community_string, cli_credentials):
        """

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

    def _networking_type_handler(self, device_ip, resource_name, vendor, system_description,
                                 snmp_community_string, cli_credentials):
        """

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
            current_entry = self.report.get_current_entry()
            if cli_creds.user is not None:
                attributes[ResourceModelsAttributes.USER] = cli_creds.user
                current_entry.user = cli_creds.user
            if cli_creds.password is not None:
                attributes[ResourceModelsAttributes.PASSWORD] = cli_creds.password
                current_entry.password = cli_creds.password
            if cli_creds.enable_password is not None:
                attributes[ResourceModelsAttributes.ENABLE_PASSWORD] = cli_creds.enable_password
                current_entry.enable_password = cli_creds.enable_password

        familes_data = device_os.families.get(model_type)

        if "second_gen" in familes_data:
            second_gen = familes_data["second_gen"]
            try:
                resource_name = self._create_cs_resource(resource_name=resource_name,
                                                         resource_family=second_gen["family_name"],
                                                         resource_model=second_gen["model_name"],
                                                         driver_name=second_gen["driver_name"],
                                                         device_ip=device_ip,
                                                         attributes=attributes,
                                                         attribute_prefix="{}.".format(second_gen["model_name"]))
            except CloudShellAPIError as e:
                if e.code == CloudshellAPIErrorCodes.UNABLE_TO_LOCATE_FAMILY_OR_MODEL:
                    if "first_gen" in familes_data:
                        first_gen = familes_data["first_gen"]
                        resource_name = self._create_cs_resource(resource_name=resource_name,
                                                                 resource_family=first_gen["family_name"],
                                                                 resource_model=first_gen["model_name"],
                                                                 driver_name=first_gen["driver_name"],
                                                                 device_ip=device_ip,
                                                                 attributes=attributes,
                                                                 attribute_prefix="")
                    else:
                        raise
                else:
                    raise
        else:
            first_gen = familes_data["first_gen"]
            resource_name = self._create_cs_resource(resource_name=resource_name,
                                                     resource_family=first_gen["family_name"],
                                                     resource_model=first_gen["model_name"],
                                                     driver_name=first_gen["driver_name"],
                                                     device_ip=device_ip,
                                                     attributes=attributes,
                                                     attribute_prefix="")

        self.cs_session.AutoLoad(resource_name)

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

    def _add_resource_driver(self, resource_name, driver_name):
        """Add appropriate driver to the created CloudShell resource

        :param str resource_name:
        :param str driver_name:
        :return:
        """
        try:
            self.cs_session.UpdateResourceDriver(resourceFullPath=resource_name,
                                                 driverName=driver_name)
        except CloudShellAPIError as e:
            if e.code == CloudshellAPIErrorCodes.UNABLE_TO_LOCATE_DRIVER:
                self.logger.exception("Unable to locate driver {}".format(driver_name))
                raise ReportableException("Shell {} is not installed on the CloudShell".format(driver_name))
            raise

    def _create_cs_resource(self, resource_name, resource_family, resource_model, driver_name, device_ip,
                            attributes, attribute_prefix):
        """Create Resource on CloudShell with appropriate attributes

        :param str resource_name:
        :param str resource_family:
        :param str resource_model:
        :param str driver_name:
        :param str device_ip:
        :param dict attributes:
        :param str attribute_prefix:
        :return: name for the created Resource
        :rtype: str
        """
        try:
            self.cs_session.CreateResource(resourceFamily=resource_family,
                                           resourceModel=resource_model,
                                           resourceName=resource_name,
                                           resourceAddress=device_ip)
        except CloudShellAPIError as e:
            if e.code == CloudshellAPIErrorCodes.RESOURCE_ALREADY_EXISTS:
                resource_name = "{}-1".format(resource_name)
                self.cs_session.CreateResource(resourceFamily=resource_family,
                                               resourceModel=resource_model,
                                               resourceName=resource_name,
                                               resourceAddress=device_ip)
            else:
                self.logger.exception("Unable to locate Shell with Resource Family/Name: {}/{}"
                                      .format(resource_family, resource_model))
                raise

        attributes = [AttributeNameValue("{}{}".format(attribute_prefix, key), value)
                      for key, value in attributes.iteritems()]

        self.cs_session.SetAttributesValues([ResourceAttributesUpdateRequest(resource_name, attributes)])

        self._add_resource_driver(resource_name=resource_name,
                                  driver_name=driver_name)

        return resource_name

    def _init_cs_session(self, cs_ip, cs_user, cs_password):
        """Initialize CloudShell session

        :param str cs_ip:
        :param str cs_user:
        :param str cs_password:
        :return:
        """
        try:
            self.cs_session = CloudShellAPISession(host=cs_ip, username=cs_user, password=cs_password)
        except CloudShellAPIError as e:
            if e.code in (CloudshellAPIErrorCodes.INCORRECT_LOGIN, CloudshellAPIErrorCodes.INCORRECT_PASSWORD):
                self.logger.exception("Unable to login to the CloudShell API")
                raise AutoDiscoveryException("Wrong CloudShell user/password")
            raise
        except Exception:
            self.logger.exception("Unable to connect to the CloudShell API")
            raise AutoDiscoveryException("CloudShell server is unreachable")

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

        if not self.offline:
            self._init_cs_session(cs_ip=cs_ip, cs_user=cs_user, cs_password=cs_password)

        for device_ip in devices_ips:
            try:
                with self.report.add_entry(ip=device_ip, offline=self.offline) as entry:
                    snmp_handler, snmp_community = self._get_snmp_handler(device_ip=device_ip,
                                                                          snmp_comunity_strings=snmp_comunity_strings)
                    entry.snmp_community = snmp_community
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
                    handler(device_ip=device_ip,
                            resource_name=resource_name,
                            vendor=vendor,
                            system_description=system_description,
                            snmp_community_string=snmp_community,
                            cli_credentials=cli_credentials)

            except Exception:
                self.logger.exception("Failed to discover {} device due to:".format(device_ip))

        self.report.generate()
