import pkg_resources

import click

from autodiscovery.commands import AutoDiscoverCommand
from autodiscovery.commands import EchoUserInputTemplateCommand
from autodiscovery.commands import UpdateVendorsCommand
from autodiscovery.data_processors import JsonDataProcessor
from autodiscovery.input_data_parsers import get_input_data_parser
from autodiscovery.reports import ConsoleReport


@click.group()
def cli():
    pass


@cli.command()
def version():
    """Get version of the CloudShell Autodiscovery CLI tool"""
    click.echo(pkg_resources.get_distribution('cloudshell-autodiscovery').version)


@cli.command(name="update-vendor-data")
@click.option('--url', help='URL for file with private enterprise numbers')
def update_vendor_data(url):
    """Update file with vendor enterprise numbers data"""
    update_vendor_data_command = UpdateVendorsCommand(data_processor=JsonDataProcessor())
    update_vendor_data_command.execute(url=url)


@cli.command(name="echo-user-input-template")
@click.option('--template-format', help='Format of the generated user input template file',
              type=click.Choice(['yml', 'json']), default="yml")
@click.option('--save-to-file', help='File to save generated user input template file')
def echo_user_input_template(template_format, save_to_file):
    """Generate user input example file in the given format"""
    auto_discover_command = EchoUserInputTemplateCommand()
    auto_discover_command.execute(template_format=template_format, save_to_file=save_to_file)


@cli.command()
@click.option('--input-file', required=True, help='Input file with devices IPs and other configuration data. '
                                                  'Can be generated with a "echo-user-input-template" command')
def run(input_file):
    """Run Auto discovery command with given arguments from the input file"""
    parser = get_input_data_parser(input_file)
    input_data_model = parser.parse(input_file)
    auto_discover_command = AutoDiscoverCommand(data_processor=JsonDataProcessor(),
                                                report=ConsoleReport())

    auto_discover_command.execute(devices_ips=input_data_model.devices_ips,
                                  snmp_comunity_strings=input_data_model.snmp_community_strings,
                                  cli_credentials=input_data_model.cli_credentials,
                                  cs_ip=input_data_model.cs_ip,
                                  cs_user=input_data_model.cs_user,
                                  cs_password=input_data_model.cs_password)
