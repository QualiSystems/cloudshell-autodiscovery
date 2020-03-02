import asyncio
import re
import uuid

from colorama import Fore
from tqdm import tqdm

from autodiscovery.common.async_snmp import AsyncSNMPService
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
        workers_num,
        output=None,
        autoload=True,
    ):
        """Init command.

        :param autodiscovery.data_processors.JsonDataProcessor data_processor:
        :param autodiscovery.reports.discovery.base.AbstractDiscoveryReport report:
        :param logging.Logger logger:
        :param cs_session_manager:
        :param int workers_num:
        :param autodiscovery.output.AbstractOutput output:
        :param bool autoload:
        """
        self.data_processor = data_processor
        self.report = report
        self.logger = logger
        self.cs_session_manager = cs_session_manager
        self.workers_num = workers_num

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

    async def execute(self, *args, **kwargs):
        raise NotImplementedError(f"Class {type(self)} must implement method 'execute'")


class RunCommand(AbstractRunCommand):
    def __init__(
        self,
        data_processor,
        report,
        logger,
        cs_session_manager,
        workers_num,
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
            data_processor, report, logger, cs_session_manager, workers_num, output, autoload
        )
        self.offline = offline

    def _parse_vendor_number(self, sys_obj_id):
        """Get device vendor number from SNMPv2 mib.

        :param: str sys_obj_id:
        :return: device vendor number
        :rtype: str
        """
        match_name = re.search(
            r"(::enterprises|.1.3.6.1.4.1)\.(?P<vendor>[0-9]*)\..*$", sys_obj_id
        )
        if match_name:
            return match_name.group("vendor")

    def _generate_device_name(self, vendor_name):
        """Generate name for the device model on CloudShell based on vendor name.

        :param str vendor_name:
        :rtype: str
        """
        vendor_name = re.sub("[^a-zA-Z0-9 .-]", "", vendor_name)
        return f"{vendor_name}-{uuid.uuid4()}"

    async def _populate_entry_with_snmp_data(self, entry, snmp_comunity_strings):
        """Discover device attributes via SNMP.

        :param autodiscovery.reports.base.Entry entry:
        :param snmp_comunity_strings: list of possible SNMP strings
        :type snmp_comunity_strings: list
        :rtype: autodiscovery.reports.base.Entry
        """
        for send_func in (self.logger.info, self.output.send):
            send_func(
                f"Discovering SNMP community string for device with IP {entry.ip}"
            )

        snmp_service = await AsyncSNMPService.get_snmp_service(
            ip_address=entry.ip,
            snmp_community_strings=snmp_comunity_strings,
            logger=self.logger,
        )

        for send_func in (self.logger.info, self.output.send):
            send_func(
                f"Discovered SNMP community string '{snmp_service.snmp_community}' for device with IP {entry.ip}"
            )

        vendor_enterprise_numbers = self.data_processor.load_vendor_enterprise_numbers()
        entry.snmp_community = snmp_service.snmp_community

        with snmp_service as snmp_service:
            entry.sys_object_id = await snmp_service.get_sys_object_id()
            entry.description = await snmp_service.get_sys_descr()
            sys_name = await snmp_service.get_sys_name()

        vendor_number = self._parse_vendor_number(entry.sys_object_id)
        entry.vendor = vendor_enterprise_numbers[vendor_number]

        if not sys_name:
            sys_name = self._generate_device_name(vendor_name=entry.vendor)

        entry.device_name = sys_name
        return entry

    async def discover_device(
        self,
        ip_address,
        snmp_comunity_strings,
        vendor_settings,
        vendor_config,
        cs_domain,
        progress_bar,
        semaphore,
    ):
        await semaphore.acquire()

        try:
            with self.report.add_entry(
                ip=ip_address, domain=cs_domain, offline=self.offline
            ) as entry:
                entry = await self._populate_entry_with_snmp_data(
                    entry=entry, snmp_comunity_strings=snmp_comunity_strings
                )
                vendor = vendor_config.get_vendor(vendor_name=entry.vendor)

                if vendor is None:
                    raise ReportableException(f"Unsupported vendor {entry.vendor}")

                try:
                    handler = self.vendor_type_handlers_map[vendor.vendor_type.lower()]
                except KeyError:
                    raise ReportableException(
                        f"Invalid vendor type '{vendor.vendor_type}'. Possible "
                        f"values are: {self.vendor_type_handlers_map.keys()}"
                    )

                discovered_entry = handler.discover(
                    entry=entry, vendor=vendor, vendor_settings=vendor_settings
                )

                if not self.offline:
                    cs_session = await self.cs_session_manager.get_session(
                        cs_domain=cs_domain
                    )
                    await handler.upload(
                        entry=discovered_entry, vendor=vendor, cs_session=cs_session
                    )

        except ReportableException as e:
            self.output.send(
                f"Failed to discover {ip_address} device. {str(e)}", error=True
            )
            self.logger.exception(f"Failed to discover {ip_address} device due to:")
        except Exception:
            self.output.send(
                f"Failed to discover {ip_address} device. See log for details",
                error=True,
            )
            self.logger.exception(f"Failed to discover {ip_address} device due to:")
        else:
            self.output.send(f"Device with IP {ip_address} was successfully discovered")
            self.logger.info(f"Device with IP {ip_address} was successfully discovered")

        progress_bar.update()
        semaphore.release()

    async def execute(
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

        devices_ips = [
            (device_ip, devices_ip_range.domain)
            for devices_ip_range in devices_ips
            for device_ip in devices_ip_range.ip_range
        ]

        semaphore = asyncio.Semaphore(value=self.workers_num)

        with tqdm(
            desc=f"{Fore.RESET}Total progress", total=len(devices_ips), position=1
        ) as progress_bar:
            await asyncio.gather(
                *[
                    asyncio.create_task(
                        (
                            self.discover_device(
                                ip_address=device_ip,
                                snmp_comunity_strings=snmp_comunity_strings,
                                vendor_settings=vendor_settings,
                                vendor_config=vendor_config,
                                cs_domain=cs_domain,
                                progress_bar=progress_bar,
                                semaphore=semaphore,
                            )
                        )
                    )
                    for device_ip, cs_domain in devices_ips
                ],
                return_exceptions=True
            )

        self.report.generate()
        failed_entries_count = self.report.get_failed_entries_count()

        print (
            f"\n\n\n{Fore.GREEN}Discovery process finished: "
            f"\n\tSuccessfully discovered {len(self.report.entries) - failed_entries_count} devices."
            f"\n\t{Fore.RED}Failed to discover {failed_entries_count} devices.{Fore.RESET}\n"
        )
