# 检查是否以管理员权限运行
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]"Administrator")
if (-not $isAdmin) {
    Write-Warning "Please run this script as Administrator!"
    Write-Host "Right click the script and select 'Run as Administrator'"
    Read-Host "Press Enter to exit"
    exit 1
}

# 检查 FluidSynth 目录
$fluidSynthPath = "C:\Program Files\FluidSynth"
if (-not (Test-Path $fluidSynthPath)) {
    Write-Error "Error: FluidSynth directory not found!"
    Write-Host "Please make sure FluidSynth is installed at $fluidSynthPath"
    Read-Host "Press Enter to exit"
    exit 1
}

try {
    # 获取当前 PATH
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    
    # 检查是否已包含 FluidSynth
    if ($currentPath -notlike "*$fluidSynthPath*") {
        # 添加新路径
        $newPath = "$currentPath;$fluidSynthPath"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
        Write-Host "Successfully added FluidSynth to PATH!" -ForegroundColor Green
    } else {
        Write-Host "FluidSynth is already in PATH!" -ForegroundColor Yellow
    }
} catch {
    Write-Error "Error setting environment variable: $($_.Exception.Message)"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "`nPlease restart your command prompt or PowerShell for changes to take effect."
Read-Host "Press Enter to exit" 