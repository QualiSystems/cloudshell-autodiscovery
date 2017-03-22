import re

from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.api.common_cloudshell_api import CloudShellAPIError
from cloudshell.snmp.quali_snmp import QualiSnmp
from cloudshell.snmp.snmp_parameters import SNMPV2Parameters

from autodiscovery.common.consts import CloudshellAPIErrorCodes
from autodiscovery.exceptions import AutoDiscoveryException
from autodiscovery.exceptions import ReportableException
from autodiscovery.handlers import NetworkingTypeHandler
from autodiscovery.handlers import Layer1TypeHandler
from autodiscovery.handlers import TrafficGeneratorTypeHandler
from autodiscovery.handlers import PDUTypeHandler


class AbstractRunCommand(object):

    def __init__(self, data_processor, report, logger):
        """

        :param autodiscovery.data_processors.JsonDataProcessor data_processor:
        :param autodiscovery.reports.AbstractReport report:
        :param logging.Logger logger:
        """
        self.data_processor = data_processor
        self.report = report
        self.logger = logger

        self.vendor_type_handlers_map = {
            "networking": NetworkingTypeHandler(logger=logger),
            "layer1": Layer1TypeHandler(logger=logger),
            "traffic_generator": TrafficGeneratorTypeHandler(logger=logger),
            "pdu": PDUTypeHandler(logger=logger),
        }

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

    def execute(self, *args, **kwargs):
        raise NotImplementedError("Class {} must implement method 'execute'".format(type(self)))


class RunCommand(AbstractRunCommand):
    def __init__(self, data_processor, report, logger, offline):
        """

        :param autodiscovery.data_processors.JsonDataProcessor data_processor:
        :param autodiscovery.reports.AbstractReport report:
        :param logging.Logger logger:
        :param bool offline:
        """
        super(RunCommand, self).__init__(data_processor, report, logger)
        self.offline = offline

    def _parse_vendor_number(self, sys_obj_id):
        """Get device vendor number from SNMPv2 mib

        :param: str sys_obj_id:
        :return: device vendor number
        :rtype: str
        """
        match_name = re.search(r'::enterprises\.(?P<vendor>[0-9]*)\..*$', sys_obj_id)
        if match_name:
            return match_name.group("vendor")

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

    def _discover_device(self, entry, snmp_comunity_strings):
        """Discover device attributes via SNMP

        :param autodiscovery.reports.base.Entry entry:
        :param list snmp_comunity_strings: list of possible SNMP read community strings for the given devices
        :rtype: autodiscovery.reports.base.Entry
        """
        snmp_handler, snmp_community = self._get_snmp_handler(device_ip=entry.ip,
                                                              snmp_comunity_strings=snmp_comunity_strings)
        # set valid SNMP string to be first in the list
        snmp_comunity_strings.remove(snmp_community)
        snmp_comunity_strings.insert(0, snmp_community)

        vendor_enterprise_numbers = self.data_processor.load_vendor_enterprise_numbers()
        entry.snmp_community = snmp_community
        entry.sys_object_id = snmp_handler.get_property('SNMPv2-MIB', 'sysObjectID', '0')
        entry.description = snmp_handler.get_property('SNMPv2-MIB', 'sysDescr', '0')
        entry.device_name = snmp_handler.get_property('SNMPv2-MIB', 'sysName', '0')
        vendor_number = self._parse_vendor_number(entry.sys_object_id)
        entry.vendor = vendor_enterprise_numbers[vendor_number]

        return entry

    def execute(self, devices_ips, snmp_comunity_strings, cli_credentials, cs_ip, cs_user, cs_password,
                additional_vendors_data):
        """Execute Auto-discovery command

        :param list devices_ips: list of devices IPs to discover
        :param list snmp_comunity_strings: list of possible SNMP read community strings for the given devices
        :param autodiscovery.models.vendor.CLICredentialsCollection cli_credentials:  possible CLI credentials
        :param str cs_ip: IP address of the CloudShell API
        :param str cs_user: user for the CloudShell API
        :param str cs_password: password for the CloudShell API
        :param list[dict] additional_vendors_data: additional vendors configuration
        :return:
        """
        vendor_config = self.data_processor.load_vendor_config(additional_vendors_data=additional_vendors_data)

        if not self.offline:
            self._init_cs_session(cs_ip=cs_ip, cs_user=cs_user, cs_password=cs_password)

        for device_ip in devices_ips:
            self.logger.info("Discovering device with IP {}".format(device_ip))
            try:
                with self.report.add_entry(ip=device_ip, offline=self.offline) as entry:
                    entry = self._discover_device(entry=entry, snmp_comunity_strings=snmp_comunity_strings)
                    vendor = vendor_config.get_vendor(vendor_name=entry.vendor)

                    if vendor is None:
                        raise ReportableException("Unsupported vendor {}".format(entry.vendor))

                    try:
                        handler = self.vendor_type_handlers_map[vendor.vendor_type.lower()]
                    except KeyError:
                        raise ReportableException(
                            "Invalid vendor type '{}'. Possible values are: {}".format(
                                vendor.vendor_type, self.vendor_type_handlers_map.keys()))

                    discovered_entry = handler.discover(entry=entry, vendor=vendor, cli_credentials=cli_credentials)

                    if not self.offline:
                        handler.upload(entry=discovered_entry, vendor=vendor, cs_session=self.cs_session)

            except Exception:
                self.logger.exception("Failed to discover {} device due to:".format(device_ip))
            else:
                self.logger.info("Device with IP {} was successfully discovered".format(device_ip))

        self.report.generate()
