from midi2audio import FluidSynth
import os

def test_soundfont():
    soundfont_path = os.path.join('app', 'static', 'soundfonts', 'FluidR3_GM', 'FluidR3_GM.sf2')
    print(f"测试 SoundFont 文件: {soundfont_path}")
    
    try:
        fs = FluidSynth(sound_font=soundfont_path)
        print("FluidSynth 初始化成功！")
        return True
    except Exception as e:
        print(f"错误: {str(e)}")
        return False

if __name__ == "__main__":
    test_soundfont() 