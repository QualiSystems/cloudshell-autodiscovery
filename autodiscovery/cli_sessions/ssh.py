import paramiko

from cloudshell.cli.session.ssh_session import SSHSession

from autodiscovery.cli_sessions.base import AbstractDiscoverySession
from autodiscovery.exceptions import AutoDiscoveryException


class SSHDiscoverySession(SSHSession, AbstractDiscoverySession):
    def __init__(self, host, port=None):
        super(SSHDiscoverySession, self).__init__(host=host, port=port, username=None, password=None)
        self._handler = paramiko.SSHClient()
        self._handler.load_system_host_keys()
        self._handler.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def check_credentials(self, cli_credentials, default_prompt, enable_prompt, logger):
        """Connect to device through SSH

        :param autodiscovery.models.VendorCLICredentials cli_credentials: list of possible CLI credentials
        :param str default_prompt: prompt for the "default" mode
        :param str enable_prompt: prompt for the "enable" mode
        :param logging.Logger logger:
        :rtype: autodiscovery.models.CLICredentials
        """
        for credentials in cli_credentials.cli_credentials:
            try:
                self._handler.connect(self.host,
                                      self.port,
                                      credentials.user,
                                      credentials.password,
                                      timeout=self._timeout,
                                      banner_timeout=30, allow_agent=False, look_for_keys=False)

                self._current_channel = self._handler.invoke_shell()
                self._current_channel.settimeout(self._timeout)

                re_prompts = "|".join([prompt for prompt in (default_prompt, enable_prompt) if prompt])
                output_str = self.hardware_expect(None,
                                                  expected_string=re_prompts,
                                                  timeout=self._timeout,
                                                  logger=logger)

                valid_creds = self._check_enable_password(enable_prompt=enable_prompt,
                                                          cli_credentials=cli_credentials,
                                                          valid_creds=credentials,
                                                          output_str=output_str,
                                                          logger=logger)
                return valid_creds

            except paramiko.AuthenticationException:
                logger.warning("Credentials {}/{} aren't valid for the device {} for SSH connection"
                               .format(credentials.user, credentials.password, self.host))
            finally:
                self._handler.close()

        raise AutoDiscoveryException("All given credentials aren't valid for the device {} for SSH connection"
                                     .format(self.host))
