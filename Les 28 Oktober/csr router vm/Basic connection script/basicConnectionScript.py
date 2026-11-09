from netmiko import ConnectHandler
import datetime

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
now = datetime.datetime.now()
connection = ConnectHandler(**device)
connection.enable()
output = connection.send_command("show ssh")
print("Datum van runnen script")
print("-----------------------")
print(now)
print(output)
connection.disconnect()