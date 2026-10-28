import datetime
import netmiko
import paramiko

now = datetime.datetime.now()
print(now)
print(netmiko.__version__)
print(paramiko.__version__)

print("\nKEX algorithms supported by paramiko:")
for kex in netmiko.Transport._preferred_kex.kex:
    print(kex)