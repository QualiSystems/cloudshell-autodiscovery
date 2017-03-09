import requests

from autodiscovery import config


class UpdateVendorsCommand(object):
    def __init__(self, data_processor, logger):
        """

        :param autodiscovery.data_processors.JsonDataProcessor data_processor:
        :param logging.Logger logger:
        """
        self.data_processor = data_processor
        self.logger = logger

    def _parse_vendor_numbers(self, data_string):
        """Parse vendor PEN into dict

        :return: dictionary {"vendpor PEN": "vendor name"}
        :rtype: dict
        """
        res_dict = {}
        resp_lines = data_string.split("\n")

        for i, line in enumerate(resp_lines):
            try:
                # if line can be parsed to integer and it doesn't contain spaces - it's the enterprise number
                if " " in line:
                    continue
                int(line)
            except ValueError:
                continue

            # next line after the enterprise number is vendor name
            res_dict[line] = resp_lines[i+1].strip()

        return res_dict

    def execute(self, url=None):
        """Execute Update vendors command

        :param str url: URL for the vendor private enterprise numbers
        :return:
        """
        if url is None:
            url = config.VENDOR_ENTERPRISE_NUMBERS_URL

        response = requests.get(url)
        response.raise_for_status()

        res_dict = self._parse_vendor_numbers(data_string=response.content)
        self.data_processor.save_vendor_enterprise_numbers(res_dict)
