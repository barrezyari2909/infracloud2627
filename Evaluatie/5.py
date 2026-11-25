from netmiko import ConnectHandler

router = {
    "device_type": "cisco_ios",
    "host": "192.168.56.20",
    "username": "ssh",
    "password": "ssh",
}


def print_sectie(titel, output):
    print("\n" + "=" * 60)
    print(titel)
    print("=" * 60)
    print(output)


def main():
    try:
        with ConnectHandler(**router) as conn:
            conn.enable()

            show_version = conn.send_command("show version")
            print_sectie("SHOW VERSION", show_version)

            hostname = conn.find_prompt().strip("#>")
            print(f"\nHostname: {hostname}")

            print_sectie(
                "INTERFACESTATUS (show ip interface brief)",
                conn.send_command("show ip interface brief"),
            )

            print_sectie(
                "ROUTINGTABEL (show ip route)",
                conn.send_command("show ip route"),
            )
            print_sectie(
                "ROUTINGPROTOCOLLEN (show ip protocols)",
                conn.send_command("show ip protocols"),
            )

    except Exception as e:
        print(f"Fout bij verbinden of uitvoeren: {e}")


if __name__ == "__main__":
    main()