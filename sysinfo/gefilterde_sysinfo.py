import datetime
import psutil
import platform
import socket
import json

now = datetime.datetime.now();
print(now)

def collect_sys_info():
    data = {}

    data["computer"] = {
        "hostname" : socket.gethostname()
    }

    data["cpu"] = {
        "processor" : platform.processor(),
        "physical cores" : psutil.cpu_count(logical=False),
        "max cpu frequentie" : psutil.cpu_freq().max
    }

    vm = psutil.virtual_memory()
    
    data["ram"] = {
        "ram" : vm.total / (1024**3) 
    }

    storage = {}
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            storage[part.mountpoint] = {
                "fstype" : part.fstype,
                "total" : usage.total / (1024**3)
            }
        except PermissionError:
            continue
        data["storage"] = storage

    network = {}
    for addrs in psutil.net_if_addrs().values():
        for a in addrs:
            # MAC-adres
            if a.family == psutil.AF_LINK and "mac address" not in network:
                network["mac address"] = a.address
            # IPv4 (slaat localhost 127.x over)
            elif (
                a.family == socket.AF_INET
                and "ipv4 address" not in network
                and not a.address.startswith("127.")
            ):
                network["ipv4 address"] = a.address
            # IPv6 (slaat localhost ::1 over)
            elif (
                a.family == socket.AF_INET6
                and "ipv6 address" not in network
                and not a.address.startswith("::1")
            ):
                network["ipv6 address"] = a.address.split("%")[0]

    data["network"] = network

    return data


if __name__ == "__main__":
    info = collect_sys_info()
    print(json.dumps(info, indent=2))
    with open("systeeminfo.json", "w", encoding="utf-8") as f:
        json.dump(info, f, indent=4, ensure_ascii=False)