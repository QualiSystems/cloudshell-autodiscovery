class DeviceInfoModel(object):
    def __init__(self, ip, vendor, sys_object_id, description, snmp_community, family, model, status, resource_name,
                 comment=None, user=None, password=None, enable_password=None):
        self.vendor = vendor
        self.sys_object_id = sys_object_id
        self.description = description
        self.ip = ip
        self.snmp_community = snmp_community
        self.family = family
        self.model = model
        self.user = user
        self.password = password
        self.enable_password = enable_password
        self.status = status
        self.resource_name = resource_name
        self.comment = comment
