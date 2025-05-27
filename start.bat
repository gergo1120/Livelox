@echo off
setlocal enabledelayedexpansion

:: Prompt user for URL
set /p input=Please enter the URL, it must ends with '=player': 

:: Use delayed expansion to safely echo the value
(
  echo !input!
) > URL.txt

echo URL saved to URL.txt
livelox_cheater.py
rmdir /s /q "%~dp0tiles"
@echo off
start "" "egyesitett_terkep.png"