from netmiko import ConnectHandler

router = {
    "device_type": "cisco_ios",
    "host": "192.168.56.20",      # IP van je CSR/CML-router
    "username": "ssh",
    "password": "ssh",
}

with ConnectHandler(**router) as conn:
    output = conn.send_command("show ssh")
    print(output)