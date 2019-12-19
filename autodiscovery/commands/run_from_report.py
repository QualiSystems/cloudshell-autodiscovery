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
            msg = f"Uploading device with IP {entry.ip}"
            self.logger.info(msg)
            self.output.send(msg)

            try:
                with entry:
                    if entry.status == entry.SUCCESS_STATUS:
                        continue
                    else:
                        entry.status = entry.SUCCESS_STATUS

                    vendor = vendor_config.get_vendor(vendor_name=entry.vendor)

                    if vendor is None:
                        raise ReportableException(f"Unsupported vendor {entry.vendor}")

                    try:
                        handler = self.vendor_type_handlers_map[
                            vendor.vendor_type.lower()
                        ]
                    except KeyError:
                        raise ReportableException(
                            f"Invalid vendor type '{vendor.vendor_type}'. "
                            f"Possible values are: "
                            f"{self.vendor_type_handlers_map.keys()}"
                        )

                    cs_session = self.cs_session_manager.get_session(
                        cs_domain=entry.domain
                    )
                    handler.upload(entry=entry, vendor=vendor, cs_session=cs_session)

            except Exception:
                self.output.send(
                    f"Failed to discover {entry.ip} device. {entry.comment}", error=True
                )
                self.logger.exception(f"Failed to upload {entry.ip} device due to:")
            else:
                self.output.send(f"Device with IP {entry.ip} was successfully uploaded")
                self.logger.info(f"Device with IP {entry.ip} was successfully uploaded")

        self.report.generate()
