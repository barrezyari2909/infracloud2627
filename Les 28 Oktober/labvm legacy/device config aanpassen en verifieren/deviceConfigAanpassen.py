from netmiko import ConnectHandler

v_device_type = "cisco_ios"
v_host = "10.10.20.1"
v_ssh_port = 22
v_username = "cisco"
v_password = "cisco"

device = {
    "device_type": v_device_type,
    "host":v_host,
    "username": v_username,
    "password": v_password,
    "secret": v_password,
}

connection = ConnectHandler(**device)
connection.enable()

config_commands = [
    "service password-encryption",
    "banner motd #afblijven#"
]

output = connection.send_config_set(config_commands)
print(output)

connection.save_config()