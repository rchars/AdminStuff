@echo off

net user admin admin /add
net localgroup Administrators admin /add

net localgroup Administrators worker /delete
net localgroup Users worker /add

reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v DefaultUserName /d worker /f
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v DefaultPassword /d "" /f
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v AutoAdminLogon /d 1 /f

echo All done!
pause
