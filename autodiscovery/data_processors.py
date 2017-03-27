import json

from autodiscovery import config
from autodiscovery import models
from autodiscovery.common import utils


class JsonDataProcessor(object):

    def __init__(self, logger):
        """

        :param logging.Logger logger:
        """
        self.logger = logger

    def _prepare_file_path(self, filename):
        """Add full path to the filename

        :param str filename: Name of the file to save ("example.json")
        :return: Full path to the file ("/var/projects/cloudshell-autodiscovery-tool/example.json")
        :rtype: str
        """
        return utils.get_full_path(config.DATA_FOLDER, filename)

    def _save(self, data, filename):
        """Save JSON Data to the given file

        :param dict data: JSON data that will be saved to the file
        :param str filename: Name of the file to save ("example.com")
        :return:
        """
        file_path = self._prepare_file_path(filename)

        with open(file_path, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)

    def _load(self, filename):
        """Load JSON Data from file

        :param str filename: Name of the file to save ("example.com")
        :return: JSON data
        """
        file_path = self._prepare_file_path(filename)

        with open(file_path, 'r') as outfile:
            return json.load(outfile)

    def save_vendor_enterprise_numbers(self, data):
        """Save Vendors PEN to the file in JSON format

        :param dict data: JSON data that will be saved to the file
        :return:
        """
        return self._save(data=data, filename=config.VENDOR_ENTERPRISE_NUMBERS_FILE)

    def load_vendor_enterprise_numbers(self):
        """Load Vendors PEN data from the file

        :return: JSON data
        :rtype: dict
        """
        return self._load(filename=config.VENDOR_ENTERPRISE_NUMBERS_FILE)

    def _merge_vendors_data(self, conf_data, additional_data):
        """Merge default vendors configuration with additional one

        :param list[dict] conf_data: default vendors config data
        :param list[dict] additional_data: additional vendors config data
        :rtype: list[dict]
        """
        merged_data = []
        for add_vendor_data in additional_data:
            for conf_vendor_data in conf_data:
                if conf_vendor_data["name"] == add_vendor_data["name"]:
                    conf_data.remove(conf_vendor_data)

                    for conf_os in conf_vendor_data.get("operation_systems", []):
                        for add_os in add_vendor_data.get("operation_systems", []):
                            if conf_os["name"] == add_os["name"]:
                                conf_vendor_data["operation_systems"].remove(conf_os)

                    if "operation_systems" in conf_vendor_data:
                        oses = add_vendor_data.setdefault("operation_systems", [])
                        oses.extend(conf_vendor_data["operation_systems"])

            merged_data.append(add_vendor_data)

        merged_data.extend(conf_data)
        return merged_data

    def load_vendor_config(self, additional_vendors_data=None):
        """Load Vendors definitions from JSON file into the corresponding models

        :rtype: models.VendorDefinitionCollection
        """
        vendors_data = self._load(filename=config.VENDORS_CONFIG_FILE)
        vendors = []

        for vendor_data in self._merge_vendors_data(conf_data=vendors_data,
                                                    additional_data=additional_vendors_data):

            if vendor_data["type"].lower() == "networking":
                operation_systems = []
                for os_data in vendor_data.get("operation_systems", []):
                    operating_sys = models.OperationSystem(name=os_data["name"],
                                                           aliases=os_data.get("aliases", []),
                                                           default_model=os_data.get("default_model"),
                                                           models_map=os_data.get("models_map", []),
                                                           families=os_data.get("families"))
                    operation_systems.append(operating_sys)

                vendor = models.NetworkingVendorDefinition(name=vendor_data["name"],
                                                           aliases=vendor_data.get("aliases", []),
                                                           vendor_type=vendor_data["type"],
                                                           default_os=vendor_data.get("default_os"),
                                                           default_prompt=vendor_data.get("default_prompt"),
                                                           enable_prompt=vendor_data.get("enable_prompt"),
                                                           operation_systems=operation_systems)

            elif vendor_data["type"].upper() == "PDU":
                vendor = models.PDUVendorDefinition(name=vendor_data["name"],
                                                    aliases=vendor_data.get("aliases", []),
                                                    vendor_type=vendor_data["type"],
                                                    default_prompt=vendor_data.get("default_prompt"),
                                                    enable_prompt=vendor_data.get("enable_prompt"),
                                                    family_name=vendor_data["family_name"],
                                                    model_name=vendor_data["model_name"],
                                                    driver_name=vendor_data["driver_name"])
            else:
                self.logger.warning("Unable to parse vendor '{}'. Vendor type '{}' is not supported".format(
                    vendor_data["name"],
                    vendor_data["type"]
                ))
                continue

            vendors.append(vendor)

        return models.VendorDefinitionCollection(vendors=vendors)
