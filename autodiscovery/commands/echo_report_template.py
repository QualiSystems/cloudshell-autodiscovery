from autodiscovery.common.consts import ResourceModelsAttributes


class EchoReportTemplateCommand(object):
    def __init__(self, report):
        """

        :param autodiscovery.reports.ExcelReport report:
        """
        self.report = report

    def execute(self):
        """Execute echo report file command

        :return:
        """
        with self.report.add_entry(ip="192.168.42.235", domain="Global", offline=True) as entry:
            entry.snmp_community = "Cisco"
            entry.sys_object_id = "SNMPv2-SMI::enterprises.9.1.359"

            entry.description = ("Cisco Internetwork Operating System Software IOS (tm) C2950 Software "
                                 "(C2950-I6K2L2Q4-M), Version 12.1(22)EA14, RELEASE SOFTWARE (fc1) Technical Support: "
                                 "http://www.cisco.com/techsupport Copyright (c) 1986-2010 by cisco Systems, "
                                 "Inc. Compiled Tue 26-O")

            entry.vendor = "ciscoSystems"
            entry.model_type = "switch"
            entry.device_name = "Boogie.Cisco2950"
            entry.folder_path = "cisco_autodiscovered"
            entry.comment = "Auto-generated example device info"
            entry.add_attribute(ResourceModelsAttributes.USER, "root")
            entry.add_attribute(ResourceModelsAttributes.PASSWORD, "Password1")

        self.report.generate()
