import datetime
import json
import os
import platform
import socket
import subprocess
import psutil

now = datetime.datetime.now()
print(f"Start systeemscan op: {now}")


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
    hostname = info["network"]["hostname"]

    # 2. Computermodel (Via PowerShell omdat wmic niet werkt)
    try:
        if platform.system() == "Windows":
            cmd = 'powershell -Command "(Get-CimInstance Win32_ComputerSystem).Model"'
            model = subprocess.check_output(cmd, shell=True).decode().strip()
        else:
            model = "Onbekend"
    except:
        model = "Onbekend"

    # 3. Serienummer opvragen (Via PowerShell)
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

    # 4. Processor
    processor = info["cpu"]["processor"]

    # 5. Aantal fysieke CPU-cores
    fysieke_cores = info["cpu"]["physical_cores"]

    # 6. Maximale CPU-frequentie
    freq = info["cpu"]["cpu_freq"]
    max_freq = f"{freq['max']} MHz" if freq else "Onbekend"

    # 7. Totale hoeveelheid RAM-geheugen
    ram_gb = round(info["memory"]["total"] / (1024**3), 2)

    # 8 & 9. Schijfinfo (Eerste schijf uit de lijst)
    eerste_schijf = (
        list(info["storage"].keys()) if info["storage"] else None
    )
    if eerste_schijf:
        schijf = info["storage"][eerste_schijf]
        fstype = schijf["fstype"]
        storage_gb = round(schijf["total"] / (1024**3), 2)
    else:
        fstype = "Onbekend"
        storage_gb = 0

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
                elif adres["family"] or ":" in ip:
                    if ip.lower().startswith("fe80"):
                        link_local = ip.split("%")
                    else:
                        ipv6 = ip
            if ipv4 != "Niet gevonden":
                break

    # === MAAK DE SCHONE DICTIONARY ===
    gefilterde_data = {
        "computernaam": hostname,
        "computermodel": model,
        "serienummer": serienummer,
        "processor": processor,
        "fysieke_cores": fysieke_cores,
        "max_cpu_frequentie": max_freq,
        "totaal_ram_gb": ram_gb,
        "bestandssysteem_opslag": fstype,
        "opslagcapaciteit_gb": storage_gb,
        "mac_adres": mac,
        "ipv4_adres": ipv4,
        "ipv6_adres": ipv6,
        "ipv6_link_local_adres": link_local,
    }

    # === SCHRIJF WEG NAAR HET JSON BESTAND ===
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_pad = os.path.join(script_dir, "gefilterde_systeeminfo.json")

    with open(json_pad, "w", encoding="utf-8") as f:
        json.dump(gefilterde_data, f, indent=4, ensure_ascii=False)

    print(f"\nSucces! Het JSON-bestand is aangemaakt: {json_pad}")
