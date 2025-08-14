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
set "TEMP_ZIP=%TEMP%\fluidsynth.zip"
set "TEMP_DIR=%TEMP%\fluidsynth_temp"

:: 检查是否已安装
if exist "%INSTALL_DIR%\fluidsynth.exe" (
    echo FluidSynth 已安装在 %INSTALL_DIR%
    echo 正在验证安装...
    "%INSTALL_DIR%\fluidsynth.exe" --version
    if !errorLevel! equ 0 (
        echo FluidSynth 安装正常
        pause
        exit /b 0
    )
)

:: 创建临时目录
echo 创建临时目录...
if exist "%TEMP_DIR%" rd /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"

:: 创建安装目录
echo 创建安装目录...
if exist "%INSTALL_DIR%" rd /s /q "%INSTALL_DIR%"
mkdir "%INSTALL_DIR%"

:: 下载 FluidSynth
echo 下载 FluidSynth...
powershell -Command "& {
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%TEMP_ZIP%'
}"
if %errorLevel% neq 0 (
    echo 下载失败！
    echo 请检查网络连接或手动下载：
    echo %DOWNLOAD_URL%
    pause
    exit /b 1
)

:: 解压文件
echo 解压文件...
powershell -Command "& {
    Expand-Archive -Path '%TEMP_ZIP%' -DestinationPath '%TEMP_DIR%' -Force
    Get-ChildItem -Path '%TEMP_DIR%' -Recurse -File | Where-Object { $_.Name -match '\.exe$|\.dll$' } | Copy-Item -Destination '%INSTALL_DIR%' -Force
}"
if %errorLevel% neq 0 (
    echo 解压或复制文件失败！
    pause
    exit /b 1
)

:: 验证文件
if not exist "%INSTALL_DIR%\fluidsynth.exe" (
    echo 未找到 fluidsynth.exe！安装失败。
    pause
    exit /b 1
)

:: 添加到系统和用户的 PATH
echo 添加到系统环境变量...
powershell -Command "& {
    # 添加到系统 PATH
    $systemPath = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    if ($systemPath -notlike '*FluidSynth*') {
        $newSystemPath = $systemPath + ';%INSTALL_DIR%'
        [Environment]::SetEnvironmentVariable('Path', $newSystemPath, 'Machine')
        echo '已添加到系统 PATH: %INSTALL_DIR%'
    }
    
    # 添加到用户 PATH
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    if ($userPath -notlike '*FluidSynth*') {
        $newUserPath = $userPath + ';%INSTALL_DIR%'
        [Environment]::SetEnvironmentVariable('Path', $newUserPath, 'User')
        echo '已添加到用户 PATH: %INSTALL_DIR%'
    }
    
    # 刷新当前会话的 PATH
    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')
}"

:: 创建 PowerShell 配置文件
echo 创建 PowerShell 配置文件...
powershell -Command "& {
    $profilePath = $PROFILE.CurrentUserAllHosts
    $profileDir = Split-Path $profilePath -Parent
    
    if (-not (Test-Path $profileDir)) {
        New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
    }
    
    if (-not (Test-Path $profilePath)) {
        New-Item -ItemType File -Path $profilePath -Force | Out-Null
    }
    
    $content = @'
# 添加 FluidSynth 到 PATH
$fluidsynthPath = '%INSTALL_DIR%'
if ($env:Path -notlike '*FluidSynth*') {
    $env:Path += ";$fluidsynthPath"
}
'@
    
    Add-Content -Path $profilePath -Value $content -Force
    echo '已更新 PowerShell 配置文件'
}"

:: 清理临时文件
echo 清理临时文件...
if exist "%TEMP_ZIP%" del "%TEMP_ZIP%"
if exist "%TEMP_DIR%" rd /s /q "%TEMP_DIR%"

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
echo 1. 关闭所有命令提示符和 PowerShell 窗口
echo 2. 重新打开 PowerShell
echo 3. 运行以下命令刷新环境变量：
echo    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')
echo 4. 运行 'fluidsynth --version' 验证安装
echo.
pause 