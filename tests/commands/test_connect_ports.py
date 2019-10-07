import unittest

import mock

from autodiscovery.commands import ConnectPortsCommand
from autodiscovery.commands.connect_ports import PORT_FAMILY
from autodiscovery.exceptions import ReportableException


class TestRunCommand(unittest.TestCase):
    def setUp(self):
        self.cs_session_manager = mock.MagicMock()
        self.report = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.output = mock.MagicMock()
        self.connect_ports_command = ConnectPortsCommand(
            cs_session_manager=self.cs_session_manager,
            report=self.report,
            offline=False,
            logger=self.logger,
            output=self.output,
        )

    def test_get_resource_attribute_value(self):
        attr_name = "Test Attribute"
        attr_val = "Test Value"
        resource = mock.MagicMock(
            ResourceAttributes=[
                mock.MagicMock(Name="Other Attribute", Value="Other Value"),
                mock.MagicMock(Name=attr_name, Value=attr_val),
            ]
        )
        # act
        result = self.connect_ports_command._get_resource_attribute_value(
            resource=resource, attribute_name=attr_name
        )
        # verify
        self.assertEqual(result, attr_val)

    def test_find_ports(self):
        port1 = mock.MagicMock(ResourceFamilyName=PORT_FAMILY)
        port2 = mock.MagicMock(ResourceFamilyName=PORT_FAMILY)
        resource = mock.MagicMock(
            ChildResources=[port1, mock.MagicMock(ChildResources=[port2])]
        )
        # act
        result = self.connect_ports_command._find_ports(resource=resource)
        # verify
        self.assertEqual(result, [port1, port2])

    def test_find_adjacent_ports(self):
        port1 = mock.MagicMock(Name="Port 1")
        port2 = mock.MagicMock(Name="Port 2")
        self.connect_ports_command._find_ports = mock.MagicMock(
            return_value=[port1, port2]
        )
        self.connect_ports_command._get_resource_attribute_value = mock.MagicMock(
            side_effect=[None, "test adjacent attr"]
        )
        # act
        result = self.connect_ports_command._find_adjacent_ports(
            resource=mock.MagicMock()
        )
        # verify
        self.assertEqual(result, [("Port 2", "test adjacent attr")])

    @mock.patch("autodiscovery.commands.connect_ports.AttributeNameValue")
    def test_find_resource_by_sys_name(self, attribute_name_value_class):
        """Check that method will return full name if the found resource."""
        family_name = "Test Family Name"
        sys_name = "Test Sys Name"
        cs_session = mock.MagicMock(
            GetResourceList=mock.MagicMock(
                return_value=mock.MagicMock(
                    Resources=[mock.MagicMock(ResourceFamilyName=family_name)]
                )
            )
        )

        cs_session.FindResources.side_effect = [
            mock.MagicMock(Resources=[mock.MagicMock()]),
            mock.MagicMock(Resources=[]),
        ]
        # act
        result = self.connect_ports_command._find_resource_by_sys_name(
            cs_session=cs_session, sys_name=sys_name
        )
        # verify

        cs_session.FindResources.assert_any_call(
            includeSubResources=False,
            resourceFamily="",
            attributeValues=[attribute_name_value_class()],
        )

        cs_session.FindResources.assert_any_call(
            includeSubResources=False,
            resourceFamily=family_name,
            attributeValues=[attribute_name_value_class()],
        )

        self.assertEqual(result, cs_session.GetResourceDetails())

    def test_find_resource_by_sys_name_no_such_resource(self):
        """Method should raise ReportableException if it fails to find resource."""
        sys_name = "Test Sys Name"
        cs_session = mock.MagicMock()
        cs_session.FindResources.return_value.Resources = []
        # act
        with self.assertRaisesRegexp(ReportableException, "Unable to find resource"):
            self.connect_ports_command._find_resource_by_sys_name(
                cs_session=cs_session, sys_name=sys_name
            )

    def test_find_resource_by_sys_name_finds_several_resources(self):
        """Method should raise ReportableException if it finds several resources."""
        sys_name = "Test Sys Name"
        cs_session = mock.MagicMock()
        cs_session.FindResources.return_value.Resources = [
            mock.MagicMock(),
            mock.MagicMock(),
        ]
        # act
        with self.assertRaisesRegexp(ReportableException, "Found several resources"):
            self.connect_ports_command._find_resource_by_sys_name(
                cs_session=cs_session, sys_name=sys_name
            )

    def test_find_port_by_adjacent_name(self):
        port_name = "Test Port Name"
        port = mock.MagicMock(
            Name="10.10.10.10/Chassis 1/Module 1/{}".format(port_name)
        )
        self.connect_ports_command._find_ports = mock.MagicMock(return_value=[port])
        # act
        result = self.connect_ports_command._find_port_by_adjacent_name(
            adjacent_resource=mock.MagicMock(), adjacent_port_name=port_name
        )
        # verify
        self.assertEquals(result, port)

    def test_find_port_by_adjacent_name_no_such_port(self):
        port_name = "Test Port Name"
        port = mock.MagicMock(Name="10.10.10.10/Chassis 1/Module 1/Other Port Name")
        self.connect_ports_command._find_ports = mock.MagicMock(return_value=[port])
        # act
        with self.assertRaisesRegexp(
            ReportableException, "Unable to find Adjacent port"
        ):
            self.connect_ports_command._find_port_by_adjacent_name(
                adjacent_resource=mock.MagicMock(), adjacent_port_name=port_name
            )

    def test_execute(self):
        domain = "Test Domain"
        resource_name = "Test Resource"
        port_name = "Port 1"
        adjacent = "Device 1 through Eth 2/1"
        cs_session = mock.MagicMock()
        self.cs_session_manager.get_session.return_value = cs_session
        self.connect_ports_command._find_adjacent_ports = mock.MagicMock(
            return_value=[(port_name, adjacent)]
        )
        self.connect_ports_command._find_resource_by_sys_name = mock.MagicMock()
        self.connect_ports_command._find_port_by_adjacent_name = mock.MagicMock()
        # act
        self.connect_ports_command.execute(
            resources_names=[resource_name], domain=domain
        )

        # verify
        cs_session.GetResourceDetails.assert_called_once_with(resource_name)
        self.report.add_entry.assert_called_once_with(
            adjacent=adjacent,
            domain=domain,
            offline=False,
            resource_name=resource_name,
            source_port=port_name,
            target_port="",
        )
        port = self.connect_ports_command._find_port_by_adjacent_name()
        cs_session.UpdatePhysicalConnection.assert_called_once_with(
            resourceAFullPath=self.report.add_entry().__enter__().source_port,
            resourceBFullPath=port.Name,
        )

        self.report.generate.assert_called_once_with()

    def test_execute_handles_reportable_exception(self):
        domain = "Test Domain"
        resource_name = "Test Resource"
        port_name = "Port 1"
        adjacent = "Device 1 through Eth 2/1"
        cs_session = mock.MagicMock()
        self.cs_session_manager.get_session.return_value = cs_session
        self.connect_ports_command._find_adjacent_ports = mock.MagicMock(
            return_value=[(port_name, adjacent)]
        )
        self.connect_ports_command._find_resource_by_sys_name = mock.MagicMock(
            side_effect=ReportableException
        )
        # act
        self.connect_ports_command.execute(
            resources_names=[resource_name], domain=domain
        )

        # verify
        self.report.add_entry.assert_called_once_with(
            adjacent=adjacent,
            domain=domain,
            offline=False,
            resource_name=resource_name,
            source_port=port_name,
            target_port="",
        )

        self.report.generate.assert_called_once_with()
        self.logger.exception.assert_called_once()

    def test_execute_handles_exception(self):
        domain = "Test Domain"
        resource_name = "Test Resource"
        port_name = "Port 1"
        adjacent = "Device 1 through Eth 2/1"
        cs_session = mock.MagicMock()
        self.cs_session_manager.get_session.return_value = cs_session
        self.connect_ports_command._find_adjacent_ports = mock.MagicMock(
            return_value=[(port_name, adjacent)]
        )
        self.connect_ports_command._find_resource_by_sys_name = mock.MagicMock(
            side_effect=Exception
        )
        # act
        self.connect_ports_command.execute(
            resources_names=[resource_name], domain=domain
        )

        # verify
        self.report.add_entry.assert_called_once_with(
            adjacent=adjacent,
            domain=domain,
            offline=False,
            resource_name=resource_name,
            source_port=port_name,
            target_port="",
        )

        self.report.generate.assert_called_once_with()
        self.logger.exception.assert_called_once()
