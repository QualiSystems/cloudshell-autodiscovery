from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.api.common_cloudshell_api import CloudShellAPIError

from autodiscovery.common.consts import CloudshellAPIErrorCodes
from autodiscovery.exceptions import AutoDiscoveryException


class CloudShellSessionManager(object):
    def __init__(self, cs_ip, cs_user, cs_password, logger):
        """

        :param str cs_ip:
        :param str cs_user:
        :param str cs_password:
        :param logging.Logger logger:
        """
        self._cs_ip = cs_ip
        self._cs_user = cs_user
        self._cs_password = cs_password
        self._logger = logger
        self._cs_sessions = {}

    def _init_cs_session(self, cs_domain):
        """Initialize CloudShell session

        :param str cs_domain:
        :rtype: CloudShellAPISession
        """
        try:
            cs_session = CloudShellAPISession(host=self._cs_ip,
                                              username=self._cs_user,
                                              password=self._cs_password,
                                              domain=cs_domain)
        except CloudShellAPIError as e:
            if e.code in (CloudshellAPIErrorCodes.INCORRECT_LOGIN, CloudshellAPIErrorCodes.INCORRECT_PASSWORD):
                self._logger.exception("Unable to login to the CloudShell API")
                raise AutoDiscoveryException("Wrong CloudShell user/password")
            raise
        except Exception:
            self._logger.exception("Unable to connect to the CloudShell API")
            raise AutoDiscoveryException("CloudShell server is unreachable")

        return cs_session

    def get_session(self, cs_domain):
        """

        :param str cs_domain: CloudShell Domain
        :return:
        """
        if cs_domain not in self._cs_sessions:
            self._cs_sessions[cs_domain] = self._init_cs_session(cs_domain=cs_domain)

        return self._cs_sessions[cs_domain]
