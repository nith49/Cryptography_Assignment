@echo off
echo Setting up Windows Firewall Rules for UPI Payment System...

REM Add rules for Bank Server (Port 5001)
netsh advfirewall firewall add rule name="UPI Bank Server In" dir=in action=allow protocol=TCP localport=5001 remoteip=any
netsh advfirewall firewall add rule name="UPI Bank Server Out" dir=out action=allow protocol=TCP localport=5001 remoteip=any

REM Add rules for UPI Machine (Port 5002)
netsh advfirewall firewall add rule name="UPI Machine In" dir=in action=allow protocol=TCP localport=5002 remoteip=any
netsh advfirewall firewall add rule name="UPI Machine Out" dir=out action=allow protocol=TCP localport=5002 remoteip=any

REM Add rules for User Client (Port 5003)
netsh advfirewall firewall add rule name="UPI User Client In" dir=in action=allow protocol=TCP localport=5003 remoteip=any
netsh advfirewall firewall add rule name="UPI User Client Out" dir=out action=allow protocol=TCP localport=5003 remoteip=any

REM Add rules for Data Sync Server (Port 5005) 
netsh advfirewall firewall add rule name="UPI Data Sync In" dir=in action=allow protocol=TCP localport=5005 remoteip=any
netsh advfirewall firewall add rule name="UPI Data Sync Out" dir=out action=allow protocol=TCP localport=5005 remoteip=any

echo Firewall rules added successfully!
echo Please run this script on all laptops that will be part of the system.
pause