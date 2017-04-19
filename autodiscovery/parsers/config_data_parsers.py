import json

from autodiscovery.exceptions import AutoDiscoveryException


def get_config_data_parser(file_name):
    parsers = (JSONConfigDataParser,)

    for parser_cls in parsers:
        if file_name.endswith(parser_cls.FILE_EXTENSION):
            return parser_cls()

    raise AutoDiscoveryException("Invalid Additional Config Data file format. Available formats are: {}".format(
        ", ".join([parser.FILE_EXTENSION for parser in parsers])))


class JSONConfigDataParser(object):
    FILE_EXTENSION = "json"

    def parse(self, config_file):
        """Parse an additional vendors configuration file into list

        :param str config_file: path to config file
        :rtype: list[dict]
        """
        with open(config_file) as f:
            return json.load(f)
