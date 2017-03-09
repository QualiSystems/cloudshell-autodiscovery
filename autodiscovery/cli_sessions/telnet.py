from collections import OrderedDict
import telnetlib

from cloudshell.cli.session.telnet_session import TelnetSession
from cloudshell.cli.session.telnet_session import TelnetSessionException

from autodiscovery.cli_sessions.base import AbstractDiscoverySession
from autodiscovery.models import CLICredentials


class TelnetDiscoverySession(TelnetSession, AbstractDiscoverySession):
    def __init__(self, host, port=None):
        super(TelnetDiscoverySession, self).__init__(host=host, port=port, username=None, password=None)
        self._handler = telnetlib.Telnet()

    def check_credentials(self, cli_credentials, default_prompt, enable_prompt, logger):
        """Connect to device through telnet

        :param autodiscovery.models.VendorCLICredentials cli_credentials: list of possible CLI credentials
        :param str default_prompt: prompt for the "default" mode
        :param str enable_prompt: prompt for the "enable" mode
        :param logging.Logger logger:
        :rtype: autodiscovery.models.CLICredentials
        """
        self._handler.open(self.host, int(self.port), self._timeout)

        if self._handler.get_socket() is None:
            raise TelnetSessionException(self.__class__.__name__, "Failed to open telnet connection.")

        try:
            self._handler.get_socket().send(telnetlib.IAC + telnetlib.WILL + telnetlib.ECHO)
            action_map = OrderedDict()
            valid_creds = CLICredentials()
            action_map['[Ll]ogin:|[Uu]ser:|[Uu]sername:'] = self.prepare_credentials_action_map(
                cli_credentials=cli_credentials,
                valid_creds=valid_creds,
                creds_key="user")

            action_map['[Pp]assword:'] = self.prepare_credentials_action_map(cli_credentials=cli_credentials,
                                                                             valid_creds=valid_creds,
                                                                             creds_key="password")

            re_prompts = "|".join([prompt for prompt in (default_prompt, enable_prompt) if prompt])
            output_str = self.hardware_expect(None,
                                              expected_string=re_prompts,
                                              timeout=self._timeout,
                                              logger=logger,
                                              action_map=action_map,
                                              check_action_loop_detector=False)

            return self._check_enable_password(enable_prompt=enable_prompt,
                                               cli_credentials=cli_credentials,
                                               valid_creds=valid_creds,
                                               output_str=output_str,
                                               logger=logger)

        finally:
            self._handler.close()
