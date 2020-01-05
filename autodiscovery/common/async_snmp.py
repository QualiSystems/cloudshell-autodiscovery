import asyncio

import aiosnmp

from autodiscovery.exceptions import ReportableException


class AsyncSNMPService:
    SYS_OBJECT_ID_OID = ".1.3.6.1.2.1.1.2.0"
    SYS_DESCR_OID = ".1.3.6.1.2.1.1.1.0"
    SYS_NAME_OID = ".1.3.6.1.2.1.1.5.0"

    def __init__(self, ip_address, logger, snmp_community="public", port=161):
        self.ip_address = ip_address
        self.logger = logger
        self.snmp_community = snmp_community
        self.snmp = aiosnmp.Snmp(host=ip_address,
                                 port=port,
                                 community=snmp_community)

    async def is_valid(self):
        is_valid = True
        try:
            await self.snmp.get(self.SYS_DESCR_OID)
        except aiosnmp.exceptions.SnmpTimeoutError:
            is_valid = False

        self.logger.info(
            f"Community string '{self.snmp_community}' "
            f"for device with IP {self.ip_address} is {'valid' if is_valid else 'invalid'}"
        )
        return is_valid

    # todo: get all atributes with one base funciton
    async def get_sys_object_id(self):
        for res in await self.snmp.get(self.SYS_OBJECT_ID_OID):
            return res.value

        raise Exception("Unable to retrieve SNMPv2 sysObjectID value")

    async def get_sys_descr(self):
        for res in await self.snmp.get(self.SYS_DESCR_OID):
            return res.value.decode()

        raise Exception("Unable to retrieve SNMPv2 sysDescr value")

    async def get_sys_name(self):
        for res in await self.snmp.get(self.SYS_NAME_OID):
            return res.value.decode()

        raise Exception("Unable to retrieve SNMPv2 sysName value")

    @classmethod
    async def _get_snmp_if_valid(cls, ip_address, snmp_community, logger):
        global count
        logger.info(
            f"Trying community string '{snmp_community}' "
            f"for device with IP {ip_address}"
        )
        snmp_service = cls(ip_address=ip_address, snmp_community=snmp_community, logger=logger)

        if await snmp_service.is_valid():
            return snmp_service

    @classmethod
    async def get_snmp_service(cls, ip_address, snmp_community_strings, logger):
        done, pending = await asyncio.wait(
            [cls._get_snmp_if_valid(ip_address=ip_address, snmp_community=snmp_community, logger=logger)
             for snmp_community in snmp_community_strings],
            return_when=asyncio.FIRST_COMPLETED)

        for task in done:
            result = task.result()
            if result:
                for pending_task in pending:
                    pending_task.cancel()

                return result

        # wait for all timeouts, not just only for the first (which ends with Exception)
        if pending:
            done, _ = await asyncio.wait(pending)
            for task in done:
                result = task.result()
                if result:
                    return result

        raise ReportableException("SNMP timeout - no resource detected")
