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
    import os
    import csv

    info = collect_sys_info()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_pad = os.path.join(script_dir, "systeeminfo.csv")

    # Kolomkoppen definiëren
    headers = [
        "hostname",
        "processor",
        "physical_cores",
        "max_cpu_freq",
        "ram_gb",
        "network_mac",
        "network_ipv4",
        "network_ipv6",
        "mountpoint",
        "fstype",
        "storage_total_gb",
    ]

    # Schrijf naar CSV
    with open(csv_pad, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(headers)

        # Omdat 'storage' meerdere schijven bevat, maken we per schijf een rij aan
        # We gebruiken .get() om te voorkomen dat de code crasht als een key leeg is
        storage_dict = info.get("storage", {})

        if storage_dict:
            for mountpoint, storage_details in storage_dict.items():
                rij = [
                    info["computer"]["hostname"],
                    info["cpu"]["processor"],
                    info["cpu"]["physical cores"],
                    info["cpu"]["max cpu frequentie"],
                    info["ram"]["ram"],
                    info["network"].get("mac address", "N/A"),
                    info["network"].get("ipv4 address", "N/A"),
                    info["network"].get("ipv6 address", "N/A"),
                    mountpoint,
                    storage_details["fstype"],
                    storage_details["total"],
                ]
                writer.writerow(rij)
        else:
            # Mocht er onverhoopt geen storage gevonden zijn, schrijf dan één basisrij
            rij = [
                info["computer"]["hostname"],
                info["cpu"]["processor"],
                info["cpu"]["physical cores"],
                info["cpu"]["max cpu frequentie"],
                info["ram"]["ram"],
                info["network"].get("mac address", "N/A"),
                info["network"].get("ipv4 address", "N/A"),
                info["network"].get("ipv6 address", "N/A"),
                "N/A",
                "N/A",
                "N/A",
            ]
            writer.writerow(rij)

    print(f"\nSucces! Het CSV-bestand is aangemaakt op: {csv_pad}")
    