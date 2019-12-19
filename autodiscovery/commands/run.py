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
        raise NotImplementedError(f"Class {type(self)} must implement method 'execute'")


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

    def _get_valid_snmp_params(self, snmp_community, ip_address):
        """Check if SNMP community string is correct and working.

        :param str snmp_community:
        :param str ip_address:
        """
        snmp_parameters = SNMPReadParameters(
            ip=ip_address, snmp_community=snmp_community
        )

        with Snmp().get_snmp_service(
            snmp_parameters=snmp_parameters, logger=self.logger
        ) as snmp:
            try:
                snmp.get(SnmpMibObject("SNMPv2-MIB", "sysDescr", "0"))
            except Exception:
                self.logger.warning(
                    f"SNMP Community string '{snmp_community}' is not valid for "
                    f"device with IP {ip_address}"
                )
                return

        return snmp_parameters

    def _get_snmp_service(self, device_ip, snmp_comunity_strings):
        """Get SNMP Service and valid community string for the device.

        :param str device_ip:
        :param list[str] snmp_comunity_strings:
        :return: tuple with Snmp instance and valid SNMP community string
        :rtype: (Snmp, str)
        """
        for snmp_community in snmp_comunity_strings:
            self.logger.info(
                f"Trying community string '{snmp_community}' "
                f"for device with IP {device_ip}"
            )

            snmp_params = self._get_valid_snmp_params(
                ip_address=device_ip, snmp_community=snmp_community
            )

            if snmp_params is not None:
                # need to return new instance, otherwise it will not work
                return (
                    Snmp().get_snmp_service(
                        snmp_parameters=snmp_params, logger=self.logger
                    ),
                    snmp_community,
                )

        raise ReportableException("SNMP timeout - no resource detected")

    def _generate_device_name(self, vendor_name):
        """Generate name for the device model on CloudShell based on vendor name.

        :param str vendor_name:
        :rtype: str
        """
        vendor_name = re.sub("[^a-zA-Z0-9 .-]", "", vendor_name)
        return f"{vendor_name}-{uuid.uuid4()}"

    def _discover_device(self, entry, snmp_comunity_strings):
        """Discover device attributes via SNMP.

        :param autodiscovery.reports.base.Entry entry:
        :param snmp_comunity_strings: list of possible SNMP strings
        :type snmp_comunity_strings: list
        :rtype: autodiscovery.reports.base.Entry
        """
        snmp_service, snmp_community = self._get_snmp_service(
            device_ip=entry.ip, snmp_comunity_strings=snmp_comunity_strings
        )
        # set valid SNMP string to be first in the list
        snmp_comunity_strings.remove(snmp_community)
        snmp_comunity_strings.insert(0, snmp_community)

        vendor_enterprise_numbers = self.data_processor.load_vendor_enterprise_numbers()
        entry.snmp_community = snmp_community

        with snmp_service as snmp:
            entry.sys_object_id = snmp.get_property(
                SnmpMibObject("SNMPv2-MIB", "sysObjectID", "0")
            ).safe_value

            entry.description = snmp.get_property(
                SnmpMibObject("SNMPv2-MIB", "sysDescr", "0")
            ).safe_value

            sys_name = snmp.get_property(
                SnmpMibObject("SNMPv2-MIB", "sysName", "0")
            ).safe_value

        vendor_number = self._parse_vendor_number(entry.sys_object_id)
        entry.vendor = vendor_enterprise_numbers[vendor_number]

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
                msg = f"Discovering device with IP {device_ip}"
                self.logger.info(msg)
                self.output.send(msg)
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
                                f"Unsupported vendor {entry.vendor}"
                            )

                        try:
                            handler = self.vendor_type_handlers_map[
                                vendor.vendor_type.lower()
                            ]
                        except KeyError:
                            raise ReportableException(
                                f"Invalid vendor type '{vendor.vendor_type}'. Possible "
                                f"values are: {self.vendor_type_handlers_map.keys()}"
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
                        f"Failed to discover {device_ip} device. {str(e)}", error=True
                    )
                    self.logger.exception(
                        f"Failed to discover {device_ip} device due to:"
                    )

                except Exception:
                    self.output.send(
                        f"Failed to discover {device_ip} device. See log for details",
                        error=True,
                    )
                    self.logger.exception(
                        f"Failed to discover {device_ip} device due to:"
                    )

                else:
                    self.output.send(
                        f"Device with IP {device_ip} was successfully discovered"
                    )
                    self.logger.info(
                        f"Device with IP {device_ip} was successfully discovered"
                    )

        self.report.generate()
