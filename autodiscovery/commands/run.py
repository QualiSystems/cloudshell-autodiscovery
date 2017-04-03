import re
import uuid

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
from autodiscovery.output import EmptyOutput


class AbstractRunCommand(object):

    def __init__(self, data_processor, report, logger, output=None, autoload=True):
        """

        :param autodiscovery.data_processors.JsonDataProcessor data_processor:
        :param autodiscovery.reports.AbstractReport report:
        :param logging.Logger logger:
        :param autodiscovery.output.AbstractOutput output:
        :param bool autoload:
        """
        self.data_processor = data_processor
        self.report = report
        self.logger = logger

        if output is None:
            output = EmptyOutput()
        self.output = output

        self.vendor_type_handlers_map = {
            "networking": NetworkingTypeHandler(logger=logger, autoload=autoload),
            "layer1": Layer1TypeHandler(logger=logger, autoload=autoload),
            "traffic_generator": TrafficGeneratorTypeHandler(logger=logger, autoload=autoload),
            "pdu": PDUTypeHandler(logger=logger, autoload=autoload),
        }
        self._cs_sessions = {}

    def _init_cs_session(self, cs_ip, cs_user, cs_password, cs_domain):
        """Initialize CloudShell session

        :param str cs_ip:
        :param str cs_user:
        :param str cs_password:
        :rtype: CloudShellAPISession
        """
        try:
            cs_session = CloudShellAPISession(host=cs_ip, username=cs_user, password=cs_password, domain=cs_domain)
        except CloudShellAPIError as e:
            if e.code in (CloudshellAPIErrorCodes.INCORRECT_LOGIN, CloudshellAPIErrorCodes.INCORRECT_PASSWORD):
                self.logger.exception("Unable to login to the CloudShell API")
                raise AutoDiscoveryException("Wrong CloudShell user/password")
            raise
        except Exception:
            self.logger.exception("Unable to connect to the CloudShell API")
            raise AutoDiscoveryException("CloudShell server is unreachable")

        return cs_session

    def _get_cs_session(self, cs_ip, cs_user, cs_password, cs_domain):
        """

        :param cs_ip:
        :param cs_user:
        :param cs_password:
        :param cs_domain:
        :return:
        """
        if cs_domain not in self._cs_sessions:
            cs_session = self._init_cs_session(cs_ip=cs_ip,
                                               cs_user=cs_user,
                                               cs_password=cs_password,
                                               cs_domain=cs_domain)

            self._cs_sessions[cs_domain] = cs_session

        return self._cs_sessions[cs_domain]

    def execute(self, *args, **kwargs):
        raise NotImplementedError("Class {} must implement method 'execute'".format(type(self)))


class RunCommand(AbstractRunCommand):
    def __init__(self, data_processor, report, logger, output=None, autoload=True, offline=False):
        """

        :param autodiscovery.data_processors.JsonDataProcessor data_processor:
        :param autodiscovery.reports.AbstractReport report:
        :param logging.Logger logger:
        :param autodiscovery.output.AbstractOutput output:
        :param bool autoload:
        :param bool offline:
        """
        super(RunCommand, self).__init__(data_processor, report, logger, output, autoload)
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

    def _generate_device_name(self, vendor_name):
        """Generate name for the device model on CloudShell based on vendor name

        :param str vendor_name:
        :rtype: str
        """
        vendor_name = re.sub("[^a-zA-Z0-9 .-]", "", vendor_name)
        return "{}-{}".format(vendor_name, uuid.uuid4())

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
        vendor_number = self._parse_vendor_number(entry.sys_object_id)
        entry.vendor = vendor_enterprise_numbers[vendor_number]
        entry.description = snmp_handler.get_property('SNMPv2-MIB', 'sysDescr', '0')
        sys_name = snmp_handler.get_property('SNMPv2-MIB', 'sysName', '0')

        if not sys_name:
            sys_name = self._generate_device_name(vendor_name=entry.vendor)

        entry.device_name = sys_name
        return entry

    def execute(self, devices_ips, snmp_comunity_strings, vendor_settings, cs_ip, cs_user, cs_password,
                additional_vendors_data):
        """Execute Auto-discovery command

        :param list[autodiscovery.models.DeviceIPRange] devices_ips: list of devices IPs to discover
        :param list snmp_comunity_strings: list of possible SNMP read community strings for the given devices
        :param autodiscovery.models.vendor.VendorSettingsCollection vendor_settings: additional vendor settings
        :param str cs_ip: IP address of the CloudShell API
        :param str cs_user: user for the CloudShell API
        :param str cs_password: password for the CloudShell API
        :param list[dict] additional_vendors_data: additional vendors configuration
        :return:
        """
        vendor_config = self.data_processor.load_vendor_config(additional_vendors_data=additional_vendors_data)

        for devices_ip_range in devices_ips:
            cs_domain = devices_ip_range.domain
            for device_ip in devices_ip_range.ip_range:
                self.logger.info("Discovering device with IP {}".format(device_ip))
                self.output.send("Discovering device with IP {}".format(device_ip))
                try:
                    with self.report.add_entry(ip=device_ip, domain=cs_domain, offline=self.offline) as entry:
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

                        discovered_entry = handler.discover(entry=entry, vendor=vendor, vendor_settings=vendor_settings)

                        if not self.offline:
                            cs_session = self._get_cs_session(cs_ip=cs_ip,
                                                              cs_user=cs_user,
                                                              cs_password=cs_password,
                                                              cs_domain=cs_domain)

                            handler.upload(entry=discovered_entry, vendor=vendor, cs_session=cs_session)
                except Exception:
                    entry = self.report.get_current_entry()
                    comment = entry.comment if entry is not None else ""
                    self.output.send("Failed to discover {} device. {}".format(device_ip, comment), error=True)
                    self.logger.exception("Failed to discover {} device due to:".format(device_ip))
                else:
                    self.output.send("Device with IP {} was successfully discovered".format(device_ip))
                    self.logger.info("Device with IP {} was successfully discovered".format(device_ip))

        self.report.generate()
