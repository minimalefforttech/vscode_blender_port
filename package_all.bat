@echo off
REM Delete all files in the packages folder
if exist packages (
    del /q packages\*
) else (
    mkdir packages
)

REM Package the VSCode extension
cd vscode_extension
call vsce package
for %%f in (*.vsix) do move "%%f" "..\packages\"
cd ..

REM Zip the Blender addon
REM Assumes blender_addon is the folder to zip
powershell Compress-Archive -Path blender_scripts\addons\vscode_port -DestinationPath packages\vscode_port.zip -Force

echo Packaging complete.
