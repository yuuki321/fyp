#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import zipfile
import datetime

def create_package():
    """创建项目代码包"""
    # 获取当前时间作为版本号
    now = datetime.datetime.now()
    version = now.strftime("%Y%m%d_%H%M%S")
    
    # 创建打包目录
    package_dir = f"ai_music_generator_v{version}"
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    
    # 要包含的目录和文件列表
    dirs_to_include = [
        "app",
        "migrations"
    ]
    
    files_to_include = [
        "run.py",
        "config.py",
        "requirements.txt",
        "README.md"
    ]
    
    # 复制目录
    for dir_name in dirs_to_include:
        if os.path.exists(dir_name):
            shutil.copytree(dir_name, os.path.join(package_dir, dir_name))
            print(f"已复制目录: {dir_name}")
        else:
            print(f"警告: 目录 {dir_name} 不存在，已跳过")
    
    # 复制文件
    for file_name in files_to_include:
        if os.path.exists(file_name):
            shutil.copy2(file_name, os.path.join(package_dir, file_name))
            print(f"已复制文件: {file_name}")
        else:
            print(f"警告: 文件 {file_name} 不存在，已跳过")
    
    # 创建必要的空目录
    os.makedirs(os.path.join(package_dir, "logs"), exist_ok=True)
    
    # 确保 static/generated 目录存在
    os.makedirs(os.path.join(package_dir, "app/static/generated"), exist_ok=True)
    
    # 创建一个空的 default_audio.mp3 文件（如果不存在）
    default_audio_path = os.path.join(package_dir, "app/static/generated/default_audio.mp3")
    if not os.path.exists(default_audio_path):
        with open(default_audio_path, 'wb') as f:
            f.write(b'')
        print("已创建空的 default_audio.mp3 文件")
    
    # 确保 soundfonts 目录存在
    os.makedirs(os.path.join(package_dir, "app/static/soundfonts"), exist_ok=True)
    
    # 创建 soundfonts 目录下的 README 文件
    with open(os.path.join(package_dir, "app/static/soundfonts/README.txt"), 'w', encoding='utf-8') as f:
        f.write("""请在此目录放置 SoundFont 文件，可以：

1. 下载 FluidR3_GM.sf2 文件:
   - 访问 https://musical-artifacts.com/artifacts/files/fluid-r3-soundfont.zip
   - 解压后将其放入 FluidR3_GM 目录中

2. 或者下载单个乐器的 SoundFont:
   - 创建 acoustic_grand_piano 目录
   - 下载 https://gleitz.github.io/midi-js-soundfonts/FluidR3_GM/acoustic_grand_piano-mp3.js
   - 放入 acoustic_grand_piano 目录中

启动应用程序前，请确保：
- FluidSynth 已安装
- 至少一个声音字体文件存在于此目录
        """)
    
    # 打包为zip文件
    zip_filename = f"{package_dir}.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(package_dir))
                zipf.write(file_path, arcname)
    
    print(f"\n打包完成！")
    print(f"打包文件: {zip_filename}")
    print(f"文件大小: {os.path.getsize(zip_filename) / (1024*1024):.2f} MB")
    
    # 清理临时目录
    shutil.rmtree(package_dir)
    print("已清理临时文件")

if __name__ == "__main__":
    create_package() 