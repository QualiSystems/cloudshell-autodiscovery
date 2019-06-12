import pkg_resources

import click

from autodiscovery import commands
from autodiscovery import config
from autodiscovery import reports
from autodiscovery.common.cs_session_manager import CloudShellSessionManager
from autodiscovery.common.utils import get_logger
from autodiscovery.data_processors import JsonDataProcessor
from autodiscovery.output import ConsoleOutput
from autodiscovery.parsers.config_data_parsers import get_config_data_parser
from autodiscovery.parsers.input_data_parsers import get_input_data_parser


@click.group()
def cli():
    pass


@cli.command()
def version():
    """Get version of the CloudShell Autodiscovery CLI tool"""
    click.echo(pkg_resources.get_distribution("cloudshell-autodiscovery").version)


@cli.command(name="update-vendor-data")
@click.option("-u", "--url", help="URL for file with private enterprise numbers")
@click.option("-l", "--log-file", help="File name for logs")
def update_vendor_data(url, log_file):
    """Update file with vendor enterprise numbers data"""
    logger = get_logger(log_file)

    update_vendor_data_command = commands.UpdateVendorsCommand(data_processor=JsonDataProcessor(logger=logger),
                                                               logger=logger)
    update_vendor_data_command.execute(url=url)


@cli.command(name="echo-input-template")
@click.option("-t", "--template-format", help="Format of the generated user input template file",
              type=click.Choice(["yml", "json"]), default="yml")
@click.option("-f", "--save-to-file", help="File to save generated user input template file")
def echo_input_template(template_format, save_to_file):
    """Generate user input example file in the given format"""
    echo_input_tpl_command = commands.EchoUserInputTemplateCommand()
    echo_input_tpl_command.execute(template_format=template_format, save_to_file=save_to_file)


@cli.command(name="echo-vendors-configuration-template")
@click.option("-t", "--template-format", help="Format of the generated user input template file",
              type=click.Choice(["json"]), default="json")
@click.option("-f", "--save-to-file", help="File to save generated user input template file")
def echo_vendors_config_template(template_format, save_to_file):
    """Generate vendors configuration example file in the given format"""
    echo_conf_tpl_command = commands.EchoVendorsConfigTemplateCommand()
    echo_conf_tpl_command.execute(template_format=template_format, save_to_file=save_to_file)


@cli.command(name="echo-excel-report-template")
@click.option("-f", "--save-to-file", required=True, help="File to save generated template file")
def echo_excel_report_template(save_to_file):
    """Generate .xlsx report example file for the "run-from-report" command"""
    report = reports.discovery.ExcelReport(file_name=save_to_file)
    echo_report_tpl_command = commands.EchoReportTemplateCommand(report=report)
    echo_report_tpl_command.execute()


@cli.command(name="echo-excel-connections-report-template")
@click.option("-f", "--save-to-file", required=True, help="File to save generated user input template file")
def echo_excel_connections_template(save_to_file):
    """Generate .xlsx report example file for the "connect-ports" command"""
    report = reports.connections.ExcelReport(file_name=save_to_file)
    echo_report_tpl_command = commands.EchoConnectionsTemplateCommand(report=report)
    echo_report_tpl_command.execute()


@cli.command()
@click.option("-i", "--input-file", required=True, help="Input file with devices IPs and other configuration data. "
                                                        "Can be generated with a 'echo-input-template' command")
@click.option("-c", "--config-file", help="Vendors configuration file with additional data. Can be generated with a "
                                          "'echo-vendors-configuration-template' command")
@click.option("-l", "--log-file", help="File name for logs")
@click.option("-r", "--report-file", help="File name for generated report")
@click.option("-t", "--report-type", type=click.Choice(reports.discovery.REPORT_TYPES),
              default=reports.discovery.DEFAULT_REPORT_TYPE,
              help="Type for generated report")
@click.option("-o", "--offline", is_flag=True, help="Generate report without creation of any Resource on the CloudShell")
@click.option("-a/-na", "--autoload/--no-autoload", help="Whether autoload discovered resource on the CloudShell or "
                                                         "not", default=True)
def run(input_file, config_file, log_file, report_file, report_type, offline, autoload):
    """Run Auto discovery command with given arguments from the input file"""
    input_data_parser = get_input_data_parser(input_file)
    input_data_model = input_data_parser.parse(input_file)
    logger = get_logger(log_file)

    if config_file is None:
        additional_vendors_data = []
    else:
        config_data_parser = get_config_data_parser(config_file)
        additional_vendors_data = config_data_parser.parse(config_file)

    report = reports.discovery.get_report(report_file=report_file, report_type=report_type)

    cs_session_manager = CloudShellSessionManager(cs_ip=input_data_model.cs_ip,
                                                  cs_user=input_data_model.cs_user,
                                                  cs_password=input_data_model.cs_password,
                                                  logger=logger)

    auto_discover_command = commands.RunCommand(data_processor=JsonDataProcessor(logger=logger),
                                                report=report,
                                                logger=logger,
                                                cs_session_manager=cs_session_manager,
                                                output=ConsoleOutput(),
                                                offline=offline,
                                                autoload=autoload)

    auto_discover_command.execute(devices_ips=input_data_model.devices_ips,
                                  snmp_comunity_strings=input_data_model.snmp_community_strings,
                                  vendor_settings=input_data_model.vendor_settings,
                                  additional_vendors_data=additional_vendors_data)


@cli.command(name="run-from-report")
@click.option("-i", "--input-file", required=True, help="Input file with CloudShell configuration data. Can be "
                                                        "generated with a 'echo-input-template' command")
@click.option("-c", "--config-file", help="Vendors configuration file with additional data. Can be generated with a "
                                          "'echo-vendors-configuration-template' command")
@click.option("-l", "--log-file", help="File name for logs")
@click.option("-r", "--report-file", required=True, help="File name of the report to run from")
@click.option("-a/-na", "--autoload/--no-autoload", help="Whether autoload discovered resource on the CloudShell "
                                                         "or not", default=True)
def run_from_report(input_file, config_file, log_file, report_file, autoload):
    """Create and autoload CloudShell resources from the generated report"""
    input_data_parser = get_input_data_parser(input_file)
    input_data_model = input_data_parser.parse(input_file)
    logger = get_logger(log_file)

    if config_file is None:
        additional_vendors_data = []
    else:
        config_data_parser = get_config_data_parser(config_file)
        additional_vendors_data = config_data_parser.parse(config_file)

    report = reports.discovery.parse_report(report_file=report_file)

    cs_session_manager = CloudShellSessionManager(cs_ip=input_data_model.cs_ip,
                                                  cs_user=input_data_model.cs_user,
                                                  cs_password=input_data_model.cs_password,
                                                  logger=logger)

    command = commands.RunFromReportCommand(data_processor=JsonDataProcessor(logger=logger),
                                            report=report,
                                            logger=logger,
                                            cs_session_manager=cs_session_manager,
                                            output=ConsoleOutput(),
                                            autoload=autoload)

    command.execute(additional_vendors_data=additional_vendors_data)


@cli.command(name="connect-ports")
@click.option("-i", "--input-file", required=True, help="Input file with CloudShell configuration data. Can be "
                                                        "generated with a 'echo-input-template' command")
@click.option("-n", "--resources-names", required=True, help="The names of the resources for which connections will be "
                                                             "created based on the 'adjacent' attribute. it can be a "
                                                             "single name or comma-separated names")
@click.option("-d", "--domain", help="CloudShell domain", default=config.DEFAULT_CLOUDSHELL_DOMAIN)
@click.option("-o", "--offline", is_flag=True, help="Generate report without creation of any connections "
                                                    "on the CloudShell")
@click.option("-r", "--connections-report-file", help="File name for generated report")
@click.option("-t", "--connections-report-type", type=click.Choice(reports.connections.REPORT_TYPES),
              default=reports.connections.DEFAULT_REPORT_TYPE,
              help="Type for generated report")
@click.option("-l", "--log-file", help="File name for logs")
def connect_ports(input_file, resources_names, domain, offline, connections_report_file,
                  connections_report_type, log_file):
    """Create connections between CloudShell Port resources based on the "Adjacent" attributes"""
    input_data_parser = get_input_data_parser(input_file)
    input_data_model = input_data_parser.parse(input_file)
    logger = get_logger(log_file)

    cs_session_manager = CloudShellSessionManager(cs_ip=input_data_model.cs_ip,
                                                  cs_user=input_data_model.cs_user,
                                                  cs_password=input_data_model.cs_password,
                                                  logger=logger)

    command = commands.ConnectPortsCommand(cs_session_manager=cs_session_manager,
                                           report=reports.connections.get_report(report_file=connections_report_file,
                                                                                 report_type=connections_report_type),
                                           offline=offline,
                                           logger=logger,
                                           output=ConsoleOutput())

    resources_names = [name.strip() for name in resources_names.split(",")]
    command.execute(resources_names=resources_names, domain=domain)


@cli.command(name="connect-ports-from-report")
@click.option("-i", "--input-file", required=True, help="Input file with CloudShell configuration data. "
                                                        "Can be generated with a 'echo-input-template' command")
@click.option("-r", "--connections-report-file", required=True, help="File with port connections data. Can be generated"
                                                                     " with 'echo-excel-connections-report-template' "
                                                                     "command")
@click.option("-l", "--log-file", help="File name for logs")
def connect_ports_from_report(input_file, connections_report_file, log_file):
    """Create connections between CloudShell Port resources specified in the connection file"""
    input_data_parser = get_input_data_parser(input_file)
    input_data_model = input_data_parser.parse(input_file)
    logger = get_logger(log_file)

    # todo: provide old report instead of creating new one?
    report = reports.connections.parse_report(report_file=connections_report_file)
    parsed_entries = report.parse_entries_from_file(connections_report_file)

    cs_session_manager = CloudShellSessionManager(cs_ip=input_data_model.cs_ip,
                                                  cs_user=input_data_model.cs_user,
                                                  cs_password=input_data_model.cs_password,
                                                  logger=logger)

    command = commands.ConnectPortsFromReportCommand(cs_session_manager=cs_session_manager,
                                                     report=reports.connections.get_report(
                                                         report_file=connections_report_file,
                                                         report_type=report.FILE_EXTENSION),
                                                     logger=logger,
                                                     output=ConsoleOutput())

    command.execute(parsed_entries=parsed_entries)
