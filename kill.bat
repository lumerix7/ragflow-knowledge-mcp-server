@echo off

rem Capture command line parameter for quiet mode
set "quiet=%1"

rem Get the script folder path
set "script_folder=%~dp0"
rem Remove the trailing backslash from script_folder
set "script_folder=%script_folder:~0,-1%"
rem Extract the folder name from the script folder path
for %%a in ("%script_folder%") do set "name=%%~na"
rem Kill the process using the derived folder name
taskkill /IM %name%.exe /F

rem If not quiet mode (-q), then pause before exit
if /I not "%quiet%"=="-q" pause

exit
