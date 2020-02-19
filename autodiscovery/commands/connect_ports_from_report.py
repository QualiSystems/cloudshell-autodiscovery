import asyncio

from aiodecorators import Semaphore
from colorama import Fore
from tqdm import tqdm

from autodiscovery.commands.run import ASYNCIO_CONCURRENCY_LIMIT
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

    @Semaphore(ASYNCIO_CONCURRENCY_LIMIT)
    async def process_resource_connection(self, entry, progress_bar):
        self.logger.info(
            f"Processing connection between port {entry.source_port} "
            f"and {entry.target_port}"
        )
        try:
            with entry:
                if entry.status == entry.SUCCESS_STATUS:
                    return

                if not all([entry.source_port, entry.target_port]):
                    raise ReportableException(
                        "'Source Port Full Name' and 'Target Port Full Name' "
                        "fields cannot be empty"
                    )

                entry.status = entry.SUCCESS_STATUS
                cs_session = await self.cs_session_manager.get_session(
                    cs_domain=entry.domain
                )

                await cs_session.UpdatePhysicalConnection(
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

        progress_bar.update()

    async def execute(self):
        """Execute command.

        :return:
        """
        with tqdm(
            desc=f"{Fore.RESET}Total progress", total=len(self.report.entries), position=1
        ) as progress_bar:
            await asyncio.gather(
                *[
                    asyncio.create_task(
                        (
                            self.process_resource_connection(
                                entry=entry,
                                progress_bar=progress_bar,
                            )
                        )
                    )
                    for entry in self.report.entries
                ],
                return_exceptions=True
            )

        self.report.generate()
        failed_entries_count = self.report.get_failed_entries_count()

        self.output.send(
            f"\n\n\n{Fore.GREEN}Connections discovery process finished: "
            f"\n\tSuccessfully discovered {len(self.report.entries) - failed_entries_count} connections."
            f"\n\t{Fore.RED}Failed to discovery {failed_entries_count} connections.{Fore.RESET}\n"
        )

