要使音乐生成功能正常工作，请按照以下步骤操作：

1. 下载 FluidSynth
Windows 用户：
- 访问 https://github.com/FluidSynth/fluidsynth/releases
- 下载最新的 Windows 版本
- 安装到系统中

2. 下载声音字体文件
- 访问 https://musical-artifacts.com/artifacts/files/fluid-r3-soundfont.zip
- 下载并解压缩
- 将 .sf2 文件重命名为 default.sf2
- 将文件放在此目录（app/static/soundfonts/）中

3. 重启应用程序

如果遇到问题，请检查：
- FluidSynth 是否正确安装
- default.sf2 文件是否存在于此目录
- 应用程序是否有权限访问这些文件 