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
        self.run_command = RunCommand(data_processor=self.data_processor,
                                      report=self.report,
                                      logger=self.logger,
                                      cs_session_manager=self.cs_session_manager,
                                      output=self.output,
                                      autoload=True,
                                      offline=False)

    def test_parse_vendor_number(self):
        # act
        result = self.run_command._parse_vendor_number(sys_obj_id="SNMPv2-SMI::enterprises.9.1.222")
        # verify
        self.assertEqual(result, "9")

    @mock.patch("autodiscovery.commands.run.QualiSnmp")
    def test_get_snmp_handler(self, quali_snmp_class):
        quali_snmp = mock.MagicMock()
        quali_snmp_class.return_value = quali_snmp
        snmp_community = "valid snmp community"
        # act
        result = self.run_command._get_snmp_handler(device_ip="10.10.10.10",
                                                    snmp_comunity_strings=[snmp_community])
        # verify
        self.assertEqual(result, (quali_snmp, snmp_community))

    @mock.patch("autodiscovery.commands.run.QualiSnmp")
    def test_get_snmp_handler_with_invalid_snmp_string(self, quali_snmp_class):
        quali_snmp = mock.MagicMock()
        quali_snmp_class.side_effect = Exception("")
        snmp_community = "valid snmp community"
        # act
        with self.assertRaisesRegexp(ReportableException, "SNMP timeout"):
            self.run_command._get_snmp_handler(device_ip="10.10.10.10",
                                               snmp_comunity_strings=[snmp_community])

    def test_execute(self):
        vendor_settings = mock.MagicMock()
        ip = "10.10.10.10"
        device_data = mock.MagicMock(ip_range=[ip])
        # act
        self.run_command.execute(devices_ips=[device_data],
                                 snmp_comunity_strings=["snmp community"],
                                 vendor_settings=vendor_settings,
                                 additional_vendors_data=None)
        # verify
        self.report.add_entry.assert_called_once_with(domain=device_data.domain,
                                                      ip=ip,
                                                      offline=False)
