import json
import pkg_resources

import click
from openpyxl import load_workbook

from autodiscovery import commands
from autodiscovery import reports
from autodiscovery.common.utils import get_logger
from autodiscovery.data_processors import JsonDataProcessor
from autodiscovery.input_data_parsers import get_input_data_parser
from autodiscovery.reports.base import Entry


@click.group()
def cli():
    pass


@cli.command()
def version():
    """Get version of the CloudShell Autodiscovery CLI tool"""
    click.echo(pkg_resources.get_distribution("cloudshell-autodiscovery").version)


@cli.command(name="update-vendor-data")
@click.option("--url", help="URL for file with private enterprise numbers")
@click.option("--log-file", help="File name for logs")
def update_vendor_data(url, log_file):
    """Update file with vendor enterprise numbers data"""
    update_vendor_data_command = commands.UpdateVendorsCommand(data_processor=JsonDataProcessor(),
                                                               logger=get_logger(log_file))
    update_vendor_data_command.execute(url=url)


@cli.command(name="echo-input-template")
@click.option("--template-format", help="Format of the generated user input template file",
              type=click.Choice(["yml", "json"]), default="yml")
@click.option("--save-to-file", help="File to save generated user input template file")
def echo_input_template(template_format, save_to_file):
    """Generate user input example file in the given format"""
    echo_input_tpl_command = commands.EchoUserInputTemplateCommand()
    echo_input_tpl_command.execute(template_format=template_format, save_to_file=save_to_file)


@cli.command(name="echo-vendors-configuration-template")
@click.option("--template-format", help="Format of the generated user input template file",
              type=click.Choice(["json"]), default="json")
@click.option("--save-to-file", help="File to save generated user input template file")
def echo_vendors_config_template(template_format, save_to_file):
    """Generate vendors configuration example file in the given format"""
    echo_conf_tpl_command = commands.EchoVendorsConfigTemplateCommand()
    echo_conf_tpl_command.execute(template_format=template_format, save_to_file=save_to_file)


@cli.command()
@click.option("--input-file", required=True, help="Input file with devices IPs and other configuration data. "
                                                  "Can be generated with a 'echo-input-template' command")
@click.option("--config-file", help="Vendors configuration file with additional data. Can be generated with a "
                                    "'echo-vendors-configuration-template' command")
@click.option("--log-file", help="File name for logs")
@click.option("--report-file", help="Type for generated report")
@click.option("--report-type", type=click.Choice(reports.REPORT_TYPES), default=reports.DEFAULT_REPORT_TYPE,
              help="File name for generated report")
@click.option("--offline", is_flag=True, help="Generate report without creation of any Resource on the CloudShell")
def run(input_file, config_file, log_file, report_file, report_type, offline):
    """Run Auto discovery command with given arguments from the input file"""
    parser = get_input_data_parser(input_file)
    input_data_model = parser.parse(input_file)
    additional_vendors_data = parse_config(config_file)
    report = reports.get_report(report_file=report_file, report_type=report_type)

    auto_discover_command = commands.RunCommand(data_processor=JsonDataProcessor(),
                                                         report=report,
                                                         logger=get_logger(log_file),
                                                         offline=offline)

    auto_discover_command.execute(devices_ips=input_data_model.devices_ips,
                                  snmp_comunity_strings=input_data_model.snmp_community_strings,
                                  cli_credentials=input_data_model.cli_credentials,
                                  cs_ip=input_data_model.cs_ip,
                                  cs_user=input_data_model.cs_user,
                                  cs_password=input_data_model.cs_password,
                                  additional_vendors_data=additional_vendors_data)


@cli.command(name="run-from-report")
@click.option("--input-file", required=True, help="Input file with CloudShell configuration data. "
                                                  "Can be generated with a 'echo-input-template' command")
@click.option("--config-file", help="Vendors configuration file with additional data. Can be generated with a "
                                    "'echo-vendors-configuration-template' command")
@click.option("--log-file", help="File name for logs")
@click.option("--report-file", required=True, help="Type for generated report")
def run_from_report(input_file, config_file, log_file, report_file):
    """Create and autoload CloudShell resources from the generated report"""
    parser = get_input_data_parser(input_file)
    input_data_model = parser.parse(input_file)
    additional_vendors_data = parse_config(config_file)
    devices_data = parse_report(report_file)

    # ??????
    # report = reports.get_report(report_file=report_file)
    # devices_data = report.load_from_file()

    command = commands.RunFromReportCommand(
        data_processor=JsonDataProcessor(),
        report=reports.get_report(report_file=report_file, report_type=reports.DEFAULT_REPORT_TYPE),
        logger=get_logger(log_file),
        offline=False)

    command.execute(device_models=devices_data,
                    cs_ip=input_data_model.cs_ip,
                    cs_user=input_data_model.cs_user,
                    cs_password=input_data_model.cs_password,
                    additional_vendors_data=additional_vendors_data)


def parse_config(config_file):
    # todo: rework this
    if config_file is not None:
        with open(config_file) as f:
            return json.load(f)

    return []


def parse_report(report_file):
    # todo: use same lib for read/write excel, rework this
    entries = []
    wb = load_workbook(report_file)
    wb_sheet = wb.active

    for row in wb_sheet.rows:
        args = [cell.value for cell in row]  # todo: get arguments by their name somehow

        entry = reports.base.Entry(ip=args[0],
                                   vendor=args[1],
                                   sys_object_id=args[2],
                                   description=args[3],
                                   snmp_community=args[4],
                                   user=args[5],
                                   password=args[6],
                                   enable_password=args[7],
                                   model_type=args[8],
                                   device_name=args[9],
                                   status=args[10],
                                   comment=args[11])

        entries.append(entry)

    return entries[1:]  # first row is a header
