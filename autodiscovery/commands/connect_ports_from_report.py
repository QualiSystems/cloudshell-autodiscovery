from autodiscovery.exceptions import ReportableException
from autodiscovery.output import EmptyOutput


class ConnectPortsFromReportCommand(object):
    def __init__(self, cs_session_manager, report, logger, output=None):
        """Init command.

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

    def execute(self):
        """Execute command.

        :return:
        """
        for entry in self.report.entries:
            self.logger.info(
                f"Processing connection between port {entry.source_port} "
                f"and {entry.target_port}"
            )
            try:
                with entry:
                    if entry.status == entry.SUCCESS_STATUS:
                        continue

                    if not all([entry.source_port, entry.target_port]):
                        raise ReportableException(
                            "'Source Port Full Name' and 'Target Port Full Name' "
                            "fields cannot be empty"
                        )

                    entry.status = entry.SUCCESS_STATUS
                    cs_session = self.cs_session_manager.get_session(
                        cs_domain=entry.domain
                    )

                    cs_session.UpdatePhysicalConnection(
                        resourceAFullPath=entry.source_port,
                        resourceBFullPath=entry.target_port,
                    )

            except ReportableException as e:
                self.output.send(
                    f"Failed to connect port '{entry.source_port}' "
                    f"and '{entry.target_port}'. {str(e)}",
                    error=True,
                )
                self.logger.exception("Failed to connect ports due to:")

            except Exception:
                self.output.send(
                    f"Failed to connect port '{entry.source_port}' and "
                    f"'{entry.target_port}'. See log for details",
                    error=True,
                )
                self.logger.exception("Failed to connect ports due to:")

            else:
                msg = (
                    f"Connection between port '{entry.source_port}' and port "
                    f"'{entry.target_port}' was successfully processed"
                )

                self.output.send(msg)
                self.logger.info(msg)

        self.report.generate()
