import json

import yaml
from ipaddress import ip_address

from autodiscovery.exceptions import AutoDiscoveryException
from autodiscovery import models


def get_input_data_parser(file_name):
    parsers = (JSONInputDataParser, YAMLInputDataParser)

    for parser_cls in parsers:
        if file_name.endswith(parser_cls.FILE_EXTENSION):
            return parser_cls()

    raise AutoDiscoveryException("Invalid Input Data file format. Available formats are: {}".format(
        ", ".join([parser.FILE_EXTENSION for parser in parsers])))


class AbstractInputDataParser(object):
    FILE_EXTENSION = "*"

    def _find_ips(self, start_ip, last_ip):
        """Find all IPs in the given range

        :param str start_ip: first IP address in the range
        :param str last_ip:  last IP address in the range
        :return: list of all IPs from the given range
        """
        start_ip = ip_address(start_ip)
        last_ip = ip_address(last_ip)
        result = []

        while start_ip <= last_ip:
            result.append(str(start_ip))
            start_ip += 1

        return result

    def _parse_devices_ips(self, devices_ips):
        """Parse all devices IPs and IP ranges into a single list

        :param list[str] devices_ips:
        :rtype: list
        """
        parsed_ips = []

        for device_range in devices_ips:
            if "-" in device_range:
                first_ip, last_ip = device_range.split("-")
                first_ip_octets = first_ip.split(".")
                last_ip_octets = last_ip.split(".")
                last_ip = first_ip_octets[:4-len(last_ip_octets)] + last_ip_octets[:4-len(last_ip_octets)]
                ips = self._find_ips(start_ip=first_ip, last_ip=".".join(last_ip))
                parsed_ips.extend(ips)
            else:
                parsed_ips.append(device_range)

        return parsed_ips

    def parse(self, input_file):
        """File with the Input data for the run command

        :param str input_file: full path to the input data file
        :rtype: models.InputDataModel
        """
        raise NotImplementedError("Class {} must implement method 'parse'".format(type(self)))


class YAMLInputDataParser(AbstractInputDataParser):
    FILE_EXTENSION = "yml"

    def parse(self, input_file):
        """File with the Input data for the run command

        :param str input_file: full path to the input data file
        :rtype: models.InputDataModel
        """
        with open(input_file) as input_f:
            file_data = input_f.read()

        data = yaml.load(file_data)
        devices_ips = self._parse_devices_ips(data["devices-ips"])
        cli_creds = models.CLICredentialsCollection(data.get("cli-credentials", {}))

        return models.InputDataModel(devices_ips=devices_ips,
                                     cs_ip=data["cloudshell"]["ip"],
                                     cs_user=data["cloudshell"]["user"],
                                     cs_password=data["cloudshell"]["password"],
                                     snmp_community_strings=data["community-strings"],
                                     cli_credentials=cli_creds)


class JSONInputDataParser(AbstractInputDataParser):
    FILE_EXTENSION = "json"

    def parse(self, input_file):
        """File with the Input data for the run command

        :param str input_file: full path to the input data file
        :rtype: models.InputDataModel
        """
        with open(input_file) as input_f:
            data = json.load(input_f)

        devices_ips = self._parse_devices_ips(data["devices-ips"])
        cli_creds = models.CLICredentialsCollection(data.get("cli-credentials", {}))

        return models.InputDataModel(devices_ips=devices_ips,
                                     cs_ip=data["cloudshell"]["ip"],
                                     cs_user=data["cloudshell"]["user"],
                                     cs_password=data["cloudshell"]["password"],
                                     snmp_community_strings=data["community-strings"],
                                     cli_credentials=cli_creds)
