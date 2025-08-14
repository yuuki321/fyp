@echo off
setlocal enabledelayedexpansion

:: 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 请以管理员身份运行此脚本！
    echo 右键点击脚本，选择"以管理员身份运行"
    pause
    exit /b 1
)

:: 设置变量
set "INSTALL_DIR=C:\Program Files\FluidSynth"
set "DOWNLOAD_URL=https://github.com/FluidSynth/fluidsynth/releases/download/v2.3.4/fluidsynth-2.3.4-win10-x64.zip"
set "TEMP_DIR=%TEMP%\fluidsynth_temp"
set "TEMP_ZIP=%TEMP_DIR%\fluidsynth.zip"

:: 创建临时目录
echo 创建临时目录...
if exist "%TEMP_DIR%" rd /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"

:: 下载 FluidSynth
echo 正在下载 FluidSynth...
bitsadmin /transfer FluidSynthDownload /download /priority normal "%DOWNLOAD_URL%" "%TEMP_ZIP%"

if not exist "%TEMP_ZIP%" (
    echo 下载失败！
    pause
    exit /b 1
)

:: 创建安装目录
echo 创建安装目录...
if exist "%INSTALL_DIR%" rd /s /q "%INSTALL_DIR%"
mkdir "%INSTALL_DIR%"

:: 解压文件
echo 解压文件...
cd /d "%TEMP_DIR%"
tar -xf "%TEMP_ZIP%"

:: 复制文件
echo 复制文件...
xcopy /E /I /Y "%TEMP_DIR%\bin\*" "%INSTALL_DIR%"

:: 设置环境变量
echo 设置环境变量...
setx PATH "%PATH%;%INSTALL_DIR%" /M

:: 刷新当前会话的环境变量
set "PATH=%PATH%;%INSTALL_DIR%"

:: 清理临时文件
echo 清理临时文件...
cd /d "%~dp0"
rd /s /q "%TEMP_DIR%"

:: 创建 soundfonts 目录
echo 创建 soundfonts 目录...
if not exist "app\static\soundfonts" mkdir "app\static\soundfonts"

:: 下载默认音色库
echo 下载默认音色库...
bitsadmin /transfer SoundfontDownload /download /priority normal "https://github.com/FluidSynth/fluidsynth/raw/master/sf2/VintageDreamsWaves-v2.sf2" "app\static\soundfonts\default.sf2"

:: 验证安装
echo 验证安装...
"%INSTALL_DIR%\fluidsynth.exe" --version
if %errorLevel% equ 0 (
    echo FluidSynth 安装成功！
) else (
    echo FluidSynth 安装可能有问题，请检查安装目录：%INSTALL_DIR%
)

echo.
echo 安装完成！请按照以下步骤操作：
echo 1. 关闭所有命令提示符窗口
echo 2. 重新打开命令提示符
echo 3. 运行 fluidsynth --version 验证安装
echo.

pause 