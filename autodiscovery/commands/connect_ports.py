from cloudshell.api.cloudshell_api import AttributeNameValue

from autodiscovery.exceptions import ReportableException
from autodiscovery.output import EmptyOutput


ADJACENT_PORT_ATTRIBUTE = "Adjacent"
SYSTEM_NAME_PORT_ATTRIBUTE = "System Name"
PORT_FAMILY = "CS_Port"


class ConnectPortsCommand(object):
    def __init__(self, cs_session_manager, report, offline, logger, output=None):
        """

        :param cs_session_manager:
        :param report:
        :param offline:
        :param logger:
        :param output:
        """
        if output is None:
            output = EmptyOutput()

        self.cs_session_manager = cs_session_manager
        self.report = report
        self.offline = offline
        self.output = output
        self.logger = logger

    def _get_resource_attribute_value(self, resource, attribute_name):
        """

        :param resource cloudshell.api.cloudshell_api.ResourceInfo:
        :param str attribute_name:
        """
        for attribute in resource.ResourceAttributes:
            if attribute.Name.endswith(attribute_name):
                return attribute.Value

    def _find_ports(self, resource):
        """

        :param resource:
        :return:
        """
        ports = []
        for resource in resource.ChildResources:
            if resource.ResourceFamilyName == PORT_FAMILY:
                ports.append(resource)
            else:
                ports += self._find_ports(resource)

        return ports

    def _find_adjacent_ports(self, resource):
        """

        :param resource:
        :return:
        """
        adjacent_ports = []
        for port in self._find_ports(resource):
            adjacent = self._get_resource_attribute_value(resource=port,
                                                          attribute_name=ADJACENT_PORT_ATTRIBUTE)
            if adjacent:
                adjacent_ports.append((port.Name, adjacent))

        return adjacent_ports

    def _find_resource_by_sys_name(self, cs_session, sys_name):
        """

        :param cloudshell.api.cloudshell_api.CloudShellAPISession cs_session:
        :param sys_name:
        :return:
        """
        resources = []
        families = set([res.ResourceFamilyName for res in cs_session.GetResourceList().Resources])

        for family, sys_attr in [("", SYSTEM_NAME_PORT_ATTRIBUTE)] + [(family, "{}.{}".format(
                family, SYSTEM_NAME_PORT_ATTRIBUTE)) for family in families]:

            for res in cs_session.FindResources(resourceFamily=family,
                                                includeSubResources=False,
                                                attributeValues=[AttributeNameValue(Name=sys_attr,
                                                                                    Value=sys_name)]).Resources:
                # response may contain an empty result
                if res.ResourceFamilyName:
                    resources.append(res)

        if not resources:
            raise ReportableException("Unable to find resource with 'System Name' attribute: '{}'".format(sys_name))
        elif len(resources) > 1:
            raise ReportableException("Found several resources: {} with the same 'System Name' attribute: '{}'"
                                      .format([resource.Name for resource in resources], sys_name))

        return cs_session.GetResourceDetails(resources[0].FullName)

    def _find_port_by_adjacent_name(self, adjacent_resource, adjacent_port_name):
        """

        :param cloudshell.api.cloudshell_api.ResourceInfo adjacent_resource:
        :param str adjacent_port_name:
        :return:
        """
        adjacent_port_name = adjacent_port_name.replace(".", "-").replace("/", "-")

        for port in self._find_ports(adjacent_resource):
            port_name = port.Name.split("/")[-1]
            if port_name == adjacent_port_name:
                return port

        raise ReportableException("Unable to find Adjacent port '{}'".format(adjacent_port_name))

    def execute(self, resources_names, domain):
        """

        :param list[str] resources_names:
        :param str domain:
        :return:
        """
        cs_session = self.cs_session_manager.get_session(cs_domain=domain)

        for resource_name in resources_names:
            msg = "Updating physical connections for the resource '{}': ".format(resource_name)
            self.output.send(msg)
            self.logger.info(msg)

            try:
                resource = cs_session.GetResourceDetails(resource_name)
                for port, adjacent in self._find_adjacent_ports(resource):
                    self.output.send("\t- Updating physical connection for the port '{}' ".format(port))
                    self.logger.info("Processing port '{}' with adjacent '{}'".format(port, adjacent))

                    try:
                        with self.report.add_entry(resource_name=resource_name,
                                                   source_port=port,
                                                   adjacent=adjacent,
                                                   target_port="",
                                                   domain=domain,
                                                   offline=self.offline) as entry:

                            adjacent_sys_name, adjacent_port_name = [x.strip() for x in adjacent.split("through")]
                            adjacent_resource = self._find_resource_by_sys_name(cs_session=cs_session,
                                                                                sys_name=adjacent_sys_name)

                            adjacent_port = self._find_port_by_adjacent_name(adjacent_resource=adjacent_resource,
                                                                             adjacent_port_name=adjacent_port_name)

                            entry.target_port = adjacent_port.Name

                            if not self.offline:
                                cs_session.UpdatePhysicalConnection(resourceAFullPath=entry.source_port,
                                                                    resourceBFullPath=entry.target_port)

                    except ReportableException as e:
                        self.output.send("\t- Failed to update physical connection for the port '{}'. {}"
                                         .format(port, e), error=True)
                        self.logger.exception("Failed to update physical connection due to:")

                    except Exception:
                        self.output.send("\t- Failed to update physical connection for the port '{}' ".format(port),
                                         error=True)
                        self.logger.exception("Failed to update physical connection due to:")

            except Exception:
                self.output.send("Failed to update physical connections for the resource '{}'. See log for the details"
                                 .format(resource_name), error=True)
                self.logger.exception("Failed to update physical connections due to:")

            else:
                msg = "Physical connections for the resource '{}' were updated".format(resource_name)
                self.output.send(msg)
                self.logger.info(msg)

        self.report.generate()
