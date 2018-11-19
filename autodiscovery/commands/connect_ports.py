from autodiscovery.exceptions import ReportableException
from autodiscovery.output import EmptyOutput


class ConnectPortsCommand(object):
    def __init__(self, cs_session_manager, report, logger, output=None):
        """

        :param cs_session_manager:
        :param report:
        :param logger:
        :param output:
        """
        if output is None:
            output = EmptyOutput()

        self.cs_session_manager = cs_session_manager
        self.report = report
        self.output = output
        self.logger = logger

    def execute(self, parsed_entries):
        """

        :param list[autodiscovery.reports.connections.base.Entry] parsed_entries:
        :return:
        """
        for parsed_entry in parsed_entries:
            self.logger.info("Processing connection between port {} and {}".format(parsed_entry.source_port,
                                                                                   parsed_entry.target_port))

            try:
                with self.report.edit_entry(entry=parsed_entry) as entry:

                    if entry.status == entry.SUCCESS_STATUS:
                        continue

                    entry.status = entry.SUCCESS_STATUS
                    cs_session = self.cs_session_manager.get_session(cs_domain=entry.domain)

                    cs_session.UpdatePhysicalConnection(resourceAFullPath=parsed_entry.source_port,
                                                        resourceBFullPath=parsed_entry.target_port)

            except ReportableException as e:
                self.output.send("Failed to connect port {} and {}. {}".format(parsed_entry.source_port,
                                                                               parsed_entry.target_port,
                                                                               str(e)), error=True)
                self.logger.exception("Failed to connect ports due to:")

            except Exception:
                self.output.send("Failed to connect port {} and {}. See log for details".format(
                    parsed_entry.source_port,
                    parsed_entry.target_port), error=True)
                self.logger.exception("Failed to connect ports due to:")

            else:
                msg = "Connection between port {} and port {} was successfully processed".format(
                    parsed_entry.source_port,
                    parsed_entry.target_port)

                self.output.send(msg)
                self.logger.info(msg)

        self.report.generate()
