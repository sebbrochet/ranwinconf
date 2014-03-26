#!/usr/bin/env python

class SortedDict(object):
    def __init__(self, d):
        self.d = d

def GetOsType(c):
    result = {}

    for os in c.Win32_OperatingSystem():
        result['Name'] = os.caption
        result['Version'] = os.version
        result['ServicePack'] = "%s - %s" % (os.ServicePackMajorVersion , os.ServicePackMinorVersion)
        InstallDate = "%s" % os.InstallDate
        result['InstallDate'] = "%s-%s:%s" % (InstallDate[:8], InstallDate[8:10], InstallDate[10:12])

    return [
        { "Name"        : result["Name"] },
        { "Version"     : result["Version"] },
        { "ServicePack" : result["ServicePack"] },
        { "InstallDate" : result["InstallDate"] },
    ]

def GetSerial(c):
    colSMBIOS = c.Win32_SystemEnclosure()
    return c.PartNumber, SerialNumber, SMBIOSAssetTag

def GetInterfaces(c):
    result = {}

    import wmi

    try:
        for interface in c.Win32_NetworkAdapterConfiguration (IPEnabled = 1):
            interface_dict = {}

            interface_dict["MAC"] = interface.MACAddress

            if interface.IPAddress:
                ip_list = []
                for ip_address in interface.IPAddress:
                    ip_list.append(ip_address)
                interface_dict["IP"] = ip_list

            if interface.IPSubnet:
                ip_subnet_list = []
                for ip_subnet in interface.IPSubnet:
                    ip_subnet_list.append(ip_subnet)
                interface_dict["MASK"] = ip_subnet_list

            if interface.DefaultIPGateway:
                default_IP_gateway_list = []
                for default_IP_gateway in interface.DefaultIPGateway:
                    default_IP_gateway_list.append(default_IP_gateway)
                interface_dict["Gateway"] = default_IP_gateway_list

            if interface.DNSServerSearchOrder:
                DNS_server_search_order_list = []

                for DNS_server_search_order in interface.DNSServerSearchOrder:
                    DNS_server_search_order_list.append(DNS_server_search_order)

                DNS_server_search_order_list.sort()

                interface_dict["DNS"] = DNS_server_search_order_list

            result[interface.Description] = interface_dict
    except AttributeError, e:
        result['Error'] = "%s" % e
    except wmi.x_wmi, e:
        result['Error'] = "%s" % e

    return result

def GetLogicalDiskList(c):
    result = []

    for disk in c.Win32_LogicalDisk():
        result.append("%s - %s - %s - %s" % (disk.caption, disk.VolumeName, disk.FileSystem, disk.Size))

    result.sort()

    return result

def GetSharedDrives(c):
    result = []

    for share in c.Win32_Share ():
        result.append("%s: %s " % (share.Name, share.Path))

    result.sort()

    return result

def GetDiskPartitions(c):
    result = []

    import wmi

    try:
        for physical_disk in c.Win32_DiskDrive ():
            for partition in physical_disk.associators ("Win32_DiskDriveToDiskPartition"):
                for logical_disk in partition.associators ("Win32_LogicalDiskToPartition"):
                    result.append("%s: %s - %s" % (physical_disk.Caption, partition.Caption, logical_disk.Caption))

        result.sort()

    except AttributeError, e:
        result.append("Error: %s" % e)
    except wmi.x_wmi, e:
        result.append("Error: %s" % e)

    return result

def GetCPU(c):
    import wmi

    result = {}

    try:
        processors = c.Win32_Processor()

        for processor in processors:
            result[processor.DeviceID] = [
                processor.Name, processor.caption
            ]
    except AttributeError, e:
        result['Error'] = "%s" % e
    except wmi.x_wmi, e:
        result['Error'] = "%s" % e

    return result

def GetSystemName(c):
    result = []

    systems = c.Win32_ComputerSystem()

    for system in systems:
        result.append(system.Name)

    return result

def GetRAM(c):
    result = []

    systems = c.Win32_ComputerSystem()

    for system in systems:
        result.append(system.TotalPhysicalMemory)

    return result

def GetInstalledProgs(c):
    import wmi

    result = {}

    try:
        progs = c.Win32_Product()
        for prog in progs:
            data_str = "%s : %s" % (prog.Version, prog.installDate)
            result[prog.Caption] = data_str
    except AttributeError, e:
        result['Error'] = "%s" % e
    except wmi.x_wmi, e:
        result['Error'] = "%s" % e

    return result

def GetServerRoles(c):
    result = []

    try:
        server_roles = c.Win32_ServerFeature()
        for server_role in server_roles:
            result.append("%s - %s" % (server_role.ID, server_role.Name))
    except Exception, e:
        result.append("-Not supported-")

    return result

def GetQuickFix(c):
    result = []

    try:
        fixes = c.Win32_QuickFixEngineering()

        for fix in fixes:
            result.append("%s - %s" % (fix.HotFixID, fix.InstalledOn))

        result.sort()
    except Exception, e:
        result.append("-Not supported-")

    return result

def GetHostConfig(host, user, password):
    result = {}

    import wmi

    loop = True
    nb_try = 1

    while loop:
        try:
            if user and password:
                c = wmi.WMI(host, user = user, password = password)
            else:
                c = wmi.WMI(host)

            loop = False

            if nb_try > 1:
                print "Found host %s at try %d" % (host, nb_try)
        except Exception, e:
            if nb_try >= 3:
                return None
            nb_try += 1

    result["Name"] = GetSystemName(c)
    result["OS"] = GetOsType(c)
    result["CPU"] = GetCPU(c)
    result["Disks"] = GetLogicalDiskList(c)
    result["Interfaces"] = GetInterfaces(c)
    result["Shared Drives"] = GetSharedDrives(c)
    result["Disk Partitions"] = GetDiskPartitions(c)
    result["RAM"] = GetRAM(c)
    result["Applications"] = GetInstalledProgs(c)
    result["Quick Fix"] = GetQuickFix(c)
    result["Server roles"] = GetServerRoles(c)

    return result

def pretty_print_dict(d, output_list, left, sort = False):
    if sort:
        for key in iter(sorted(d.keys())):
            output_list.append("%s%s" % (left * ' ', key))
            pretty_print(d[key], output_list, left+3)
    else:
        for key in d.keys():
            output_list.append("%s%s" % (left * ' ', key))
            pretty_print(d[key], output_list, left+3)

def pretty_print_list(l, output_list, left):
    for item in l:
        if item.__class__ is list:
            pretty_print(item, output_list, left+3)
        else:
            pretty_print(item, output_list, left)

def pretty_print(v, output_list, left=0):
    if v.__class__ is SortedDict:
        pretty_print_dict(v.d, output_list, left, sort = True)
    elif v.__class__ is dict:
        pretty_print_dict(v, output_list, left)
    elif v.__class__ is list:
        pretty_print_list(v, output_list, left)
    else:
        output_list.append("%s%s" % (left * ' ', v))

def myprint(unicodeobj):
    print unicodeobj.encode('utf-8')

def generate_host_config(host, target, user="", password="", RecordOnlyGoodConfig=False):
    host_config = GetHostConfig(host, user, password)

    output_list = []

    if host_config:
        display_list = [
            { "Name" : host_config["Name"] },
            { "OS" : host_config["OS"] },
            { "Server roles" : host_config["Server roles"] },
            { "CPU" : host_config["CPU"] },
            { "RAM" : host_config["RAM"] },
            { "Interfaces" : host_config["Interfaces"] },
            { "Disk Partitions" : host_config["Disk Partitions"] },
            { "Disks" : host_config["Disks"] },
            { "Shared Drives" : host_config["Shared Drives"] },
            { "Applications" : SortedDict(host_config["Applications"]) },
            { "Quick Fix" : host_config["Quick Fix"] },
        ]

        pretty_print(display_list, output_list)
    else:
        output_list.append("Error: check if:")
        output_list.append("host %s answers ping" % host)
        output_list.append("COM+ service is started on host: %s" % host)
        output_list.append("Used account has enough (admin) rights")

    if target != "<stdout>":
        if host_config or not RecordOnlyGoodConfig:
            f = file(target, "w")
            f.write('\n'.join(output_list).encode('utf-8'))
            f.close()
    else:
        myprint('\n'.join(output_list))
