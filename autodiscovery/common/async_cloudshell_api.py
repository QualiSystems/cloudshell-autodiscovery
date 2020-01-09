import socket
import ssl
import xml.etree.ElementTree as etree
from collections import OrderedDict

import aiohttp
from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.api.common_cloudshell_api import (
    CloudShellAPIError,
    CommonAPIRequest,
    CommonApiResult,
    CommonAPISession,
    XMLWrapper,
)


class AsyncCloudShellAPISession(CloudShellAPISession):
    def __init__(
        self,
        host,
        username="",
        password="",
        domain="",
        timezone="UTC",
        datetimeformat="MM/dd/yyyy HH:mm",
        token_id="",
        port=8029,
        uri="/ResourceManagerApiService/",
        cloudshell_api_scheme="http",
    ):
        CommonAPISession.__init__(self, host, username, password, domain)

        self.port = str(port)
        self.hostname = f"{socket.gethostname()}:{self.port}"
        self.headers = {
            "Content-Type": "text/xml",
            "Accept": "*/*",
            "ClientTimeZoneId": timezone,
            "DateTimeFormat": datetimeformat,
        }

        self.url = f"{cloudshell_api_scheme}://{host}:{port}{uri}"
        self.token_id = token_id

    async def connect(self):
        if self.token_id:
            response_info = await self.SecureLogon(self.token_id, self.domain)
        else:
            response_info = await self.Logon(self.username, self.password, self.domain)

        self.domain = response_info.Domain.DomainId
        self.token_id = response_info.Token.Token

    async def _sendRequest(self, username, domain, operation, message):
        request_headers = self.headers.copy()

        request_headers["Content-Length"] = str(len(message))
        request_headers["Host"] = f"{self.host}:{self.port}"
        request_headers[
            "Authorization"
        ] = f"MachineName={self.hostname};Token={self.token_id}"

        ssl_protocol = ssl.PROTOCOL_TLS
        ctx = ssl.SSLContext(ssl_protocol)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        operation_url = str(self.url + operation)
        # todo: handle ssl ?!
        # ssl_context or ssl ????

        async with aiohttp.ClientSession(headers=request_headers) as session:
            async with session.post(url=operation_url, data=message) as response:
                response.raise_for_status()
                return await response.text()

    async def generateAPIRequest(self, kwargs):
        method_name = kwargs.pop("method_name", None)

        if method_name is None:
            raise CloudShellAPIError(404, 'Key "method_name" not in input data!', "")

        request_node = etree.Element(method_name)

        for name in kwargs:
            child_node = etree.SubElement(request_node, name)
            self._new_serializeRequestData(child_node, kwargs[name])

        response_str = await self._sendRequest(
            self.username,
            self.domain,
            method_name,
            etree.tostring(request_node).decode("utf-8"),
        )

        response_str = response_str.replace(
            'xmlns="http://schemas.qualisystems.com/ResourceManagement/'
            'ApiCommandResult.xsd"',
            "",
        ).replace("&#x0;", "<NUL>")

        response_xml = XMLWrapper.parseXML(response_str)
        api_result = CommonApiResult(response_xml)

        if not api_result.success:
            raise CloudShellAPIError(
                api_result.error_code, api_result.error, response_str
            )

        if api_result.response_info is None:
            return response_str

        return api_result.response_info

    async def Logon(self, username="", password="", domainName="Global"):
        return await self.generateAPIRequest(
            OrderedDict(
                [
                    ("method_name", "Logon"),
                    ("username", username),
                    ("password", password),
                    ("domainName", domainName),
                ]
            )
        )

    async def SecureLogon(self, token="", domainName="Global"):
        return await self.generateAPIRequest(
            OrderedDict(
                [
                    ("method_name", "SecureLogon"),
                    ("token", token),
                    ("domainName", domainName),
                ]
            )
        )

    async def CreateResource(
        self,
        resourceFamily="",
        resourceModel="",
        resourceName="",
        resourceAddress="",
        folderFullPath="",
        parentResourceFullPath="",
        resourceDescription="",
    ):
        return await self.generateAPIRequest(
            OrderedDict(
                [
                    ("method_name", "CreateResource"),
                    ("resourceFamily", resourceFamily),
                    ("resourceModel", resourceModel),
                    ("resourceName", resourceName),
                    ("resourceAddress", resourceAddress),
                    ("folderFullPath", folderFullPath),
                    ("parentResourceFullPath", parentResourceFullPath),
                    ("resourceDescription", resourceDescription),
                ]
            )
        )

    async def CreateFolder(self, folderFullPath=""):
        return await self.generateAPIRequest(
            OrderedDict(
                [("method_name", "CreateFolder"), ("folderFullPath", folderFullPath)]
            )
        )

    async def SetAttributesValues(self, resourcesAttributesUpdateRequests=[]):
        return await self.generateAPIRequest(
            OrderedDict(
                [
                    ("method_name", "SetAttributesValues"),
                    (
                        "resourcesAttributesUpdateRequests",
                        CommonAPIRequest.toContainer(resourcesAttributesUpdateRequests),
                    ),
                ]
            )
        )

    async def AutoLoad(self, resourceFullPath=""):
        return await self.generateAPIRequest(
            OrderedDict(
                [("method_name", "AutoLoad"), ("resourceFullPath", resourceFullPath)]
            )
        )

    async def UpdateResourceDriver(self, resourceFullPath="", driverName=""):
        return await self.generateAPIRequest(
            OrderedDict(
                [
                    ("method_name", "UpdateResourceDriver"),
                    ("resourceFullPath", resourceFullPath),
                    ("driverName", driverName),
                ]
            )
        )
