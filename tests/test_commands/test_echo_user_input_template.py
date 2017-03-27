import unittest

import mock

from autodiscovery.commands import EchoUserInputTemplateCommand


class TestEchoUserInputTemplateCommand(unittest.TestCase):
    def setUp(self):
        self.echo_command = EchoUserInputTemplateCommand()

    @mock.patch("autodiscovery.commands.echo_user_input_template.click")
    @mock.patch("autodiscovery.commands.echo_user_input_template.json")
    @mock.patch("autodiscovery.commands.echo_user_input_template.yaml")
    @mock.patch("autodiscovery.commands.echo_user_input_template.open")
    @mock.patch("autodiscovery.commands.echo_user_input_template.utils")
    def test_execute_in_json_format(self, utils, open, yaml, json, click):
        """Check that method will generate input data example in JSON format"""
        template_format = "json"
        example_file = "example template.json"
        utils.get_full_path.return_value = example_file
        file_data = mock.MagicMock()
        opened_file = mock.MagicMock()
        json_data = mock.MagicMock()
        open.return_value = opened_file
        opened_file.__enter__().read.return_value = file_data
        json.dumps.return_value = json_data
        # act
        self.echo_command.execute(template_format=template_format)
        # verify
        open.assert_called_once_with(example_file)
        json.dumps.assert_called_once_with(yaml.load(file_data), indent=4, sort_keys=True)
        click.echo.assert_called_once_with(json_data)

    @mock.patch("autodiscovery.commands.echo_user_input_template.click")
    @mock.patch("autodiscovery.commands.echo_user_input_template.open")
    @mock.patch("autodiscovery.commands.echo_user_input_template.utils")
    def test_execute_in_yaml_format(self, utils, open, click):
        """Check that method will generate input data example in YAML format"""
        template_format = "yaml"
        example_file = "example template.yml"
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

    @mock.patch("autodiscovery.commands.echo_user_input_template.click")
    @mock.patch("autodiscovery.commands.echo_user_input_template.open")
    @mock.patch("autodiscovery.commands.echo_user_input_template.utils")
    def test_execute_save_to_file(self, utils, open, click):
        """Check that method will save to file example template data"""
        template_format = "yml"
        example_filename = "example template.yml"
        save_to_filename = "input.yml"
        utils.get_full_path.return_value = example_filename
        example_file = mock.MagicMock()
        save_to_file = mock.MagicMock()
        open.side_effect = [example_file, save_to_file]
        # act
        self.echo_command.execute(template_format=template_format, save_to_file=save_to_filename)
        # verify
        open.assert_any_call(example_filename)
        open.assert_any_call(save_to_filename, "w")
        example_file.__enter__().read.assert_called_once_with()
        save_to_file.__enter__().write.assert_called_once_with(example_file.__enter__().read())
