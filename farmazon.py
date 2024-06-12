import winreg

# dword na 0
# Computer\HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Search\BingSearchEnabled
# dword na 1
# Computer\HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\Explorer\DisableSearchBoxSuggestions
# dword na 0
# Computer\HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize\AppsUseLightTheme
# dword na 0
# Computer\HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize\SystemUsesLightTheme

if __name__ == '__main__':
    windows_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows', 0, winreg.KEY_WRITE)
    explorer_key = winreg.CreateKey(windows_key, 'Explorer')
    winreg.SetValueEx(explorer_key, 'DisableSearchBoxSuggestions', 0, winreg.REG_DWORD, 1)

    search_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Search', 0, winreg.KEY_WRITE)
    winreg.SetValueEx(search_key, 'BingSearchEnabled', 0, winreg.REG_DWORD, 0)

    dark_apps_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize', 0, winreg.KEY_WRITE)
    winreg.SetValueEx(dark_apps_key, 'AppsUseLightTheme', 0, winreg.REG_DWORD, 0)

    dark_sys_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize', 0, winreg.KEY_WRITE)
    winreg.SetValueEx(dark_sys_key, 'SystemUsesLightTheme', 0, winreg.REG_DWORD, 0)

    for key in (explorer_key, windows_key, search_key, dark_apps_key, dark_sys_key): winreg.CloseKey(key)
