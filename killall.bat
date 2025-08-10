@echo off
setlocal enableDelayedExpansion

if "%~1" == "" (
  echo Usage: killall.bat process1 [process2] [process3] ...
  pause
  exit /b 1
)

for %%p in (%*) do (
  set process=%%p
  taskkill /F /IM !process!
)

echo All instances of the specified processes have been killed.
