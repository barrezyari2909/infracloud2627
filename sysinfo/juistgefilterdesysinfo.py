import datetime
import json
import os
import platform
import socket
import subprocess
import psutil

now = datetime.datetime.now()
print(now)


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

    # Memory info
    data["memory"] = psutil.virtual_memory()._asdict()
    data["swap"] = psutil.swap_memory()._asdict()

    # Storage info (alle partities)
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

    # Network info
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

    # 2. Computermodel (Via PowerShell omdat wmic niet werkt)
    try:
        if platform.system() == "Windows":
            cmd = 'powershell -Command "(Get-CimInstance Win32_ComputerSystem).Model"'
            model = subprocess.check_output(cmd, shell=True).decode().strip()
        else:
            model = "Onbekend"
    except:
        model = "Onbekend"
    print("Computermodel:", model)

    # NIEUW: Serienummer opvragen (Via PowerShell)
    serienummer = "Onbekend"
    try:
        if platform.system() == "Windows":
            cmd = 'powershell -Command "(Get-CimInstance Win32_Bios).SerialNumber"'
            serienummer = (
                subprocess.check_output(cmd, shell=True).decode().strip()
            )
        elif platform.system() == "Linux":
            serienummer = (
                subprocess.check_output(
                    "cat /sys/class/dmi/id/product_serial", shell=True
                )
                .decode()
                .strip()
            )
        elif platform.system() == "Darwin":  # macOS
            cmd = "system_profiler SPHardwareDataType | grep Serial"
            serienummer = (
                subprocess.check_output(cmd, shell=True)
                .decode()
                .split(":")[-1]
                .strip()
            )
    except:
        serienummer = "Niet beschikbaar"
    print("Serienummer:", serienummer)

    # 3. Processor
    print("Processor:", info["cpu"]["processor"])

    # 4. Aantal fysieke CPU-cores
    print("Fysieke cores:", info["cpu"]["physical_cores"])

    # 5. Maximale CPU-frequentie
    freq = info["cpu"]["cpu_freq"]
    print(
        "Maximale CPU-frequentie:", f"{freq['max']} MHz" if freq else "Onbekend"
    )

    # 6. Totale hoeveelheid RAM-geheugen
    ram_gb = round(info["memory"]["total"] / (1024**3), 2)
    print("Totale RAM:", ram_gb, "GB")

    # 7 & 8. Schijfinfo (We pakken de eerste schijf uit de lijst)
    eerste_schijf = (
        list(info["storage"].keys())[0] if info["storage"] else None
    )
    if eerste_schijf:
        schijf = info["storage"][eerste_schijf]
        print("Bestandssysteem opslag:", schijf["fstype"])
        print("Opslagcapaciteit:", round(schijf["total"] / (1024**3), 2), "GB")
    else:
        print("Bestandssysteem opslag: Geen schijf gevonden")
        print("Opslagcapaciteit: Geen schijf gevonden")

    # Netwerkkaarten doorlopen om de primaire (actieve) interface te vinden
    mac, ipv4, ipv6, link_local = (
        "Niet gevonden",
        "Niet gevonden",
        "Niet gevonden",
        "Niet gevonden",
    )

    for kaart, details in info["network"]["interfaces"].items():
        if details["stats"] and details["stats"]["isup"]:
            for adres in details["addrs"]:
                ip = adres["address"]
                # MAC-adres
                if (
                    adres["family"] in [-1, 17, 18]
                    or ":" in ip
                    and len(ip) < 20
                ):
                    mac = ip
                # IPv4-adres
                elif adres["family"] == 2:
                    ipv4 = ip
                # IPv6-adres
                elif adres["family"] in [23, 10] or ":" in ip:
                    if ip.lower().startswith("fe80"):
                        link_local = ip.split("%")[0]
                    else:
                        ipv6 = ip
            if ipv4 != "Niet gevonden":
                break

    # 9 t/m 12. Netwerk printen
    print("MAC-adres:", mac)
    print("IPv4-adres:", ipv4)
    print("IPv6-adres:", ipv6)
    print("IPv6 link-local-adres:", link_local)
