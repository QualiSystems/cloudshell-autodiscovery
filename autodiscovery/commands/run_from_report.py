from autodiscovery.commands.run import AbstractRunCommand
from autodiscovery.exceptions import ReportableException


class RunFromReportCommand(AbstractRunCommand):
    def execute(self, device_models, cs_ip, cs_user, cs_password, additional_vendors_data):
        """

        :param device_models:
        :param cs_ip:
        :param cs_user:
        :param cs_password:
        :param additional_vendors_data:
        :return:
        """
        vendor_config = self.data_processor.load_vendor_config(additional_vendors_data=additional_vendors_data)
        self._init_cs_session(cs_ip=cs_ip, cs_user=cs_user, cs_password=cs_password)

        for device_model in device_models:
            try:
                with self.report.edit_entry(entry=device_model) as entry:

                    if entry.status == entry.SUCCESS_STATUS:
                        continue

                    vendor = vendor_config.get_vendor(vendor_name=device_model.vendor)

                    if vendor is None:
                        raise ReportableException("Unsupported vendor {}".format(device_model.vendor))

                    try:
                        handler = self.vendor_type_handlers_map[vendor.vendor_type.lower()]
                    except KeyError:
                        raise ReportableException("Invalid vendor type '{}'. Possible values are: {}"
                                                  .format(vendor.vendor_type, self.vendor_type_handlers_map.keys()))

                    handler.upload(entry=entry,  vendor=vendor, cs_session=self.cs_session)

            except Exception:
                self.logger.exception("Failed to discover {} device due to:".format(device_model.ip))

        self.report.generate()
