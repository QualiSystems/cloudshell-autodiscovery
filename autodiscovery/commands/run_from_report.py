from autodiscovery.commands.run import AbstractRunCommand
from autodiscovery.exceptions import ReportableException


class RunFromReportCommand(AbstractRunCommand):
    def execute(self, additional_vendors_data):
        """Execute command.

        :param list[dict] additional_vendors_data:
        :return:
        """
        vendor_config = self.data_processor.load_vendor_config(
            additional_vendors_data=additional_vendors_data
        )

        for entry in self.report.entries:
            self.logger.info("Uploading device with IP {}".format(entry.ip))
            self.output.send("Uploading device with IP {}".format(entry.ip))

            try:
                with entry:
                    if entry.status == entry.SUCCESS_STATUS:
                        continue
                    else:
                        entry.status = entry.SUCCESS_STATUS

                    vendor = vendor_config.get_vendor(vendor_name=entry.vendor)

                    if vendor is None:
                        raise ReportableException(
                            "Unsupported vendor {}".format(entry.vendor)
                        )

                    try:
                        handler = self.vendor_type_handlers_map[
                            vendor.vendor_type.lower()
                        ]
                    except KeyError:
                        raise ReportableException(
                            "Invalid vendor type '{}'. Possible values are: {}".format(
                                vendor.vendor_type, self.vendor_type_handlers_map.keys()
                            )
                        )

                    cs_session = self.cs_session_manager.get_session(
                        cs_domain=entry.domain
                    )
                    handler.upload(entry=entry, vendor=vendor, cs_session=cs_session)

            except Exception:
                self.output.send(
                    "Failed to discover {} device. {}".format(entry.ip, entry.comment),
                    error=True,
                )
                self.logger.exception(
                    "Failed to upload {} device due to:".format(entry.ip)
                )
            else:
                self.output.send(
                    "Device with IP {} was successfully uploaded".format(entry.ip)
                )
                self.logger.info(
                    "Device with IP {} was successfully uploaded".format(entry.ip)
                )

        self.report.generate()
