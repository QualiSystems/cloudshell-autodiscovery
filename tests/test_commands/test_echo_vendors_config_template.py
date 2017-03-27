import unittest

import mock

from autodiscovery.commands import EchoVendorsConfigTemplateCommand


class TestEchoVendorsConfigTemplateCommand(unittest.TestCase):
    def setUp(self):
        self.echo_command = EchoVendorsConfigTemplateCommand()

    @mock.patch("autodiscovery.commands.echo_vendors_config_template.click")
    @mock.patch("autodiscovery.commands.echo_vendors_config_template.open")
    @mock.patch("autodiscovery.commands.echo_vendors_config_template.utils")
    def test_execute(self, utils, open, click):
        """Check that method will generate input data example in JSON format"""
        template_format = "json"
        example_file = "example template.json"
        utils.get_full_path.return_value = example_file
        file_data = mock.MagicMock()
        opened_file = mock.MagicMock()
        open.return_value = opened_file
        opened_file.__enter__().read.return_value = file_data
        # act
        self.echo_command.execute(template_format=template_format)
        # verify
        open.assert_called_once_with(example_file)
        click.echo.assert_called_once_with(file_data)

    @mock.patch("autodiscovery.commands.echo_vendors_config_template.click")
    @mock.patch("autodiscovery.commands.echo_vendors_config_template.open")
    @mock.patch("autodiscovery.commands.echo_vendors_config_template.utils")
    def test_execute_save_to_file(self, utils, open, click):
        """Check that method will save to file example template data"""
        template_format = "json"
        example_filename = "example template.json"
        utils.get_full_path.return_value = example_filename

        save_to_filename = "additional_config.json"
        example_file = mock.MagicMock()
        save_to_file = mock.MagicMock()
        open.side_effect = [example_file, save_to_file]
        # act
        self.echo_command.execute(template_format=template_format, save_to_file=save_to_filename)
        # verify
        example_file.__enter__().read.assert_called_once_with()
        save_to_file.__enter__().write.assert_called_once_with(example_file.__enter__().read())
