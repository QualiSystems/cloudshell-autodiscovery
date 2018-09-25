from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.api.common_cloudshell_api import CloudShellAPIError

from autodiscovery.common.consts import CloudshellAPIErrorCodes
from autodiscovery.exceptions import AutoDiscoveryException
from autodiscovery.output import EmptyOutput


class ConnectPortsCommand(object):
    def __init__(self, report, logger, output=None):
        """

        :param output:
        """
        if output is None:
            output = EmptyOutput()

        self.report = report
        self.output = output
        self.logger = logger
        self._cs_sessions = {}

    # TODO: this code is duplicated !!!!
    def _init_cs_session(self, cs_ip, cs_user, cs_password, cs_domain):
        """Initialize CloudShell session

        :param str cs_ip:
        :param str cs_user:
        :param str cs_password:
        :rtype: CloudShellAPISession
        """
        try:
            cs_session = CloudShellAPISession(host=cs_ip, username=cs_user, password=cs_password, domain=cs_domain)
        except CloudShellAPIError as e:
            if e.code in (CloudshellAPIErrorCodes.INCORRECT_LOGIN, CloudshellAPIErrorCodes.INCORRECT_PASSWORD):
                self.logger.exception("Unable to login to the CloudShell API")
                raise AutoDiscoveryException("Wrong CloudShell user/password")
            raise
        except Exception:
            self.logger.exception("Unable to connect to the CloudShell API")
            raise AutoDiscoveryException("CloudShell server is unreachable")

        return cs_session

    # TODO: this code is duplicated !!!!
    def _get_cs_session(self, cs_ip, cs_user, cs_password, cs_domain):
        """

        :param cs_ip:
        :param cs_user:
        :param cs_password:
        :param cs_domain:
        :return:
        """
        if cs_domain not in self._cs_sessions:
            cs_session = self._init_cs_session(cs_ip=cs_ip,
                                               cs_user=cs_user,
                                               cs_password=cs_password,
                                               cs_domain=cs_domain)

            self._cs_sessions[cs_domain] = cs_session

        return self._cs_sessions[cs_domain]

    def execute(self, parsed_entries, cs_ip, cs_user, cs_password):
        """

        :param list[autodiscovery.reports.connections.base.Entry] parsed_entries:
        :param str cs_ip:
        :param str cs_user:
        :param str cs_password:
        :return:
        """
        for parsed_entry in parsed_entries:
            self.logger.info("Processing connection between port {} and {}".format(parsed_entry.source_port,
                                                                                   parsed_entry.target_port))

            try:
                with self.report.edit_entry(entry=parsed_entry) as entry:

                    if entry.status == entry.SUCCESS_STATUS:
                        continue

                    entry.status = entry.SUCCESS_STATUS

                    cs_session = self._get_cs_session(cs_ip=cs_ip,
                                                      cs_user=cs_user,
                                                      cs_password=cs_password,
                                                      cs_domain=entry.domain)

                    cs_session.UpdatePhysicalConnection(resourceAFullPath=parsed_entry.source_port,
                                                        resourceBFullPath=parsed_entry.target_port)

            except Exception:
                self.output.send("Failed to connect port {} and {}. {}".format(parsed_entry.source_port,
                                                                               parsed_entry.target_port,
                                                                               parsed_entry.comment), error=True)
                self.logger.exception("Failed to connect ports due to:")
            else:
                msg = "Connection between port {} and port {} was successfully processed".format(
                    parsed_entry.source_port,
                    parsed_entry.target_port)

                self.output.send(msg)
                self.logger.info(msg)

        self.report.generate()
