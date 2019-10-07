import unittest

import mock

from autodiscovery.commands import RunCommand
from autodiscovery.exceptions import ReportableException


class TestRunCommand(unittest.TestCase):
    def setUp(self):
        self.data_processor = mock.MagicMock()
        self.report = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.cs_session_manager = mock.MagicMock()
        self.output = mock.MagicMock()
        self.run_command = RunCommand(
            data_processor=self.data_processor,
            report=self.report,
            logger=self.logger,
            cs_session_manager=self.cs_session_manager,
            output=self.output,
            autoload=True,
            offline=False,
        )

    def test_parse_vendor_number(self):
        # act
        result = self.run_command._parse_vendor_number(
            sys_obj_id="SNMPv2-SMI::enterprises.9.1.222"
        )
        # verify
        self.assertEqual(result, "9")

    @mock.patch("autodiscovery.commands.run.QualiSnmp")
    def test_get_snmp_handler(self, quali_snmp_class):
        quali_snmp = mock.MagicMock()
        quali_snmp_class.return_value = quali_snmp
        snmp_community = "valid snmp community"
        # act
        result = self.run_command._get_snmp_handler(
            device_ip="10.10.10.10", snmp_comunity_strings=[snmp_community]
        )
        # verify
        self.assertEqual(result, (quali_snmp, snmp_community))

    @mock.patch("autodiscovery.commands.run.QualiSnmp")
    def test_get_snmp_handler_with_invalid_snmp_string(self, quali_snmp_class):
        quali_snmp_class.side_effect = Exception("")
        snmp_community = "valid snmp community"
        # act
        with self.assertRaisesRegexp(ReportableException, "SNMP timeout"):
            self.run_command._get_snmp_handler(
                device_ip="10.10.10.10", snmp_comunity_strings=[snmp_community]
            )

    def test_execute(self):
        """Check that method will discover and upload entry"""
        vendor_settings = mock.MagicMock()
        ip = "10.10.10.10"
        snmp_community = "snmp community string"
        device_data = mock.MagicMock(ip_range=[ip])
        handler = mock.MagicMock()
        self.run_command._get_snmp_handler = mock.MagicMock(
            return_value=(mock.MagicMock(), snmp_community)
        )
        self.run_command._parse_vendor_number = mock.MagicMock()
        self.run_command.vendor_type_handlers_map = mock.MagicMock(
            __getitem__=mock.MagicMock(return_value=handler)
        )
        # act
        self.run_command.execute(
            devices_ips=[device_data],
            snmp_comunity_strings=[snmp_community],
            vendor_settings=vendor_settings,
            additional_vendors_data=None,
        )
        # verify
        self.report.add_entry.assert_called_once_with(
            domain=device_data.domain, ip=ip, offline=False
        )

        self.cs_session_manager.get_session.assert_called_once_with(
            cs_domain=device_data.domain
        )
        self.report.generate.assert_called_once_with()
        handler.discover.assert_called_once_with(
            entry=self.report.add_entry().__enter__(),
            vendor=self.data_processor.load_vendor_config().get_vendor(),
            vendor_settings=vendor_settings,
        )

        handler.upload.assert_called_once_with(
            entry=handler.discover(),
            vendor=self.data_processor.load_vendor_config().get_vendor(),
            cs_session=self.cs_session_manager.get_session(),
        )

    def test_execute_handles_exception(self):
        """Check that method will handle Exception and will generate report"""
        vendor_settings = mock.MagicMock()
        ip = "10.10.10.10"
        snmp_community = "snmp community string"
        device_data = mock.MagicMock(ip_range=[ip])
        self.run_command._discover_device = mock.MagicMock(side_effect=Exception())
        # act
        self.run_command.execute(
            devices_ips=[device_data],
            snmp_comunity_strings=[snmp_community],
            vendor_settings=vendor_settings,
            additional_vendors_data=None,
        )
        # verify
        self.report.add_entry.assert_called_once_with(
            domain=device_data.domain, ip=ip, offline=False
        )

        self.report.generate.assert_called_once_with()
        self.logger.exception.assert_called_once()

    def test_execute_handles_reportable_exception(self):
        """Check that method will handle ReportableException and will generate report"""
        vendor_settings = mock.MagicMock()
        ip = "10.10.10.10"
        snmp_community = "snmp community string"
        device_data = mock.MagicMock(ip_range=[ip])
        self.run_command._discover_device = mock.MagicMock(
            side_effect=ReportableException()
        )
        # act
        self.run_command.execute(
            devices_ips=[device_data],
            snmp_comunity_strings=[snmp_community],
            vendor_settings=vendor_settings,
            additional_vendors_data=None,
        )
        # verify
        self.report.add_entry.assert_called_once_with(
            domain=device_data.domain, ip=ip, offline=False
        )

        self.report.generate.assert_called_once_with()
        self.logger.exception.assert_called_once()
