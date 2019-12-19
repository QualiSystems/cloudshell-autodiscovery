import re
import uuid

from cloudshell.snmp.cloudshell_snmp import Snmp
from cloudshell.snmp.core.domain.snmp_oid import SnmpMibObject
from cloudshell.snmp.snmp_parameters import SNMPReadParameters

from autodiscovery.exceptions import ReportableException
from autodiscovery.handlers import (
    Layer1TypeHandler,
    NetworkingTypeHandler,
    PDUTypeHandler,
    TrafficGeneratorTypeHandler,
)
from autodiscovery.output import EmptyOutput


class AbstractRunCommand(object):
    def __init__(
        self,
        data_processor,
        report,
        logger,
        cs_session_manager,
        output=None,
        autoload=True,
    ):
        """Init command.

        :param autodiscovery.data_processors.JsonDataProcessor data_processor:
        :param autodiscovery.reports.discovery.base.AbstractDiscoveryReport report:
        :param logging.Logger logger:
        :param cs_session_manager:
        :param autodiscovery.output.AbstractOutput output:
        :param bool autoload:
        """
        self.data_processor = data_processor
        self.report = report
        self.logger = logger
        self.cs_session_manager = cs_session_manager

        if output is None:
            output = EmptyOutput()
        self.output = output

        self.vendor_type_handlers_map = {
            "networking": NetworkingTypeHandler(logger=logger, autoload=autoload),
            "layer1": Layer1TypeHandler(logger=logger, autoload=autoload),
            "traffic_generator": TrafficGeneratorTypeHandler(
                logger=logger, autoload=autoload
            ),
            "pdu": PDUTypeHandler(logger=logger, autoload=autoload),
        }

    def execute(self, *args, **kwargs):
        raise NotImplementedError(
            "Class {} must implement method 'execute'".format(type(self))
        )


class RunCommand(AbstractRunCommand):
    def __init__(
        self,
        data_processor,
        report,
        logger,
        cs_session_manager,
        output=None,
        autoload=True,
        offline=False,
    ):
        """Init command.

        :param autodiscovery.data_processors.JsonDataProcessor data_processor:
        :param autodiscovery.reports.discovery.base.AbstractDiscoveryReport report:
        :param logging.Logger logger:
        :param autodiscovery.common.cs_session_manager.CloudShellSessionManager cs_session_manager:  # noqa
        :param autodiscovery.output.AbstractOutput output:
        :param bool autoload:
        :param bool offline:
        """
        super(RunCommand, self).__init__(
            data_processor, report, logger, cs_session_manager, output, autoload
        )
        self.offline = offline

    def _parse_vendor_number(self, sys_obj_id):
        """Get device vendor number from SNMPv2 mib.

        :param: str sys_obj_id:
        :return: device vendor number
        :rtype: str
        """
        match_name = re.search(r"::enterprises\.(?P<vendor>[0-9]*)\..*$", sys_obj_id)
        if match_name:
            return match_name.group("vendor")

    def _is_snmp_valid(self, snmp, snmp_community, ip_address):
        """Verify that SNMP credentials are correct and service is working.

        :param cloudshell.snmp.cloudshell_snmp.Snmp snmp:
        :param str snmp_community:
        :param str ip_address:
        """
        try:
            snmp.get(
                SnmpMibObject("SNMPv2-MIB", "sysDescr", "0")
            )
        except Exception:
            self.logger.warning(
                f"SNMP Community string '{snmp_community}' is not valid for "
                f"device with IP {ip_address}"
            )
            return False

        return True

    def _get_snmp_handler(self, device_ip, snmp_comunity_strings):
        """Get SNMP Handler and valid community string for the device.

        :param str device_ip:
        :param list[str] snmp_comunity_strings:
        :return: tuple with Snmp instance and valid SNMP community string
        :rtype: (Snmp, str)
        """
        for snmp_community in snmp_comunity_strings:
            self.logger.info(
                "Trying community string '{}' for device with IP {}".format(
                    snmp_community, device_ip
                )
            )
            snmp_parameters = SNMPReadParameters(
                ip=device_ip, snmp_community=snmp_community
            )

            with Snmp().get_snmp_service(snmp_parameters=snmp_parameters, logger=self.logger) as snmp:
                if self._is_snmp_valid(snmp=snmp, snmp_community=snmp_community, ip_address=device_ip):
                    return snmp, snmp_community

        raise ReportableException("SNMP timeout - no resource detected")

    def _generate_device_name(self, vendor_name):
        """Generate name for the device model on CloudShell based on vendor name.

        :param str vendor_name:
        :rtype: str
        """
        vendor_name = re.sub("[^a-zA-Z0-9 .-]", "", vendor_name)
        return "{}-{}".format(vendor_name, uuid.uuid4())

    def _discover_device(self, entry, snmp_comunity_strings):
        """Discover device attributes via SNMP.

        :param autodiscovery.reports.base.Entry entry:
        :param snmp_comunity_strings: list of possible SNMP strings
        :type snmp_comunity_strings: list
        :rtype: autodiscovery.reports.base.Entry
        """
        snmp_handler, snmp_community = self._get_snmp_handler(
            device_ip=entry.ip, snmp_comunity_strings=snmp_comunity_strings
        )
        # set valid SNMP string to be first in the list
        snmp_comunity_strings.remove(snmp_community)
        snmp_comunity_strings.insert(0, snmp_community)

        vendor_enterprise_numbers = self.data_processor.load_vendor_enterprise_numbers()
        entry.snmp_community = snmp_community

        entry.sys_object_id = snmp_handler.get_property(
            SnmpMibObject("SNMPv2-MIB", "sysObjectID", "0")
        ).safe_value

        vendor_number = self._parse_vendor_number(entry.sys_object_id)
        entry.vendor = vendor_enterprise_numbers[vendor_number]

        entry.description = snmp_handler.get_property(
            SnmpMibObject("SNMPv2-MIB", "sysDescr", "0")
        ).safe_value

        sys_name = snmp_handler.get_property(
            SnmpMibObject("SNMPv2-MIB", "sysName", "0")
        ).safe_value

        if not sys_name:
            sys_name = self._generate_device_name(vendor_name=entry.vendor)

        entry.device_name = sys_name
        return entry

    def execute(
        self,
        devices_ips,
        snmp_comunity_strings,
        vendor_settings,
        additional_vendors_data,
    ):
        """Execute Auto-discovery command.

        :param devices_ips: list of devices IPs to discover
        :type devices_ips: list[autodiscovery.models.DeviceIPRange]
        :param snmp_comunity_strings: list of possible SNMP strings
        :type snmp_comunity_strings: list
        :param vendor_settings: additional vendor settings
        :type vendor_settings: autodiscovery.models.vendor.VendorSettingsCollection
        :param list[dict] additional_vendors_data: additional vendors configuration
        :return:
        """
        vendor_config = self.data_processor.load_vendor_config(
            additional_vendors_data=additional_vendors_data
        )

        for devices_ip_range in devices_ips:
            cs_domain = devices_ip_range.domain
            for device_ip in devices_ip_range.ip_range:
                self.logger.info("Discovering device with IP {}".format(device_ip))
                self.output.send("Discovering device with IP {}".format(device_ip))
                try:
                    with self.report.add_entry(
                        ip=device_ip, domain=cs_domain, offline=self.offline
                    ) as entry:
                        entry = self._discover_device(
                            entry=entry, snmp_comunity_strings=snmp_comunity_strings
                        )
                        vendor = vendor_config.get_vendor(vendor_name=entry.vendor)

                        if vendor is None:
                            raise ReportableException(
                                "Unsupported vendor {}".format(entry.vendor)
                            )

                        try:
                            handler = self.vendor_type_handlers_map[
                                vendor.vendor_type.lower()
                            ]
                        except KeyError:
                            raise ReportableException(
                                "Invalid vendor type '{}'. Possible values "
                                "are: {}".format(
                                    vendor.vendor_type,
                                    self.vendor_type_handlers_map.keys(),
                                )
                            )

                        discovered_entry = handler.discover(
                            entry=entry, vendor=vendor, vendor_settings=vendor_settings
                        )

                        if not self.offline:
                            cs_session = self.cs_session_manager.get_session(
                                cs_domain=cs_domain
                            )
                            handler.upload(
                                entry=discovered_entry,
                                vendor=vendor,
                                cs_session=cs_session,
                            )

                except ReportableException as e:
                    self.output.send(
                        "Failed to discover {} device. {}".format(device_ip, str(e)),
                        error=True,
                    )
                    self.logger.exception(
                        "Failed to discover {} device due to:".format(device_ip)
                    )

                except Exception:
                    self.output.send(
                        "Failed to discover {} device. See log for details".format(
                            device_ip
                        ),
                        error=True,
                    )
                    self.logger.exception(
                        "Failed to discover {} device due to:".format(device_ip)
                    )

                else:
                    self.output.send(
                        "Device with IP {} was successfully discovered".format(
                            device_ip
                        )
                    )
                    self.logger.info(
                        "Device with IP {} was successfully discovered".format(
                            device_ip
                        )
                    )

        self.report.generate()
