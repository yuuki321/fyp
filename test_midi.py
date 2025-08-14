import pretty_midi
from midi2audio import FluidSynth
import os

def create_test_midi():
    # 创建 MIDI 对象
    pm = pretty_midi.PrettyMIDI()
    
    # 创建钢琴音色
    piano_program = pretty_midi.Instrument(program=0)
    
    # 添加一个简单的 C 大调音阶
    for i, note_number in enumerate([60, 62, 64, 65, 67, 69, 71, 72]):  # C4 到 C5
        note = pretty_midi.Note(
            velocity=100,
            pitch=note_number,
            start=i * 0.5,  # 每个音符间隔 0.5 秒
            end=(i + 1) * 0.5
        )
        piano_program.notes.append(note)
    
    # 添加音轨
    pm.instruments.append(piano_program)
    
    # 保存 MIDI 文件
    midi_path = 'test.mid'
    pm.write(midi_path)
    print(f"MIDI 文件已保存: {midi_path}")
    
    # 转换为音频
    soundfont_path = os.path.join('app', 'static', 'soundfonts', 'FluidR3_GM', 'FluidR3_GM.sf2')
    fs = FluidSynth(sound_font=soundfont_path)
    audio_path = 'test.mp3'
    fs.midi_to_audio(midi_path, audio_path)
    print(f"音频文件已保存: {audio_path}")

if __name__ == "__main__":
    create_test_midi() 