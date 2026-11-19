from netmiko import ConnectHandler
from netmiko import NetMikoTimeoutException, NetMikoAuthenticationException

v_device_type = "linux"
v_host = "192.168.56.103"
v_ssh_port = 22
v_username = "yari"
v_password = "yari"

device = {
    "device_type": v_device_type,
    "host":v_host,
    "username": v_username,
    "password": v_password,
    "secret": v_password,
}

try:
    print(f"connecting to {v_host}:{v_ssh_port}...")
    with ConnectHandler(**device) as connection:
        print("Connected succesfully!")

        print("device information")
        print("------------------")

        output = connection.send_command("hostname")
        print(f"hostname: {output}")

        output = connection.send_command("hostnamectl")
        model_name = "unknown"
        for line in output.splitlines():
            if 'Icon name' in line:
                model_name = line.split("Icon name: ")[1].split(",")[0].strip()
                break
        print(f"chassis: {model_name}")

        output = connection.send_command(
            "sudo -S dmidecode -s system-serial-number",
            expect_string=r"[Pp]assword",
            )
        output += connection.send_command(
            v_password,
            expect_string=r"[$#]",
        )
        serial_number = "unknown"
        for line in output.splitlines():
            cleaned = line.strip()
            if(
                cleaned
                and "[sudo] password" not in cleaned
                and "dmidecode" not in cleaned
                and not cleaned.endwith(("$", "#"))
            ):
                serial_number = cleaned
                break
        print(f"serial-number: {serial_number}")

        print("Software Information")
        print("--------------------")

        output = connection.send_command("hostnamectl")
        ios_version = "unknown"
        for line in output.splitlines():
            if "Operating System" in line:
                ios_version = line.split("Operating System:")[1].strip()
        print(f"ios-version: {ios_version}")

        output = connection.send_command("uptime")
        uptime = output
        print(f"uptime: {uptime}")
        print("interface")
        print("---------")

        output = connection.send_command("ip -br addr")
        aantal_interfaces = 0
        for line in output.splitlines():
            cleaned = line.strip()
            if not cleaned:
                continue
            parts = cleaned.split()
            if len(parts) >= 2:
                aantal_interfaces+=1
                intf_name = parts[0]
                status = parts[1]
                print(f"{intf_name} {status}")
        print(f"Totaal aantal interfaces: {aantal_interfaces}")
        print("routes")
        print("------")
        output = connection.send_command("ip route")

        for line in output.splitlines():
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

        print(f"{network} via {interface}")

except NetMikoTimeoutException:
    print("Connection timed out")
except NetMikoAuthenticationException:
    print("Authentication failed check password and user")
except Exception as e:
    print(f"An error occured: {e}")