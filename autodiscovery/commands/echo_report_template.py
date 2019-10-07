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
        with self.report.add_entry(
            ip="192.168.42.235", domain="Global", offline=True
        ) as entry:
            entry.snmp_community = "Cisco"
            entry.sys_object_id = "-"
            entry.description = "-"
            entry.vendor = "-"
            entry.model_type = "switch"
            entry.device_name = "Boogie.Cisco2950"
            entry.folder_path = "cisco_autodiscovered"
            entry.comment = "Auto-generated device info example"
            entry.add_attribute(ResourceModelsAttributes.USER, "root")
            entry.add_attribute(ResourceModelsAttributes.PASSWORD, "Password1")

        self.report.generate()
