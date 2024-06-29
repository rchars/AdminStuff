@echo off

echo Setting admin account
net user admin admin /add
net localgroup Administrators admin /add
echo Setting admin password
net user admin *

echo Setting worker account
net localgroup Administrators worker /delete
net localgroup Users worker /add

echo Setting auto-logon for worker
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v DefaultUserName /d worker /f
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v DefaultPassword /d "worker" /f
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v AutoAdminLogon /d 1 /f

echo Setting password never expires for admin
wmic UserAccount where Name='admin' set PasswordExpires=false

echo Setting password never expires for worker
wmic UserAccount where Name='worker' set PasswordExpires=false

echo All done!
pause
