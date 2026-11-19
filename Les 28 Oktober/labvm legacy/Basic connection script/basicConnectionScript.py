from netmiko import ConnectHandler
from netmiko.ssh_exception import NetmikoTimeoutException, AuthenticationException

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
}

try:
    print(f"Connecting to {v_host}:{v_ssh_port}...")
    with ConnectHandler(**device) as connection:
        print("Connected successfully!")

        # Vraag het sudo-wachtwoord op via stdin (-S) en wacht op de prompt
        output = connection.send_command(
            "sudo -S systemctl status ssh",
            expect_string=r"[Pp]assword",
        )
        # Stuur het wachtwoord door en wacht tot de shell-prompt terug is
        output += connection.send_command(
            v_password,
            expect_string=r"[$#]",
        )
        print("\n--- Command Output ---")
        print(output)

except NetmikoTimeoutException:
    print("Connection timed out. Check your network route.")
except AuthenticationException:
    print("Authentication failed. Check username and password.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")