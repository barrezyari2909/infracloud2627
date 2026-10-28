import datetime
import json
import platform
import psutil
import socket
import subprocess

now = datetime.datetime.now()
print("Uitvoertijd:", now.strftime("%Y-%m-%d %H:%M:%S"))


def get_computer_model():
    """Haalt het computermodel op via PowerShell (vervangt verouderde WMIC)."""
    os_type = platform.system()

    try:
        if os_type == "Windows":
            # PowerShell Get-CimInstance vervangt wmic
            cmd = 'powershell -Command "(Get-CimInstance -ClassName Win32_ComputerSystem).Model"'
            return subprocess.check_output(cmd, shell=True).decode().strip()
        elif os_type == "Linux":
            with open("/sys/class/dmi/id/product_name", "r") as f:
                return f.read().strip()
        elif os_type == "Darwin":  # macOS
            cmd = "sysctl -n hw.model"
            return subprocess.check_output(cmd, shell=True).decode().strip()
    except Exception:
        pass

    return "Onbekend"


def collect_system_info():
    data = {}

    # CPU info
    data["cpu"] = {
        "platform": platform.platform(),
        "processor": platform.processor(),
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_processors": psutil.cpu_count(logical=True),
        "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
        "cpu_percent_total": psutil.cpu_percent(interval=0.1),
        "cpu_percent_per_cpu": psutil.cpu_percent(interval=0.1, percpu=True),
    }

    # Geheugen info
    data["memory"] = psutil.virtual_memory()._asdict()
    data["swap"] = psutil.swap_memory()._asdict()

    # Opslag info (alle partities)
    storage = {}
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            storage[part.mountpoint] = {
                "device": part.device,
                "fstype": part.fstype,
                "opts": part.opts,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent,
            }
        except PermissionError:
            continue
    data["storage"] = storage

    # Netwerk info
    net = {}
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    io = psutil.net_io_counters(pernic=True)
    for iface, addr_list in addrs.items():
        net[iface] = {
            "addrs": [a._asdict() for a in addr_list],
            "stats": stats[iface]._asdict() if iface in stats else None,
            "io": io[iface]._asdict() if iface in io else None,
        }

    data["network"] = {
        "hostname": socket.gethostname(),
        "fqdn": socket.getfqdn(),
        "interfaces": net,
    }

    return data


if __name__ == "__main__":
    info = collect_system_info()

    # 1. Computernaam
    print("Computernaam:", info["network"]["hostname"])

    # 2. Computermodel
    print("Computermodel:", get_computer_model())

    # 3. Processor
    print("Processor:", info["cpu"]["processor"])

    # 4. Aantal fysieke CPU-cores
    print("Fysieke cores:", info["cpu"]["physical_cores"])

    # 5. Maximale CPU-frequentie
    freq = info["cpu"]["cpu_freq"]
    print("Maximale CPU-frequentie:", f"{freq['max']} MHz" if freq and freq["max"] else "Onbekend")

    # 6. Totale hoeveelheid RAM-geheugen
    ram_gb = round(info["memory"]["total"] / (1024**3), 2)
    print("Totale RAM:", ram_gb, "GB")

    # 7 & 8. Schijfinfo
    if info["storage"]:
        eerste_schijf = list(info["storage"].keys())[0]
        schijf = info["storage"][eerste_schijf]
        print("Bestandssysteem opslag:", schijf["fstype"])
        print("Opslagcapaciteit:", round(schijf["total"] / (1024**3), 2), "GB")

    # 9 t/m 12. Netwerkkaarten doorlopen om actieve IP's en MAC te vinden
    mac, ipv4, ipv6, link_local = "Niet gevonden", "Niet gevonden", "Niet gevonden", "Niet gevonden"
    af_link = getattr(psutil, "AF_LINK", None)

    for kaart, details in info["network"]["interfaces"].items():
        if details["stats"] and details["stats"]["isup"]:
            temp_mac, temp_ipv4, temp_ipv6, temp_ll = None, None, None, None

            for adres in details["addrs"]:
                family = adres["family"]
                ip = adres["address"]

                # MAC-adres
                if family == af_link:
                    temp_mac = ip
                # IPv4-adres (geen loopback)
                elif family == socket.AF_INET and not ip.startswith("127."):
                    temp_ipv4 = ip
                # IPv6-adres
                elif family == socket.AF_INET6:
                    clean_ip = ip.split("%")[0]
                    if clean_ip.lower().startswith("fe80"):
                        temp_ll = clean_ip
                    elif not clean_ip.startswith("::1"):
                        temp_ipv6 = clean_ip

            # Zodra we de actieve IPv4-kaart vinden, slaan we op en stoppen we
            if temp_ipv4:
                mac = temp_mac or mac
                ipv4 = temp_ipv4
                ipv6 = temp_ipv6 or ipv6
                link_local = temp_ll or link_local
                break

    print("MAC-adres:", mac)
    print("IPv4-adres:", ipv4)
    print("IPv6-adres:", ipv6)
    print("IPv6 link-local-adres:", link_local)