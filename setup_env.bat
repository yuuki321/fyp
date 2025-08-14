@echo off
echo 正在设置 FluidSynth 环境变量...

:: 检查是否以管理员权限运行
net session >nul 2>&1
if %errorLevel% == 0 (
    echo 正在以管理员权限运行...
) else (
    echo 请以管理员权限运行此脚本！
    echo 右键点击此脚本，选择"以管理员身份运行"
    pause
    exit /b 1
)

:: 检查 FluidSynth 目录是否存在
if not exist "C:\Program Files\FluidSynth" (
    echo 错误：找不到 FluidSynth 目录！
    echo 请确保 FluidSynth 已安装在 C:\Program Files\FluidSynth
    pause
    exit /b 1
)

:: 设置环境变量
setx PATH "%PATH%;C:\Program Files\FluidSynth" /M
if %errorLevel% == 0 (
    echo FluidSynth 环境变量设置完成！
    echo 当前 PATH: %PATH%
) else (
    echo 设置环境变量时出错！
)

echo.
echo 请按照以下步骤操作：
echo 1. 关闭所有命令提示符窗口
echo 2. 重新打开命令提示符
echo 3. 运行 fluidsynth --version 验证安装
echo.

pause 