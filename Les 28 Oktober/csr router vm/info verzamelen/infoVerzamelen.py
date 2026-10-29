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

print("Device Information")
print("------------------")

output = connection.send_command('sh run | i host')
parts = output.split()
if len(parts) >= 2:
    hostname = parts[1]
else:
    hostname = output.strip()

print("Hostname:", hostname)

output = connection.send_command("show inventory")
model_name = "onbekend"
for line in output.splitlines():
    if 'PID' in line:
        model_name = line.split("PID:")[1].split(",")[0].strip()
        break

print("Model:", model_name)

output = connection.send_command("show inventory")
serial_number = "onbekend"
for line in output.splitlines():
    if 'SN:' in line:
        serial_number = line.split("SN:")[1].strip()
        break

print("Serial Number:", serial_number)
print("Software Information")
print("--------------------")

output = connection.send_command("show version")
ios_version = "onbekend"
for line in output.splitlines():
    if "Software," in line:
        ios_version = line.split("Software,")[1].strip()
        break

print("IOS Version:", ios_version)

output = connection.send_command("show version")
uptime = "onbekend"
for line in output.splitlines():
    if "uptime is" in line:
        uptime = line.split("uptime is")[1].strip()

print("System uptime:", uptime)
print("interface")
print("---------")

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
        print(f"{intf_name} {status}")

print("Total interfaces:", aantal_interfaces)

print("Connected Devices (CDP Neighbors)")
print("---------------------------------")





print("Routing Table")
print("-------------")

output = connection.send_command("show ip route")

for line in output.splitlines():
    # Cisco IOS routing regels voor Connected (C) of Static (S) beginnen vaak met C of S
    if line.startswith("C") or line.startswith("S"):
        parts = line.split()
        
        # Controleer of de regel genoeg onderdelen heeft om vast te leggen
        if len(parts) >= 2:
            network = parts[1]                     # Het IP-netwerk (bijv. 10.0.0.0/24)
            interface = parts[-1].strip(",")       # De uitgaande interface (laatste woord, bijv. GigabitEthernet1)
            
            print(f"{network} via {interface}")