:: Find pip.conf or pip.ini, extract extra-index-url, and set it as an environment variable of EXTRA_INDEX_URL
@echo off
setlocal enabledelayedexpansion

:: Find pip.conf or pip.ini, extract extra-index-url, and set it as an environment variable of EXTRA_INDEX_URL
for %%f in (%USERPROFILE%\.pip\pip.conf %APPDATA%\pip\pip.ini %PROGRAMDATA%\pip\pip.ini ) do (
    if exist %%f (
        for /f "tokens=1,2 delims==" %%a in ('findstr /i "extra-index-url" %%f') do (
            set "urls=%%b"
            for /f "tokens=1 delims= " %%c in ("!urls!") do set "EXTRA_INDEX_URL=%%c"
            echo Found EXTRA_INDEX_URL: !EXTRA_INDEX_URL!
            goto :found
        )
    )
)

:: If not found, echo a message and exit
echo EXTRA_INDEX_URL not found in pip.conf or pip.ini
pause
exit /b 1

:found

:: Extract all hosts from EXTRA_INDEX_URL (which might contain multiple URLs)
set "EXTRA_INDEX_HOST="
for %%u in (!EXTRA_INDEX_URL!) do (
    for /f "tokens=2 delims=/" %%h in ("%%u") do (
        if "!EXTRA_INDEX_HOST!"=="" (
            set "EXTRA_INDEX_HOST=%%h"
        ) else (
            set "EXTRA_INDEX_HOST=!EXTRA_INDEX_HOST! %%h"
        )
    )
    echo Added host from URL: %%u
)

echo Final EXTRA_INDEX_HOST: !EXTRA_INDEX_HOST!

if "!EXTRA_INDEX_HOST!" == "" (
    echo Failed to extract EXTRA_INDEX_HOST from EXTRA_INDEX_URL
    pause
    exit /b 1
)


docker-compose up -d

pause
