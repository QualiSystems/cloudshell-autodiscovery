import json
import os

from autodiscovery import config
from autodiscovery import models


class JsonDataProcessor(object):
    def _prepare_file_path(self, filename):
        """Add full path to the filename

        :param str filename: Name of the file to save ("example.com")
        :return: Full path to the file ("/var/projects/cloudshell-autodiscovery-tool/example.com")
        :rtype: str
        """
        dir_name = os.path.split(os.path.abspath(__file__))[0]
        return os.path.join(dir_name, os.pardir, config.DATA_FOLDER, filename)

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
        :rtype: dict
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

    def load_vendor_definition(self):
        """Load Vendors definitions from JSON file into the corresponding models

        :rtype: models.VendorDefinitionCollection
        """
        vendors_data = self._load(filename=config.VENDOR_DEFINITION_FILE)
        vendors = []
        for vendor_data in vendors_data:
            operation_systems = []
            for os_data in vendor_data.get("operation_systems", []):
                operating_sys = models.OperationSystem(name=os_data["name"],
                                                       aliases=os_data.get("aliases", []),
                                                       default_model=os_data.get("default_model"),
                                                       models_map=os_data.get("models_map"),
                                                       families=os_data.get("families"),
                                                       first_gen=os_data.get("first_gen"),
                                                       second_gen=os_data.get("second_gen"))
                operation_systems.append(operating_sys)

            vendor = models.VendorDefinition(name=vendor_data["name"],
                                             aliases=vendor_data.get("aliases", []),
                                             vendor_type=vendor_data["type"],
                                             default_os=vendor_data.get("default_os"),
                                             default_prompt=vendor_data.get("default_prompt"),
                                             enable_prompt=vendor_data.get("enable_prompt"),
                                             operation_systems=operation_systems)
            vendors.append(vendor)

        return models.VendorDefinitionCollection(vendors=vendors)
