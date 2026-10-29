from netmiko import ConnectHandler

v_device_type = "cisco_ios"
v_host = "192.168.56.20"
v_ssh_port = 22
v_username = "yari"
v_password = "cisco123"

device = {
    "device_type": v_device_type,
    "host":v_host,
    "username": v_username,
    "password": v_password,
    "secret": v_password,
}

connection = ConnectHandler(**device)
connection.enable()

# Open het bestand 'router_info.txt' in schrijfmodus ("w")
with open("router_info.txt", "w", encoding="utf-8") as file:

    # Functie om zowel op het scherm te printen als naar het bestand te schrijven
    def log(tekst=""):
        print(tekst)
        file.write(tekst + "\n")

    log("Device Information")
    log("------------------")

    output = connection.send_command('sh run | i host')
    parts = output.split()
    if len(parts) >= 2:
        hostname = parts[1]
    else:
        hostname = output.strip()

    log(f"Hostname: {hostname}")

    output = connection.send_command("show inventory")
    model_name = "onbekend"
    for line in output.splitlines():
        if 'PID' in line:
            model_name = line.split("PID:")[1].split(",")[0].strip()
            break

    log(f"Model: {model_name}")

    output = connection.send_command("show inventory")
    serial_number = "onbekend"
    for line in output.splitlines():
        if 'SN:' in line:
            serial_number = line.split("SN:")[1].strip()
            break

    log(f"Serial Number: {serial_number}")
    log("\nSoftware Information")
    log("--------------------")

    output = connection.send_command("show version")
    ios_version = "onbekend"
    for line in output.splitlines():
        if "Software," in line:
            ios_version = line.split("Software,")[1].strip()
            break

    log(f"IOS Version: {ios_version}")

    output = connection.send_command("show version")
    uptime = "onbekend"
    for line in output.splitlines():
        if "uptime is" in line:
            uptime = line.split("uptime is")[1].strip()

    log(f"System uptime: {uptime}")
    log("\nInterface")
    log("---------")

    output = connection.send_command("show ip int brief")
    aantal_interfaces = 0
    for line in output.splitlines():
        if not line.strip() or line.startswith("Interface") or line.startswith("-"):
            continue

        aantal_interfaces += 1

        parts = line.split()
        if len(parts) >= 6:
            intf_name = parts[0]
            status = parts[5]
            log(f"{intf_name} {status}")

    log(f"Total interfaces: {aantal_interfaces}")

    log("\nConnected Devices (CDP Neighbors)")
    log("---------------------------------")

    log("\nRouting Table")
    log("-------------")

    output = connection.send_command("show ip route")

    for line in output.splitlines():
        if line.startswith("C") or line.startswith("S"):
            parts = line.split()
            if len(parts) >= 2:
                network = parts[1]
                interface = parts[-1].strip(",")
                log(f"{network} via {interface}")

connection.disconnect()
print("\n--> Output succesvol opgeslagen in 'router_info.txt'!")