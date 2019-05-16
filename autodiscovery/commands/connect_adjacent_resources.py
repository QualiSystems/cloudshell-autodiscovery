from autodiscovery.exceptions import ReportableException
from autodiscovery.output import EmptyOutput


class ConnectAdjacentResourcesCommand(object):
    def __init__(self, cs_session_manager, report, logger, output=None):
        """

        :param cs_session_manager:
        :param report:
        :param logger:
        :param output:
        """
        if output is None:
            output = EmptyOutput()

        self.cs_session_manager = cs_session_manager
        self.report = report
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
            if resource.ResourceFamilyName == "CS_Port":
                adjacent = self._get_resource_attribute_value(resource=resource,
                                                              attribute_name="Adjacent")

                if adjacent:
                    ports.append((resource.Name, adjacent))
            else:
                ports += self._find_ports(resource)

        return ports

    def _find_resource_by_sys_name(self, adjacent_device_name):
        pass

    def execute(self, resources_names, domain):
        """

        :param list[str] resources_names:
        :param str domain:
        :return:
        """
        cs_session = self.cs_session_manager.get_session(cs_domain=domain)

        for resource_name in resources_names:
            resource = cs_session.GetResourceDetails(resource_name)

            try:
                for port, adjacent in self._find_ports(resource):
                    adjacent_device_name, adjacent_port = [x.strip() for x in adjacent.split("through")]

                    # todo: 1) find correct resource by sys name
                    # todo: 2) create possible port names by replacing "/" in "-" or "."
                    # todo: 3) iterate over all resources to find needed port

                    adjacent_resource = self._find_resource_by_sys_name(adjacent_device_name)

                    with self.report.add_entry(source_port=port, target_port=adjacent_port,
                                               domain=domain) as entry:

                        cs_session.UpdatePhysicalConnection(resourceAFullPath=entry.source_port,
                                                            resourceBFullPath=entry.target_port)

            except ReportableException as e:
                self.output.send("Failed to connect port {} and {}. {}".format(entry.source_port,
                                                                               entry.target_port,
                                                                               str(e)), error=True)
                self.logger.exception("Failed to connect ports due to:")

            except Exception:
                self.output.send("Failed to connect port {} and {}. See log for details".format(
                    entry.source_port,
                    entry.target_port), error=True)
                self.logger.exception("Failed to connect ports due to:")

            else:
                msg = "Connection between port {} and port {} was successfully processed".format(
                    entry.source_port,
                    entry.target_port)

                self.output.send(msg)
                self.logger.info(msg)

        self.report.generate()
