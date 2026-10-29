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

output = connection.send_command("show running-config")
banner_motd = "ongekend"
for line in output.splitlines():
    if "banner motd" in line:
        banner_motd = line
print(banner_motd)