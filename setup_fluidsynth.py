import os
import requests
import zipfile
import shutil
from tqdm import tqdm

def download_file(url, filename):
    """下载文件并显示进度条"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filename, 'wb') as f, tqdm(
        desc=filename,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for data in response.iter_content(chunk_size=1024):
            size = f.write(data)
            pbar.update(size)

def setup_soundfont():
    """下载并设置声音字体文件"""
    # 创建必要的目录
    os.makedirs('app/static/soundfonts', exist_ok=True)
    os.makedirs('temp', exist_ok=True)
    
    # 下载声音字体文件
    print("下载声音字体文件...")
    soundfont_url = "https://cdn.jsdelivr.net/gh/FluidSynth/fluidsynth@master/sf2/VintageDreamsWaves-v2.sf2"
    dst_path = "app/static/soundfonts/default.sf2"
    
    print(f"正在从 {soundfont_url} 下载声音字体文件...")
    download_file(soundfont_url, dst_path)
    print(f"声音字体文件已下载到: {dst_path}")

def setup_fluidsynth():
    """下载 FluidSynth"""
    print("\n下载 FluidSynth...")
    os.makedirs('temp/fluidsynth', exist_ok=True)
    
    # 下载 FluidSynth 二进制文件
    files_to_download = {
        'fluidsynth.exe': 'https://github.com/FluidSynth/fluidsynth/releases/download/v2.3.4/fluidsynth.exe',
        'libfluidsynth.dll': 'https://github.com/FluidSynth/fluidsynth/releases/download/v2.3.4/libfluidsynth.dll'
    }
    
    for filename, url in files_to_download.items():
        print(f"\n下载 {filename}...")
        output_path = os.path.join('temp/fluidsynth', filename)
        try:
            download_file(url, output_path)
        except Exception as e:
            print(f"下载 {filename} 时出错: {str(e)}")
            continue
    
    print("\nFluidSynth 文件已下载到 temp/fluidsynth 目录")
    print("请按照以下步骤完成安装：")
    print("1. 创建目录 C:\\Program Files\\FluidSynth")
    print("2. 将 temp/fluidsynth 中的所有文件复制到 C:\\Program Files\\FluidSynth")
    print("3. 将 C:\\Program Files\\FluidSynth 添加到系统环境变量 PATH 中")

if __name__ == "__main__":
    try:
        print("开始设置...")
        setup_soundfont()
        setup_fluidsynth()
        print("\n设置完成！")
        print("\n请确保：")
        print("1. FluidSynth 已正确安装并添加到系统环境变量")
        print("2. 声音字体文件存在于 app/static/soundfonts/default.sf2")
        
        # 清理临时文件
        if os.path.exists('temp'):
            shutil.rmtree('temp')
            print("\n临时文件已清理")
            
    except Exception as e:
        print(f"\n设置过程中出现错误：{str(e)}") 