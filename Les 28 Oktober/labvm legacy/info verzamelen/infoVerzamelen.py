from netmiko import ConnectHandler
from netmiko import NetMikoTimeoutException, NetMikoAuthenticationException

v_device_type = "linux"
v_host = "192.168.56.103"
v_ssh_port = 22
v_username = "yari"
v_password = "yari"

device = {
    "device_type": v_device_type,
    "host": v_host,
    "port": v_ssh_port,
    "username": v_username,
    "password": v_password,
    "secret": v_password,
}

# Lijst om alle regels voor het tekstbestand te verzamelen
report_lines = []

def log_and_store(text):
    """Print de tekst in de console én voegt deze toe aan de lijst voor het bestand."""
    print(text)
    report_lines.append(text)

try:
    print(f"connecting to {v_host}:{v_ssh_port}...")
    with ConnectHandler(**device) as connection:
        print("Connected succesfully!\n")

        log_and_store("device information")
        log_and_store("------------------")

        hostname = connection.send_command("hostname").strip()
        log_and_store(f"hostname: {hostname}")

        output_hostnamectl = connection.send_command("hostnamectl")
        model_name = "unknown"
        for line in output_hostnamectl.splitlines():
            if 'Icon name' in line:
                model_name = line.split("Icon name: ")[1].split(",")[0].strip()
                break
        log_and_store(f"chassis: {model_name}")

        output_serial = connection.send_command(
            "sudo -S dmidecode -s system-serial-number",
            expect_string=r"[Pp]assword",
        )
        output_serial += connection.send_command(
            v_password,
            expect_string=r"[$#]",
        )
        serial_number = "unknown"
        for line in output_serial.splitlines():
            cleaned = line.strip()
            if (
                cleaned
                and "[sudo] password" not in cleaned
                and "dmidecode" not in cleaned
                and not cleaned.endswith(("$", "#"))
            ):
                serial_number = cleaned
                break
        log_and_store(f"serial-number: {serial_number}")

        log_and_store("\nSoftware Information")
        log_and_store("--------------------")

        ios_version = "unknown"
        for line in output_hostnamectl.splitlines():
            if "Operating System" in line:
                ios_version = line.split("Operating System:")[1].strip()
                break
        log_and_store(f"ios-version: {ios_version}")

        uptime = connection.send_command("uptime").strip()
        log_and_store(f"uptime: {uptime}")

        log_and_store("\ninterface")
        log_and_store("---------")

        output_int = connection.send_command("ip -br addr")
        aantal_interfaces = 0
        for line in output_int.splitlines():
            cleaned = line.strip()
            if not cleaned:
                continue
            parts = cleaned.split()
            if len(parts) >= 2:
                aantal_interfaces += 1
                intf_name = parts[0]
                status = parts[1]
                log_and_store(f"{intf_name} {status}")
        log_and_store(f"Totaal aantal interfaces: {aantal_interfaces}")

        log_and_store("\nroutes")
        log_and_store("------")
        output_route = connection.send_command("ip route")

        for line in output_route.splitlines():
            cleaned = line.strip()
            if not cleaned:
                continue

            parts = cleaned.split()
            network = parts[0]

            interface = "unknown"
            if "dev" in parts:
                dev_index = parts.index("dev")
                if dev_index + 1 < len(parts):
                    interface = parts[dev_index + 1]

            log_and_store(f"{network} via {interface}")

        # Schrijf alle verzamelde regels weg naar een .txt bestand
        bestandsnaam = f"{hostname}_info.txt"
        with open(bestandsnaam, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines) + "\n")

        print(f"\nAlle gegevens zijn opgeslagen in '{bestandsnaam}'.")

except NetMikoTimeoutException:
    print("Connection timed out")
except NetMikoAuthenticationException:
    print("Authentication failed check password and user")
except Exception as e:
    print(f"An error occured: {e}")