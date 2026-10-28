import datetime 
import netmiko
import paramiko 

now = datetime.datetime.now()
print(now)

print("Paramiko:", paramiko.__version__) 
print("Netmiko:", netmiko.__version__)

print("\nKEX supported by Paramiko:") 
for kex in paramiko.Transport._preferred_kex:
    print(kex)