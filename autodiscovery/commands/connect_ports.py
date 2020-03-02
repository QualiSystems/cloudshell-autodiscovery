import asyncio

from cloudshell.api.cloudshell_api import AttributeNameValue
from colorama import Fore
from tqdm import tqdm

from autodiscovery.exceptions import ReportableException
from autodiscovery.output import EmptyOutput

ADJACENT_PORT_ATTRIBUTE = "Adjacent"
SYSTEM_NAME_PORT_ATTRIBUTE = "System Name"
PORT_FAMILY = "CS_Port"


class ConnectPortsCommand(object):
    def __init__(
        self, cs_session_manager, report, offline, logger, workers_num, output=None
    ):
        if output is None:
            output = EmptyOutput()

        self.cs_session_manager = cs_session_manager
        self.report = report
        self.offline = offline
        self.output = output
        self.logger = logger
        self.workers_num = workers_num

    def _get_resource_attribute_value(self, resource, attribute_name):
        """Get resource attribute value.

        :param resource cloudshell.api.cloudshell_api.ResourceInfo:
        :param str attribute_name:
        """
        for attribute in resource.ResourceAttributes:
            if attribute.Name.endswith(attribute_name):
                return attribute.Value

    def _find_ports(self, resource):
        """Find ports on the resource.

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
        """Find Adjacent ports.

        :param resource:
        :return:
        """
        adjacent_ports = []
        for port in self._find_ports(resource):
            adjacent = self._get_resource_attribute_value(
                resource=port, attribute_name=ADJACENT_PORT_ATTRIBUTE
            )
            if adjacent:
                adjacent_ports.append((port.Name, adjacent))

        return adjacent_ports

    def _find_resource_by_sys_name(self, cs_session, sys_name):
        """Find resource by its system name.

        :param cloudshell.api.cloudshell_api.CloudShellAPISession cs_session:
        :param sys_name:
        :return:
        """
        resources = []
        families = {
            res.ResourceFamilyName for res in cs_session.GetResourceList().Resources
        }

        for family, sys_attr in [("", SYSTEM_NAME_PORT_ATTRIBUTE)] + [
            (family, f"{family}.{SYSTEM_NAME_PORT_ATTRIBUTE}") for family in families
        ]:

            for res in cs_session.FindResources(
                resourceFamily=family,
                includeSubResources=False,
                attributeValues=[AttributeNameValue(Name=sys_attr, Value=sys_name)],
            ).Resources:
                # response may contain an empty result
                if res.ResourceFamilyName:
                    resources.append(res)

        if not resources:
            raise ReportableException(
                f"Unable to find resource with 'System Name' attribute: '{sys_name}'"
            )
        elif len(resources) > 1:
            raise ReportableException(
                f"Found several resources: {[resource.Name for resource in resources]} "
                f"with the same 'System Name' attribute: '{sys_name}'"
            )

        return cs_session.GetResourceDetails(resources[0].FullName)

    def _find_port_by_adjacent_name(self, adjacent_resource, adjacent_port_name):
        """Find port by Adjacent name.

        :param cloudshell.api.cloudshell_api.ResourceInfo adjacent_resource:
        :param str adjacent_port_name:
        :return:
        """
        adjacent_port_name = adjacent_port_name.replace(".", "-").replace("/", "-")

        for port in self._find_ports(adjacent_resource):
            port_name = port.Name.split("/")[-1]
            if port_name == adjacent_port_name:
                return port

        raise ReportableException(
            f"Unable to find Adjacent port '{adjacent_port_name}'"
        )

    async def discover_resource_connections(
        self, resource_name, domain, progress_bar, semaphore
    ):
        await semaphore.acquire()

        msg = f"Updating physical connections for the resource '{resource_name}': "
        self.output.send(msg)
        self.logger.info(msg)

        try:
            cs_session = await self.cs_session_manager.get_session(cs_domain=domain)
            resource = await cs_session.GetResourceDetails(resource_name)

            for port, adjacent in self._find_adjacent_ports(resource):
                self.output.send(f"Updating physical connection for the port '{port}' ")
                self.logger.info(f"Processing port '{port}' with adjacent '{adjacent}'")

                try:
                    with self.report.add_entry(
                        resource_name=resource_name,
                        source_port=port,
                        adjacent=adjacent,
                        target_port="",
                        domain=domain,
                        offline=self.offline,
                    ) as entry:
                        adjacent_sys_name, adjacent_port_name = [
                            x.strip() for x in adjacent.split("through")
                        ]
                        adjacent_resource = self._find_resource_by_sys_name(
                            cs_session=cs_session, sys_name=adjacent_sys_name
                        )

                        adjacent_port = self._find_port_by_adjacent_name(
                            adjacent_resource=adjacent_resource,
                            adjacent_port_name=adjacent_port_name,
                        )

                        entry.target_port = adjacent_port.Name

                        if not self.offline:
                            await cs_session.UpdatePhysicalConnection(
                                resourceAFullPath=entry.source_port,
                                resourceBFullPath=entry.target_port,
                            )

                except ReportableException as e:
                    self.output.send(
                        f"Failed to update physical connection "
                        f"for the port '{port}'. {e}",
                        error=True,
                    )
                    self.logger.exception(
                        "Failed to update physical connection due to:"
                    )

                except Exception:
                    self.output.send(
                        "Failed to update physical connection "
                        f"for the port '{port}' ",
                        error=True,
                    )
                    self.logger.exception(
                        "Failed to update physical connection due to:"
                    )

        except Exception:
            self.output.send(
                f"Failed to update physical connections for the resource "
                f"'{resource_name}'. See log for the details",
                error=True,
            )
            self.logger.exception("Failed to update physical connections due to:")

        else:
            msg = (
                f"Physical connections for the resource '{resource_name}' "
                "were updated"
            )
            self.output.send(msg)
            self.logger.info(msg)

        progress_bar.update()
        semaphore.release()

    async def execute(self, resources_names, domain):
        """Execute command.

        :param list[str] resources_names:
        :param str domain:
        :return:
        """
        semaphore = asyncio.Semaphore(value=self.workers_num)

        with tqdm(
            desc=f"{Fore.RESET}Total progress", total=len(resources_names), position=1
        ) as progress_bar:
            await asyncio.gather(
                *[
                    asyncio.create_task(
                        (
                            self.discover_resource_connections(
                                resource_name=resource_name,
                                domain=domain,
                                progress_bar=progress_bar,
                                semaphore=semaphore,
                            )
                        )
                    )
                    for resource_name in resources_names
                ],
                return_exceptions=True
            )

        self.report.generate()
        failed_entries_count = self.report.get_failed_entries_count()

        print (
            f"\n\n\n{Fore.GREEN}Connections discovery process finished: "
            f"\n\tSuccessfully discovered {len(self.report.entries) - failed_entries_count} connections."
            f"\n\t{Fore.RED}Failed to discovery {failed_entries_count} connections.{Fore.RESET}\n"
        )
