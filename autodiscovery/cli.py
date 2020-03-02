import asyncio
from functools import wraps

import pkg_resources

import click

from autodiscovery import commands, config
from autodiscovery.common.consts import ASYNCIO_CONCURRENCY_LIMIT
from autodiscovery.common.cs_session_manager import CloudShellSessionManager
from autodiscovery.common.utils import get_logger
from autodiscovery.data_processors import JsonDataProcessor
from autodiscovery.output import TqdmOutput
from autodiscovery.parsers.config_data_parsers import get_config_data_parser
from autodiscovery.parsers.input_data_parsers import get_input_data_parser
from autodiscovery.reports import connections as connections_reports
from autodiscovery.reports import discovery as discovery_reports


def coroutine(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.group()
def cli():
    pass


@cli.command()
def version():
    """Get version of the CloudShell Autodiscovery CLI tool."""
    click.echo(pkg_resources.get_distribution("cloudshell-autodiscovery").version)


@cli.command(name="update-vendor-data")
@click.option("-u", "--url", help="URL for file with private enterprise numbers")
@click.option("-l", "--log-file", help="File name for logs")
def update_vendor_data(url, log_file):
    """Update file with vendor enterprise numbers data."""
    logger = get_logger(log_file)

    update_vendor_data_command = commands.UpdateVendorsCommand(
        data_processor=JsonDataProcessor(logger=logger), logger=logger
    )
    update_vendor_data_command.execute(url=url)


@cli.command(name="echo-input-template")
@click.option(
    "-t",
    "--template-format",
    help="Format of the generated user input template file",
    type=click.Choice(["yml", "json"]),
    default="yml",
)
@click.option(
    "-f", "--save-to-file", help="File to save generated user input template file"
)
def echo_input_template(template_format, save_to_file):
    """Generate user input example file in the given format."""
    echo_input_tpl_command = commands.EchoUserInputTemplateCommand()
    echo_input_tpl_command.execute(
        template_format=template_format, save_to_file=save_to_file
    )


@cli.command(name="echo-vendors-configuration-template")
@click.option(
    "-t",
    "--template-format",
    help="Format of the generated user input template file",
    type=click.Choice(["json"]),
    default="json",
)
@click.option(
    "-f", "--save-to-file", help="File to save generated user input template file"
)
def echo_vendors_config_template(template_format, save_to_file):
    """Generate vendors configuration example file in the given format."""
    echo_conf_tpl_command = commands.EchoVendorsConfigTemplateCommand()
    echo_conf_tpl_command.execute(
        template_format=template_format, save_to_file=save_to_file
    )


@cli.command(name="echo-discovery-report-template")
@click.option(
    "-f", "--save-to-file", required=True, help="File to save generated template file"
)
@click.option(
    "-t",
    "--report-type",
    type=click.Choice(discovery_reports.EDITABLE_REPORT_TYPES),
    default=discovery_reports.DEFAULT_REPORT_TYPE,
    help="Type for generated report",
)
def echo_discovery_report_template(save_to_file, report_type):
    """Generate csv|xlsx report example file for the "run-from-report" command."""
    report = discovery_reports.get_report(
        report_file=save_to_file, report_type=report_type
    )
    echo_report_tpl_command = commands.EchoReportTemplateCommand(report=report)
    echo_report_tpl_command.execute()


@cli.command(name="echo-connections-report-template")
@click.option(
    "-f",
    "--save-to-file",
    required=True,
    help="File to save generated user input template file",
)
@click.option(
    "-t",
    "--report-type",
    type=click.Choice(connections_reports.EDITABLE_REPORT_TYPES),
    default=connections_reports.DEFAULT_REPORT_TYPE,
    help="Type for generated report",
)
def echo_connections_report_template(save_to_file, report_type):
    """Generate csv|xlsx report example file for the "connect-ports" command."""
    report = connections_reports.get_report(
        report_file=save_to_file, report_type=report_type
    )
    echo_report_tpl_command = commands.EchoConnectionsTemplateCommand(report=report)
    echo_report_tpl_command.execute()


@cli.command()
@coroutine
@click.option(
    "-i",
    "--input-file",
    required=True,
    help="Input file with devices IPs and other configuration data. "
    "Can be generated with a 'echo-input-template' command",
)
@click.option(
    "-c",
    "--config-file",
    help="Vendors configuration file with additional data. Can be generated with a "
    "'echo-vendors-configuration-template' command",
)
@click.option("-l", "--log-file", help="File name for logs")
@click.option("-r", "--report-file", help="File name for generated report")
@click.option(
    "-t",
    "--report-type",
    type=click.Choice(discovery_reports.REPORT_TYPES),
    default=discovery_reports.DEFAULT_REPORT_TYPE,
    help="Type for generated report",
)
@click.option(
    "-o",
    "--offline",
    is_flag=True,
    help="Generate report without creation of any Resource on the CloudShell",
)
@click.option(
    "-a/-na",
    "--autoload/--no-autoload",
    help="Whether autoload discovered resource on the CloudShell or " "not",
    default=True,
)
@click.option(
    "-w",
    "--workers",
    default=ASYNCIO_CONCURRENCY_LIMIT,
    show_default=True,
    help="The number of concurrent devices discovering",
)
async def run(
    input_file,
    config_file,
    log_file,
    report_file,
    report_type,
    offline,
    autoload,
    workers,
):
    """Run Auto discovery command with given arguments from the input file."""
    input_data_parser = get_input_data_parser(input_file)
    input_data_model = input_data_parser.parse(input_file)
    logger = get_logger(log_file)

    if config_file is None:
        additional_vendors_data = []
    else:
        config_data_parser = get_config_data_parser(config_file)
        additional_vendors_data = config_data_parser.parse(config_file)

    report = discovery_reports.get_report(
        report_file=report_file, report_type=report_type
    )
    cs_session_manager = CloudShellSessionManager(
        cs_ip=input_data_model.cs_ip,
        cs_user=input_data_model.cs_user,
        cs_password=input_data_model.cs_password,
        logger=logger,
    )

    auto_discover_command = commands.RunCommand(
        data_processor=JsonDataProcessor(logger=logger),
        report=report,
        logger=logger,
        cs_session_manager=cs_session_manager,
        output=TqdmOutput(),
        offline=offline,
        autoload=autoload,
        workers_num=workers,
    )

    await auto_discover_command.execute(
        devices_ips=input_data_model.devices_ips,
        snmp_comunity_strings=input_data_model.snmp_community_strings,
        vendor_settings=input_data_model.vendor_settings,
        additional_vendors_data=additional_vendors_data,
    )


@cli.command(name="run-from-report")
@coroutine
@click.option(
    "-i",
    "--input-file",
    required=True,
    help="Input file with CloudShell configuration data. Can be "
    "generated with a 'echo-input-template' command",
)
@click.option(
    "-c",
    "--config-file",
    help="Vendors configuration file with additional data. Can be generated with a "
    "'echo-vendors-configuration-template' command",
)
@click.option("-l", "--log-file", help="File name for logs")
@click.option(
    "-r", "--report-file", required=True, help="File name of the report to run from"
)
@click.option(
    "-a/-na",
    "--autoload/--no-autoload",
    help="Whether autoload discovered resource on the CloudShell " "or not",
    default=True,
)
@click.option(
    "-w",
    "--workers",
    default=ASYNCIO_CONCURRENCY_LIMIT,
    show_default=True,
    help="The number of concurrent devices discovering",
)
async def run_from_report(
    input_file, config_file, log_file, report_file, autoload, workers
):
    """Create and autoload CloudShell resources from the generated report."""
    input_data_parser = get_input_data_parser(input_file)
    input_data_model = input_data_parser.parse(input_file)
    logger = get_logger(log_file)

    if config_file is None:
        additional_vendors_data = []
    else:
        config_data_parser = get_config_data_parser(config_file)
        additional_vendors_data = config_data_parser.parse(config_file)

    report = discovery_reports.parse_report(report_file=report_file)
    cs_session_manager = CloudShellSessionManager(
        cs_ip=input_data_model.cs_ip,
        cs_user=input_data_model.cs_user,
        cs_password=input_data_model.cs_password,
        logger=logger,
    )

    command = commands.RunFromReportCommand(
        data_processor=JsonDataProcessor(logger=logger),
        report=report,
        logger=logger,
        cs_session_manager=cs_session_manager,
        output=TqdmOutput(),
        autoload=autoload,
        workers_num=workers,
    )

    await command.execute(additional_vendors_data=additional_vendors_data)


@cli.command(name="connect-ports")
@coroutine
@click.option(
    "-i",
    "--input-file",
    required=True,
    help="Input file with CloudShell configuration data. Can be "
    "generated with a 'echo-input-template' command",
)
@click.option(
    "-n",
    "--resources-names",
    required=True,
    help="The names of the resources for which connections will be "
    "created based on the 'adjacent' attribute. it can be a "
    "single name or comma-separated names",
)
@click.option(
    "-d", "--domain", help="CloudShell domain", default=config.DEFAULT_CLOUDSHELL_DOMAIN
)
@click.option(
    "-o",
    "--offline",
    is_flag=True,
    help="Generate report without creation of any connections " "on the CloudShell",
)
@click.option("-r", "--connections-report-file", help="File name for generated report")
@click.option(
    "-t",
    "--connections-report-type",
    type=click.Choice(connections_reports.REPORT_TYPES),
    default=connections_reports.DEFAULT_REPORT_TYPE,
    help="Type for generated report",
)
@click.option("-l", "--log-file", help="File name for logs")
@click.option(
    "-w",
    "--workers",
    default=ASYNCIO_CONCURRENCY_LIMIT,
    show_default=True,
    help="The number of concurrent devices discovering",
)
async def connect_ports(
    input_file,
    resources_names,
    domain,
    offline,
    connections_report_file,
    connections_report_type,
    log_file,
    workers,
):
    """Create connections between CloudShell Port resources.

    Command will create connections based on the "Adjacent" attributes
    """
    input_data_parser = get_input_data_parser(input_file)
    input_data_model = input_data_parser.parse(input_file)
    logger = get_logger(log_file)

    cs_session_manager = CloudShellSessionManager(
        cs_ip=input_data_model.cs_ip,
        cs_user=input_data_model.cs_user,
        cs_password=input_data_model.cs_password,
        logger=logger,
    )

    command = commands.ConnectPortsCommand(
        cs_session_manager=cs_session_manager,
        report=connections_reports.get_report(
            report_file=connections_report_file, report_type=connections_report_type
        ),
        offline=offline,
        logger=logger,
        workers_num=workers,
        output=TqdmOutput(),
    )

    resources_names = [name.strip() for name in resources_names.split(",")]
    await command.execute(resources_names=resources_names, domain=domain)


@cli.command(name="connect-ports-from-report")
@coroutine
@click.option(
    "-i",
    "--input-file",
    required=True,
    help="Input file with CloudShell configuration data. "
    "Can be generated with a 'echo-input-template' command",
)
@click.option(
    "-r",
    "--connections-report-file",
    required=True,
    help="File with port connections data. Can be generated"
    " with 'echo-excel-connections-report-template' "
    "command",
)
@click.option("-l", "--log-file", help="File name for logs")
@click.option(
    "-w",
    "--workers",
    default=ASYNCIO_CONCURRENCY_LIMIT,
    show_default=True,
    help="The number of concurrent devices discovering",
)
async def connect_ports_from_report(
    input_file, connections_report_file, log_file, workers
):
    """Create connections between CloudShell Port resources."""
    input_data_parser = get_input_data_parser(input_file)
    input_data_model = input_data_parser.parse(input_file)
    logger = get_logger(log_file)

    report = connections_reports.parse_report(report_file=connections_report_file)
    cs_session_manager = CloudShellSessionManager(
        cs_ip=input_data_model.cs_ip,
        cs_user=input_data_model.cs_user,
        cs_password=input_data_model.cs_password,
        logger=logger,
    )

    command = commands.ConnectPortsFromReportCommand(
        cs_session_manager=cs_session_manager,
        report=report,
        logger=logger,
        workers_num=workers,
        output=TqdmOutput(),
    )

    await command.execute()
