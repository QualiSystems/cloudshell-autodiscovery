import asyncio

from colorama import Fore
from tqdm import tqdm

from autodiscovery.commands.run import AbstractRunCommand
from autodiscovery.exceptions import ReportableException


class RunFromReportCommand(AbstractRunCommand):
    async def upload_device(self, entry, vendor_config, progress_bar, semaphore):
        """

        :param entry:
        :param vendor_config:
        :param progress_bar:
        :param semaphore:
        :return:
        """
        await semaphore.acquire()

        msg = f"Uploading device with IP {entry.ip}"
        self.logger.info(msg)
        self.output.send(msg)

        try:
            with entry:
                if entry.status == entry.SUCCESS_STATUS:
                    progress_bar.update()
                    return
                else:
                    entry.status = entry.SUCCESS_STATUS

                vendor = vendor_config.get_vendor(vendor_name=entry.vendor)

                if vendor is None:
                    raise ReportableException(f"Unsupported vendor {entry.vendor}")

                try:
                    handler = self.vendor_type_handlers_map[vendor.vendor_type.lower()]
                except KeyError:
                    raise ReportableException(
                        f"Invalid vendor type '{vendor.vendor_type}'. "
                        f"Possible values are: "
                        f"{self.vendor_type_handlers_map.keys()}"
                    )

                cs_session = await self.cs_session_manager.get_session(
                    cs_domain=entry.domain
                )
                await handler.upload(entry=entry, vendor=vendor, cs_session=cs_session)

        except Exception:
            self.output.send(
                f"Failed to discover {entry.ip} device. {entry.comment}", error=True
            )
            self.logger.exception(f"Failed to upload {entry.ip} device due to:")
        else:
            self.output.send(f"Device with IP {entry.ip} was successfully uploaded")
            self.logger.info(f"Device with IP {entry.ip} was successfully uploaded")

        progress_bar.update()
        semaphore.release()

    async def execute(self, additional_vendors_data):
        """Execute command.

        :param list[dict] additional_vendors_data:
        :return:
        """
        semaphore = asyncio.Semaphore(value=self.workers_num)

        vendor_config = self.data_processor.load_vendor_config(
            additional_vendors_data=additional_vendors_data
        )

        with tqdm(
            desc=f"{Fore.RESET}Total progress",
            total=len(self.report.entries),
            position=1,
        ) as progress_bar:
            await asyncio.gather(
                *[
                    asyncio.create_task(
                        (
                            self.upload_device(
                                entry=entry,
                                vendor_config=vendor_config,
                                progress_bar=progress_bar,
                                semaphore=semaphore,
                            )
                        )
                    )
                    for entry in self.report.entries
                ],
                return_exceptions=True
            )

        self.report.generate()
        failed_entries_count = self.report.get_failed_entries_count()

        print (
            f"\n\n\n{Fore.GREEN}Uploading process finished: "
            f"\n\tSuccessfully uploaded {len(self.report.entries) - failed_entries_count} devices."
            f"\n\t{Fore.RED}Failed to upload {failed_entries_count} devices.{Fore.RESET}\n"
        )
