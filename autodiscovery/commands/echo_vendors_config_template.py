import click

from autodiscovery import config
from autodiscovery.common import utils


class EchoVendorsConfigTemplateCommand(object):
    def execute(self, template_format, save_to_file=None):
        """Execute echo user input file command

        :param str template_format: format of the template file (json)
        :param str save_to_file: file name to save generated template in
        :return:
        """
        file_name = utils.get_full_path(config.EXAMPLES_FOLDER, config.VENDORS_CONFIG_EXAMPLE_FILE)

        with open(file_name) as template_file:
            file_data = template_file.read()

        if save_to_file is None:
            click.echo(file_data)
        else:
            with open(save_to_file, "w") as template_file:
                template_file.write(file_data)
