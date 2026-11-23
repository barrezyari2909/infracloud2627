from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoAuthenticationException, NetMikoTimeoutException

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

except NetMikoTimeoutException:
    print("connection timeout")
except NetMikoAuthenticationException:
    print("authentication failed check user and pass")
except Exception as e:
    print(f"An unexpected error occurred: {e}")