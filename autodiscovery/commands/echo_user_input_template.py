import logging

import click
import json
import yaml

from autodiscovery import config


logging.basicConfig(level=logging.INFO)


class EchoUserInputTemplateCommand(object):
    def execute(self, template_format, save_to_file=None):
        """Execute Update vendors command

        :param str save_to_file: URL for the vendor private enterprise numbers
        :return:
        """
        with open(config.USER_INPUT_EXAMPLE_FILE) as template_file:
            file_data = template_file.read()

        if template_format == "json":
            file_data = json.dumps(yaml.load(file_data), indent=4, sort_keys=True)

        if save_to_file is None:
            click.echo(file_data)
        else:
            with open(save_to_file, "w") as template_file:
                template_file.write(file_data)
