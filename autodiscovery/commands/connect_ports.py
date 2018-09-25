from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.api.common_cloudshell_api import CloudShellAPIError

from autodiscovery.common.consts import CloudshellAPIErrorCodes
from autodiscovery.exceptions import AutoDiscoveryException
from autodiscovery.output import EmptyOutput


class ConnectPortsCommand(object):
    def __init__(self, report, output=None):
        """

        :param output:
        """
        if output is None:
            output = EmptyOutput()

        self.report = report
        self.output = output
        self._cs_sessions = {}

    # TODO: THIS CODE IS DUPLICATED !!!!
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

        :param list[autodiscovery.reports.base.Entry] parsed_entries:
        :param str cs_ip:
        :param str cs_user:
        :param str cs_password:
        :return:
        """
        # for parsed_entry in parsed_entries:
        #     cs_session = self._get_cs_session(cs_ip=cs_ip,
        #                                       cs_user=cs_user,
        #                                       cs_password=cs_password,
        #                                       cs_domain="Global")
        #
        #     # cs_session.MapPorts("DUT/Chassis 1/Module 1/Port 2",
        #     #                     "DUT/Chassis 1/Module 1/Port 1", "bi")
        #
        #     cs_session.MapPorts("DUT/Chassis 1/Module 1/Port 1",
        #                         "Cisco ACI Ports Structure/Pod 1/Node 101/FEX 101/Slot 1/Port 11", "bi")
        #
        #     # todo: add overrideExistingConnections flag
        #     cs_session.UpdatePhysicalConnection(resourceAFullPath="DUT/Chassis 1/Module 1/Port 2",
        #                                         resourceBFullPath="Cisco ACI Ports Structure/Pod 1/Node 101/FEX 101/Slot 1/Port 11")
        #
        #     # def UpdatePhysicalConnection(self, resourceAFullPath='', resourceBFullPath='',
        #     #                              overrideExistingConnections=True):
        #     #     """
        #     #         Define a physical connection (cable link) between two resources.
        #     #
        #     #         :param str resourceAFullPath: Specify the resource name. You can also include the full path from the root to the resource before the resource name, separated by slashes. For example: FolderName/RouterA/Port1.
        #     #         :param str resourceBFullPath: Specify the resource name. You can also include the full path from the root to the resource before the resource name, separated by slashes. For example: FolderName/RouterA/Port1. You may leave this parameter blank if you wish to disconnect the existing source resource connection.
        #     #         :param bool overrideExistingConnections: Overriding existing connections will automatically remove existing physical connection if they conflict with the requested new connections. If set to 'No', an error message will be displayed if any port is already connected and the operation will be cancelled.
        #     #
        #     #         :rtype: str
        #     #     """
        #     #     return self.generateAPIRequest(OrderedDict(
        #     #         [('method_name', 'UpdatePhysicalConnection'), ('resourceAFullPath', resourceAFullPath),
        #     #          ('resourceBFullPath', resourceBFullPath),
        #     #          ('overrideExistingConnections', overrideExistingConnections)]))
        #
        #     def UpdatePhysicalConnections(self, physicalConnectionUpdateRequest=[], overrideExistingConnections=True):
        #
        #     import ipdb;ipdb.set_trace()

        for parsed_entry in parsed_entries:
            # self.logger.info("Uploading device with IP {}".format(parsed_entry.ip))
            # self.output.send("Uploading device with IP {}".format(parsed_entry.ip))

            try:
                with self.report.edit_entry(entry=parsed_entry) as entry:

                    if entry.status == entry.SUCCESS_STATUS:
                        continue
                    else:
                        entry.status = entry.SUCCESS_STATUS

                    vendor = vendor_config.get_vendor(vendor_name=parsed_entry.vendor)

                    if vendor is None:
                        raise ReportableException("Unsupported vendor {}".format(parsed_entry.vendor))

                    try:
                        handler = self.vendor_type_handlers_map[vendor.vendor_type.lower()]
                    except KeyError:
                        raise ReportableException("Invalid vendor type '{}'. Possible values are: {}"
                                                  .format(vendor.vendor_type, self.vendor_type_handlers_map.keys()))

                    cs_session = self._get_cs_session(cs_ip=cs_ip,
                                                      cs_user=cs_user,
                                                      cs_password=cs_password,
                                                      cs_domain=entry.domain)

                    handler.upload(entry=entry,  vendor=vendor, cs_session=cs_session)

            except Exception:
                self.output.send("Failed to discover {} device. {}".format(parsed_entry.ip,
                                                                           parsed_entry.comment), error=True)
                self.logger.exception("Failed to upload {} device due to:".format(parsed_entry.ip))
            else:
                self.output.send("Device with IP {} was successfully uploaded".format(parsed_entry.ip))
                self.logger.info("Device with IP {} was successfully uploaded".format(parsed_entry.ip))

        self.report.generate()
