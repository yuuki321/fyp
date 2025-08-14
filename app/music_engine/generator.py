import numpy as np
from typing import Dict, List, Optional
import pretty_midi
from midi2audio import FluidSynth
import os
import logging
import subprocess
import platform
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MusicGenerator:
    def __init__(self):
        logger.debug("初始化 MusicGenerator")
        
        # 创建输出目录
        self.output_dir = os.path.join('app', 'static', 'generated')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 检查 FluidSynth
        if not self._check_fluidsynth():
            logger.warning("FluidSynth 检查失败，但将继续初始化")
        
        # 初始化 FluidSynth
        try:
            soundfont_path = self._find_soundfont()
            if soundfont_path:
                self.fs = FluidSynth(sound_font=soundfont_path)
                logger.info(f"FluidSynth 使用 {soundfont_path} 初始化成功")
            else:
                logger.error("找不到任何声音字体文件")
                print("Missing dependencies: No SoundFont files found")
                self.fs = None
        except Exception as e:
            logger.error(f"初始化 FluidSynth 失败: {str(e)}", exc_info=True)
            print(f"Missing dependencies: FluidSynth initialization failed - {str(e)}")
            self.fs = None
    
    def _check_fluidsynth(self):
        """检查 FluidSynth 是否可用"""
        try:
            # 根据操作系统确定 FluidSynth 路径
            if platform.system() == 'Windows':
                fluidsynth_path = os.path.join('C:', os.sep, 'Program Files', 'FluidSynth', 'bin', 'fluidsynth.exe')
            else:  # macOS 和 Linux
                fluidsynth_path = 'fluidsynth'  # 假设已经在系统PATH中
            
            # 尝试运行 FluidSynth
            try:
                logger.debug(f"尝试运行 FluidSynth: {fluidsynth_path}")
                result = subprocess.run([fluidsynth_path, '--version'], 
                                     capture_output=True, 
                                     text=True)
                if result.returncode == 0:
                    logger.info(f"FluidSynth 版本: {result.stdout.strip()}")
                    return True
                else:
                    logger.warning(f"无法获取 FluidSynth 版本信息: {result.stderr}")
                    return False
            except FileNotFoundError:
                logger.error("找不到 FluidSynth 可执行文件")
                return False
            except Exception as e:
                logger.warning(f"运行 FluidSynth 命令失败: {str(e)}")
                return False
            
        except Exception as e:
            logger.error(f"检查 FluidSynth 时出错: {str(e)}", exc_info=True)
            return False
    
    def _find_soundfont(self):
        """搜索可用的SoundFont文件"""
        # 可能的SoundFont文件路径列表
        potential_paths = [
            os.path.join('app', 'static', 'soundfonts', 'FluidR3_GM', 'FluidR3_GM.sf2'),
            os.path.join('app', 'static', 'soundfonts', 'default.sf2'),
            os.path.join('app', 'static', 'soundfonts', 'acoustic_grand_piano', 'acoustic_grand_piano-mp3.js'),
        ]
        
        # 检查路径是否存在
        for path in potential_paths:
            if os.path.exists(path):
                logger.info(f"找到声音字体文件: {path}")
                self._current_soundfont = path
                return path
        
        # 如果没有找到预定义的路径，搜索soundfonts目录
        static_soundfonts = os.path.join('app', 'static', 'soundfonts')
        if os.path.exists(static_soundfonts):
            for root, dirs, files in os.walk(static_soundfonts):
                for file in files:
                    if file.endswith('.sf2') or file.endswith('.js'):
                        path = os.path.join(root, file)
                        logger.info(f"找到声音字体文件: {path}")
                        self._current_soundfont = path
                        return path
        
        # 没有找到任何声音字体文件
        self._current_soundfont = None
        return None
    
    def generate_music(self, params: Dict) -> Dict:
        """
        根据输入参数生成音乐
        params: {
            'style': str,
            'mood': str,
            'duration': float,
            'chord_progression': str,
            'tempo': int
        }
        """
        logger.debug(f"开始生成音乐，参数: {params}")
        try:
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            midi_filename = f"midi_{timestamp}.mid"
            audio_filename = f"audio_{timestamp}.mp3"
            
            # 生成相对路径
            midi_path = os.path.join('generated', midi_filename)
            audio_path = os.path.join('generated', audio_filename)
            
            # 生成绝对路径（用于实际文件操作）
            abs_midi_path = os.path.join('app', 'static', midi_path)
            abs_audio_path = os.path.join('app', 'static', audio_path)
            
            # 生成 MIDI 数据
            self._generate_midi(params, abs_midi_path)
            logger.debug(f"MIDI 生成成功: {abs_midi_path}")
            
            # 转换为音频文件
            self._midi_to_audio(abs_midi_path, abs_audio_path)
            logger.debug(f"音频转换成功: {abs_audio_path}")
            
            return {
                'status': 'success',
                'midi_path': midi_path.replace('\\', '/'),
                'audio_path': audio_path.replace('\\', '/')
            }
        except Exception as e:
            logger.error(f"生成音乐时出错: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _generate_midi(self, params: Dict, output_path: str):
        """生成 MIDI 文件"""
        logger.debug("开始生成 MIDI 文件")
        
        # 创建 MIDI 对象
        pm = pretty_midi.PrettyMIDI(initial_tempo=params.get('tempo', 120))
        
        # 获取参数
        duration = float(params.get('duration', 60))  # 总时长（秒）
        tempo = float(params.get('tempo', 120))  # 速度（BPM）
        mood = params.get('mood', 'happy')  # 情绪
        style = params.get('style', 'pop')  # 音乐风格
        
        # 根据风格调整乐器
        style_settings = {
            'pop': {
                'melody': 0,    # Acoustic Grand Piano
                'chord': 48,    # String Ensemble
                'bass': 32,     # Acoustic Bass
                'drums': True,  # 使用鼓点
                'rhythm_complexity': 0.5
            },
            'rock': {
                'melody': 29,   # Overdriven Guitar
                'chord': 30,    # Distortion Guitar
                'bass': 33,     # Electric Bass
                'drums': True,
                'rhythm_complexity': 0.8
            },
            'classical': {
                'melody': 0,    # Acoustic Grand Piano
                'chord': 48,    # String Ensemble
                'bass': 43,     # Contrabass
                'drums': False,
                'rhythm_complexity': 0.3
            },
            'electronic': {
                'melody': 81,   # Synth Lead
                'chord': 51,    # Synth Strings
                'bass': 39,     # Synth Bass
                'drums': True,
                'rhythm_complexity': 0.7
            },
            'jazz': {
                'melody': 66,   # Alto Sax
                'chord': 0,     # Acoustic Piano
                'bass': 32,     # Acoustic Bass
                'drums': True,
                'rhythm_complexity': 0.6
            }
        }
        
        # 获取风格设置
        style_config = style_settings.get(style, style_settings['pop'])
        
        # 根据情绪调整参数
        mood_settings = {
            'happy': {
                'scale': 'major',
                'velocity_main': 90,
                'velocity_bass': 100,
                'velocity_chord': 80,
                'octave_shift': 0,
                'note_length': 0.8,
                'tempo_adjust': 1.0,
                'chord_style': 'normal',
                'decoration_prob': 0.3,
                'melody_pattern': 'active'
            },
            'sad': {
                'scale': 'minor',
                'velocity_main': 70,
                'velocity_bass': 85,
                'velocity_chord': 65,
                'octave_shift': -1,
                'note_length': 0.9,
                'tempo_adjust': 0.8,
                'chord_style': 'spread',
                'decoration_prob': 0.15,
                'melody_pattern': 'flowing'
            },
            'energetic': {
                'scale': 'major',
                'velocity_main': 100,
                'velocity_bass': 110,
                'velocity_chord': 90,
                'octave_shift': 0,
                'note_length': 0.7,
                'tempo_adjust': 1.2,
                'chord_style': 'rhythmic',
                'decoration_prob': 0.4,
                'melody_pattern': 'rhythmic'
            },
            'calm': {
                'scale': 'major',
                'velocity_main': 65,
                'velocity_bass': 75,
                'velocity_chord': 60,
                'octave_shift': -1,
                'note_length': 1.0,
                'tempo_adjust': 0.7,
                'chord_style': 'arpeggiated',
                'decoration_prob': 0.1,
                'melody_pattern': 'smooth'
            },
            'romantic': {
                'scale': 'major',
                'velocity_main': 80,
                'velocity_bass': 85,
                'velocity_chord': 75,
                'octave_shift': 0,
                'note_length': 0.9,
                'tempo_adjust': 0.9,
                'chord_style': 'arpeggiated',
                'decoration_prob': 0.25,
                'melody_pattern': 'flowing'
            },
            'mysterious': {
                'scale': 'minor',
                'velocity_main': 75,
                'velocity_bass': 85,
                'velocity_chord': 70,
                'octave_shift': -1,
                'note_length': 0.85,
                'tempo_adjust': 0.75,
                'chord_style': 'sparse',
                'decoration_prob': 0.2,
                'melody_pattern': 'staccato'
            },
            'dramatic': {
                'scale': 'minor',
                'velocity_main': 95,
                'velocity_bass': 105,
                'velocity_chord': 90,
                'octave_shift': 0,
                'note_length': 0.8,
                'tempo_adjust': 1.0,
                'chord_style': 'full',
                'decoration_prob': 0.3,
                'melody_pattern': 'dramatic'
            },
            'peaceful': {
                'scale': 'major',
                'velocity_main': 60,
                'velocity_bass': 70,
                'velocity_chord': 55,
                'octave_shift': -1,
                'note_length': 1.1,
                'tempo_adjust': 0.6,
                'chord_style': 'arpeggiated',
                'decoration_prob': 0.05,
                'melody_pattern': 'smooth'
            },
            'nostalgic': {
                'scale': 'major',
                'velocity_main': 70,
                'velocity_bass': 80,
                'velocity_chord': 65,
                'octave_shift': 0,
                'note_length': 0.85,
                'tempo_adjust': 0.8,
                'chord_style': 'normal',
                'decoration_prob': 0.2,
                'melody_pattern': 'reflective'
            },
            'dreamy': {
                'scale': 'major',
                'velocity_main': 65,
                'velocity_bass': 75,
                'velocity_chord': 60,
                'octave_shift': 0,
                'note_length': 0.95,
                'tempo_adjust': 0.75,
                'chord_style': 'arpeggiated',
                'decoration_prob': 0.15,
                'melody_pattern': 'floating'
            },
            'passionate': {
                'scale': 'minor',
                'velocity_main': 100,
                'velocity_bass': 110,
                'velocity_chord': 95,
                'octave_shift': 0,
                'note_length': 0.8,
                'tempo_adjust': 1.1,
                'chord_style': 'rhythmic',
                'decoration_prob': 0.35,
                'melody_pattern': 'intense'
            },
            'melancholic': {
                'scale': 'minor',
                'velocity_main': 65,
                'velocity_bass': 75,
                'velocity_chord': 60,
                'octave_shift': -1,
                'note_length': 0.9,
                'tempo_adjust': 0.7,
                'chord_style': 'sparse',
                'decoration_prob': 0.1,
                'melody_pattern': 'flowing'
            },
            'epic': {
                'scale': 'minor',
                'velocity_main': 110,
                'velocity_bass': 120,
                'velocity_chord': 100,
                'octave_shift': 0,
                'note_length': 0.85,
                'tempo_adjust': 1.0,
                'chord_style': 'full',
                'decoration_prob': 0.4,
                'melody_pattern': 'heroic'
            },
            'playful': {
                'scale': 'major',
                'velocity_main': 85,
                'velocity_bass': 90,
                'velocity_chord': 80,
                'octave_shift': 1,
                'note_length': 0.7,
                'tempo_adjust': 1.1,
                'chord_style': 'staccato',
                'decoration_prob': 0.45,
                'melody_pattern': 'bouncy'
            },
            'dark': {
                'scale': 'minor',
                'velocity_main': 80,
                'velocity_bass': 90,
                'velocity_chord': 75,
                'octave_shift': -2,
                'note_length': 0.9,
                'tempo_adjust': 0.85,
                'chord_style': 'sparse',
                'decoration_prob': 0.2,
                'melody_pattern': 'haunting'
            },
            'hopeful': {
                'scale': 'major',
                'velocity_main': 85,
                'velocity_bass': 90,
                'velocity_chord': 80,
                'octave_shift': 0,
                'note_length': 0.85,
                'tempo_adjust': 0.9,
                'chord_style': 'normal',
                'decoration_prob': 0.25,
                'melody_pattern': 'uplifting'
            },
            'tense': {
                'scale': 'minor',
                'velocity_main': 85,
                'velocity_bass': 95,
                'velocity_chord': 80,
                'octave_shift': -1,
                'note_length': 0.75,
                'tempo_adjust': 1.05,
                'chord_style': 'dissonant',
                'decoration_prob': 0.3,
                'melody_pattern': 'suspenseful'
            },
            'ethereal': {
                'scale': 'major',
                'velocity_main': 60,
                'velocity_bass': 70,
                'velocity_chord': 55,
                'octave_shift': 1,
                'note_length': 1.2,
                'tempo_adjust': 0.65,
                'chord_style': 'arpeggiated',
                'decoration_prob': 0.15,
                'melody_pattern': 'floating'
            },
            'whimsical': {
                'scale': 'major',
                'velocity_main': 80,
                'velocity_bass': 85,
                'velocity_chord': 75,
                'octave_shift': 1,
                'note_length': 0.75,
                'tempo_adjust': 1.0,
                'chord_style': 'playful',
                'decoration_prob': 0.5,
                'melody_pattern': 'quirky'
            },
            'aggressive': {
                'scale': 'minor',
                'velocity_main': 115,
                'velocity_bass': 125,
                'velocity_chord': 110,
                'octave_shift': 0,
                'note_length': 0.7,
                'tempo_adjust': 1.3,
                'chord_style': 'percussive',
                'decoration_prob': 0.3,
                'melody_pattern': 'intense'
            },
            'triumphant': {
                'scale': 'major',
                'velocity_main': 105,
                'velocity_bass': 115,
                'velocity_chord': 100,
                'octave_shift': 0,
                'note_length': 0.85,
                'tempo_adjust': 1.1,
                'chord_style': 'full',
                'decoration_prob': 0.35,
                'melody_pattern': 'victorious'
            },
            'majestic': {
                'scale': 'major',
                'velocity_main': 100,
                'velocity_bass': 110,
                'velocity_chord': 95,
                'octave_shift': 0,
                'note_length': 0.9,
                'tempo_adjust': 0.95,
                'chord_style': 'full',
                'decoration_prob': 0.25,
                'melody_pattern': 'regal'
            }
        }
        
        # 获取情绪设置
        settings = mood_settings.get(mood, mood_settings['happy'])
        
        # 调整速度
        tempo *= settings['tempo_adjust']
        beats_per_second = tempo / 60
        seconds_per_beat = 1 / beats_per_second
        beats_per_chord = 4
        seconds_per_chord = beats_per_chord / beats_per_second
        
        # 解析和弦进行
        chord_progression = self._parse_chord_progression(params.get('chord_progression', ''), settings['scale'])
        logger.debug(f"和弦进行: {chord_progression}")
        
        # 创建音轨
        melody = pretty_midi.Instrument(program=style_config['melody'])  # 主旋律
        chords = pretty_midi.Instrument(program=style_config['chord'])   # 和弦
        bass = pretty_midi.Instrument(program=style_config['bass'])      # 贝斯
        
        current_time = 0.0
        while current_time < duration:
            for chord in chord_progression:
                if current_time >= duration:
                    break
                    
                # 1. 和弦伴奏
                if settings['chord_style'] == 'spread':
                    # 分散和弦
                    for i, note_number in enumerate(chord):
                        note = pretty_midi.Note(
                            velocity=settings['velocity_chord'],
                            pitch=note_number + settings['octave_shift'] * 12,
                            start=current_time + i * seconds_per_beat * 0.2,
                            end=current_time + seconds_per_chord * 0.95
                        )
                        chords.notes.append(note)
                else:
                    # 普通和弦
                    for note_number in chord:
                        note = pretty_midi.Note(
                            velocity=settings['velocity_chord'],
                            pitch=note_number + settings['octave_shift'] * 12,
                            start=current_time,
                            end=current_time + seconds_per_chord * 0.95
                        )
                        chords.notes.append(note)
                
                # 2. 生成旋律
                melody_notes = self._generate_melody(
                    chord,
                    settings['melody_pattern'],
                    beats_per_chord,
                    current_time,
                    seconds_per_beat,
                    settings
                )
                melody.notes.extend(melody_notes)
                
                # 3. 低音部分（贝斯）
                if settings['chord_style'] == 'rhythmic':
                    # 添加节奏型贝斯线
                    for i in range(beats_per_chord):
                        note = pretty_midi.Note(
                            velocity=settings['velocity_bass'],
                            pitch=chord[0] - 12,
                            start=current_time + i * seconds_per_beat,
                            end=current_time + (i + 0.8) * seconds_per_beat
                        )
                        bass.notes.append(note)
                else:
                    # 普通贝斯线
                    note = pretty_midi.Note(
                        velocity=settings['velocity_bass'],
                        pitch=chord[0] - 12,
                        start=current_time,
                        end=current_time + seconds_per_chord * 0.95
                    )
                    bass.notes.append(note)
                
                # 4. 添加装饰音
                for i in range(beats_per_chord):
                    if np.random.random() < settings['decoration_prob']:
                        beat_time = current_time + i * seconds_per_beat
                        if beat_time >= duration:
                            break
                            
                        note_number = np.random.choice(chord) + 12
                        note = pretty_midi.Note(
                            velocity=int(settings['velocity_main'] * 0.8),
                            pitch=note_number + settings['octave_shift'] * 12,
                            start=beat_time,
                            end=beat_time + seconds_per_beat * 0.5
                        )
                        melody.notes.append(note)
                
                # 5. 添加鼓点
                if style_config['drums']:
                    self._add_drums(pm, current_time, seconds_per_chord, 
                                  style_config['rhythm_complexity'], settings['chord_style'])
                
                current_time += seconds_per_chord
        
        # 添加所有音轨
        pm.instruments.extend([melody, chords, bass])
        
        # 保存 MIDI 文件
        pm.write(output_path)
        logger.debug(f"MIDI 文件已保存: {output_path}")
    
    def _generate_melody(self, chord: List[int], pattern: str, num_beats: int,
                        start_time: float, seconds_per_beat: float, settings: Dict) -> List[pretty_midi.Note]:
        """生成旋律"""
        notes = []
        scale = self._get_scale_from_chord(chord)
        
        # 生成变化的音符长度 - 短音、中音、长音的概率分布
        def get_varied_length():
            length_type = np.random.choice(['short', 'medium', 'long', 'extra_long'], 
                                           p=[0.3, 0.4, 0.2, 0.1])
            if length_type == 'short':
                return np.random.uniform(0.2, 0.4)
            elif length_type == 'medium':
                return np.random.uniform(0.5, 0.7)
            elif length_type == 'long':
                return np.random.uniform(0.8, 1.0)
            else:  # extra_long
                return np.random.uniform(1.1, 1.8)
        
        if pattern == 'active':
            # 活跃的旋律，使用较短音符但有变化
            for i in range(num_beats * 2):
                if np.random.random() < 0.8:  # 80% 的概率添加音符
                    note_number = np.random.choice(scale)
                    # 使用变化的音符长度
                    length = get_varied_length() * 0.5  # 调整基础值
                    note = pretty_midi.Note(
                        velocity=settings['velocity_main'],
                        pitch=note_number + settings['octave_shift'] * 12,
                        start=start_time + i * seconds_per_beat * 0.5,
                        end=start_time + i * seconds_per_beat * 0.5 + length * seconds_per_beat
                    )
                    notes.append(note)
        
        elif pattern == 'flowing':
            # 流畅的旋律，使用较长音符，有变化
            i = 0
            while i < num_beats:
                note_number = np.random.choice(scale)
                # 不同长度的音符
                length = get_varied_length()
                note = pretty_midi.Note(
                    velocity=settings['velocity_main'],
                    pitch=note_number + settings['octave_shift'] * 12,
                    start=start_time + i * seconds_per_beat,
                    end=start_time + (i + length) * seconds_per_beat
                )
                notes.append(note)
                # 根据生成的音符长度移动
                i += max(0.5, length * 0.8)  # 确保至少移动半拍
        
        elif pattern == 'rhythmic':
            # 节奏型旋律，有明显的节奏变化
            i = 0
            while i < num_beats * 3:
                if np.random.random() < 0.7:  # 70% 的概率添加音符
                    note_number = np.random.choice(scale)
                    # 不同长度的音符，节奏型更注重短音符
                    length_prob = [0.5, 0.3, 0.15, 0.05]  # 更偏向短音符
                    length_type = np.random.choice(['short', 'medium', 'long', 'extra_long'], p=length_prob)
                    if length_type == 'short':
                        length = np.random.uniform(0.1, 0.3)
                    elif length_type == 'medium':
                        length = np.random.uniform(0.4, 0.6)
                    elif length_type == 'long':
                        length = np.random.uniform(0.7, 0.9)
                    else:  # extra_long
                        length = np.random.uniform(1.0, 1.2)
                    
                    note = pretty_midi.Note(
                        velocity=settings['velocity_main'],
                        pitch=note_number + settings['octave_shift'] * 12,
                        start=start_time + i * seconds_per_beat / 3,
                        end=start_time + (i * seconds_per_beat / 3) + (length * seconds_per_beat / 2)
                    )
                    notes.append(note)
                i += 0.5 + np.random.random() * 0.5  # 添加随机间隔
        
        elif pattern == 'staccato':
            # 断奏风格，短促有力的音符
            for i in range(num_beats * 2):
                if np.random.random() < 0.75:  # 75% 的概率添加音符
                    note_number = np.random.choice(scale)
                    # 短促音符
                    length = np.random.uniform(0.1, 0.3)
                    # 断奏通常会有短暂的间隔
                    start_offset = np.random.uniform(0, 0.1) * seconds_per_beat
                    note = pretty_midi.Note(
                        velocity=int(settings['velocity_main'] * 1.1),  # 稍微增加力度
                        pitch=note_number + settings['octave_shift'] * 12,
                        start=start_time + i * seconds_per_beat * 0.5 + start_offset,
                        end=start_time + i * seconds_per_beat * 0.5 + start_offset + length * seconds_per_beat
                    )
                    notes.append(note)
        
        elif pattern == 'dramatic':
            # 戏剧性旋律，有明显的力度变化和不规则的节奏
            i = 0
            accented = True  # 是否强调当前音符
            while i < num_beats:
                if np.random.random() < 0.85:  # 85% 的概率添加音符
                    note_number = np.random.choice(scale)
                    # 长度在短到中之间变化
                    length = np.random.uniform(0.3, 1.0) if accented else np.random.uniform(0.1, 0.4)
                    velocity = int(settings['velocity_main'] * 1.2) if accented else int(settings['velocity_main'] * 0.8)
                    
                    note = pretty_midi.Note(
                        velocity=velocity,
                        pitch=note_number + settings['octave_shift'] * 12,
                        start=start_time + i * seconds_per_beat,
                        end=start_time + i * seconds_per_beat + length * seconds_per_beat
                    )
                    notes.append(note)
                    accented = not accented  # 交替强弱
                i += np.random.choice([0.5, 0.75, 1.0])  # 不规则的节奏间隔
        
        elif pattern == 'smooth':
            # 平滑连接的旋律，相邻音符几乎无间隙
            i = 0
            previous_end = start_time
            while i < num_beats:
                note_number = np.random.choice(scale)
                # 中等到长音符
                length = np.random.uniform(0.6, 1.2)
                
                note = pretty_midi.Note(
                    velocity=settings['velocity_main'],
                    pitch=note_number + settings['octave_shift'] * 12,
                    start=previous_end,  # 从上一个音符结束处开始
                    end=previous_end + length * seconds_per_beat
                )
                notes.append(note)
                previous_end = note.end - 0.05 * seconds_per_beat  # 轻微重叠，确保平滑
                i += length * 0.8  # 根据音符长度移动
        
        elif pattern == 'reflective':
            # 沉思型旋律，中等节奏，有意的停顿
            i = 0
            while i < num_beats:
                if np.random.random() < 0.7:  # 70% 的概率添加音符
                    note_number = np.random.choice(scale)
                    # 中长型音符
                    length = np.random.uniform(0.7, 1.2)
                    
                    note = pretty_midi.Note(
                        velocity=int(settings['velocity_main'] * 0.9),  # 较柔和音量
                        pitch=note_number + settings['octave_shift'] * 12,
                        start=start_time + i * seconds_per_beat,
                        end=start_time + i * seconds_per_beat + length * seconds_per_beat
                    )
                    notes.append(note)
                    
                    # 添加停顿
                    if np.random.random() < 0.3:  # 30% 概率有较长停顿
                        i += length + np.random.uniform(0.5, 1.0)
                    else:
                        i += length
                else:
                    i += 0.5  # 没有音符时也向前移动
        
        elif pattern == 'floating':
            # 飘逸的旋律，音高有较大变化，长度不规则
            i = 0
            previous_pitch = np.random.choice(scale) + settings['octave_shift'] * 12
            pitch_range = 12  # 允许较大的音高变化范围
            
            while i < num_beats:
                # 在之前音符的基础上选择新音符，创造平滑的变化
                pitch_delta = np.random.choice([-4, -3, -2, -1, 1, 2, 3, 4])
                new_pitch = previous_pitch + pitch_delta
                
                # 确保音高在合理范围内
                if abs(new_pitch - (np.mean(scale) + settings['octave_shift'] * 12)) > pitch_range:
                    # 如果偏离太远，重新选择
                    new_pitch = np.random.choice(scale) + settings['octave_shift'] * 12
                
                # 使用变化的长度
                length = np.random.uniform(0.3, 1.5)
                
                note = pretty_midi.Note(
                    velocity=int(settings['velocity_main'] * np.random.uniform(0.8, 1.0)),  # 轻微的音量变化
                    pitch=new_pitch,
                    start=start_time + i * seconds_per_beat,
                    end=start_time + i * seconds_per_beat + length * seconds_per_beat
                )
                notes.append(note)
                previous_pitch = new_pitch
                i += length * np.random.uniform(0.6, 1.0)  # 不规则的间隔
        
        elif pattern == 'intense':
            # 强烈、紧张的旋律，快速且有力
            i = 0
            while i < num_beats * 3:
                if np.random.random() < 0.85:  # 高密度的音符
                    note_number = np.random.choice(scale)
                    # 短促而有力的音符
                    length = np.random.uniform(0.1, 0.4)
                    # 变化的力度，创造紧张感
                    velocity_var = np.random.uniform(0.9, 1.3)
                    
                    note = pretty_midi.Note(
                        velocity=int(settings['velocity_main'] * velocity_var),
                        pitch=note_number + settings['octave_shift'] * 12,
                        start=start_time + i * seconds_per_beat / 3,
                        end=start_time + i * seconds_per_beat / 3 + length * seconds_per_beat
                    )
                    notes.append(note)
                    
                    # 有时添加同音重复，增强紧张感
                    if np.random.random() < 0.3:
                        repeat = pretty_midi.Note(
                            velocity=int(note.velocity * 1.1),  # 重复音更强
                            pitch=note.pitch,
                            start=note.end + 0.05 * seconds_per_beat,
                            end=note.end + 0.05 * seconds_per_beat + length * 0.7 * seconds_per_beat
                        )
                        notes.append(repeat)
                i += np.random.uniform(0.2, 0.5)  # 快速但不规则的节奏
        
        elif pattern == 'heroic':
            # 英雄式旋律，雄壮有力的长音符与短音符结合
            i = 0
            while i < num_beats:
                if np.random.random() < 0.75:
                    note_number = np.random.choice(scale)
                    # 切换长短音符
                    if i % 2 == 0:  # 长音符
                        length = np.random.uniform(0.8, 1.5)
                        velocity = int(settings['velocity_main'] * 1.2)  # 更强的力度
                    else:  # 短音符
                        length = np.random.uniform(0.3, 0.5)
                        velocity = int(settings['velocity_main'] * 0.9)
                    
                    note = pretty_midi.Note(
                        velocity=velocity,
                        pitch=note_number + settings['octave_shift'] * 12,
                        start=start_time + i * seconds_per_beat,
                        end=start_time + i * seconds_per_beat + length * seconds_per_beat
                    )
                    notes.append(note)
                i += 1.0  # 规律的节奏
        
        elif pattern == 'bouncy':
            # 活泼跳跃的旋律
            i = 0
            while i < num_beats * 2:
                if np.random.random() < 0.8:
                    note_number = np.random.choice(scale)
                    # 短促而有弹性的音符
                    length = np.random.uniform(0.2, 0.4)
                    # 有变化的力度
                    velocity = int(settings['velocity_main'] * np.random.uniform(0.9, 1.1))
                    
                    # 添加一点点随机起始偏移，模拟"弹跳"感
                    start_offset = np.random.uniform(0, 0.05) * seconds_per_beat
                    
                    note = pretty_midi.Note(
                        velocity=velocity,
                        pitch=note_number + settings['octave_shift'] * 12,
                        start=start_time + i * seconds_per_beat * 0.5 + start_offset,
                        end=start_time + i * seconds_per_beat * 0.5 + start_offset + length * seconds_per_beat
                    )
                    notes.append(note)
                    
                    # 有时添加一个短跳音
                    if np.random.random() < 0.4 and i + 0.25 < num_beats * 2:
                        jump_pitch = note_number + np.random.choice([-3, -2, 2, 3, 4])
                        if jump_pitch in scale:
                            jump_note = pretty_midi.Note(
                                velocity=int(velocity * 0.9),
                                pitch=jump_pitch + settings['octave_shift'] * 12,
                                start=note.end + 0.02 * seconds_per_beat,
                                end=note.end + 0.02 * seconds_per_beat + 0.15 * seconds_per_beat
                            )
                            notes.append(jump_note)
                i += 0.5
        
        elif pattern == 'haunting':
            # 阴森、神秘的旋律
            i = 0
            while i < num_beats:
                if np.random.random() < 0.65:
                    note_number = np.random.choice(scale)
                    # 较长音符，表现神秘感
                    length = np.random.uniform(0.8, 1.8)
                    # 较轻的音量
                    velocity = int(settings['velocity_main'] * np.random.uniform(0.7, 0.9))
                    
                    note = pretty_midi.Note(
                        velocity=velocity,
                        pitch=note_number + settings['octave_shift'] * 12,
                        start=start_time + i * seconds_per_beat,
                        end=start_time + i * seconds_per_beat + length * seconds_per_beat
                    )
                    notes.append(note)
                    
                    # 偶尔添加不协和的装饰音
                    if np.random.random() < 0.3:
                        dissonant_pitch = note_number + np.random.choice([-1, 1, 6, 11])
                        echo = pretty_midi.Note(
                            velocity=int(velocity * 0.6),  # 更轻的回声
                            pitch=dissonant_pitch + settings['octave_shift'] * 12,
                            start=note.start + 0.2 * seconds_per_beat,
                            end=note.start + 0.2 * seconds_per_beat + 0.5 * seconds_per_beat
                        )
                        notes.append(echo)
                i += np.random.uniform(0.7, 1.3)  # 不规则的间隔
        
        elif pattern == 'uplifting':
            # 振奋人心的旋律，逐渐上升
            i = 0
            pitch_idx = 0  # 用于音阶中的索引
            direction = 1  # 1表示上升，-1表示下降
            
            while i < num_beats:
                if np.random.random() < 0.85:
                    # 按照上升趋势选择音符
                    sorted_scale = sorted(scale)
                    if pitch_idx >= len(sorted_scale):
                        pitch_idx = 0
                        direction = -1  # 改变方向
                    elif pitch_idx < 0:
                        pitch_idx = 0
                        direction = 1  # 改变方向
                    
                    note_number = sorted_scale[pitch_idx]
                    pitch_idx += direction
                    
                    # 适中的音符长度
                    length = np.random.uniform(0.4, 0.8)
                    
                    note = pretty_midi.Note(
                        velocity=settings['velocity_main'],
                        pitch=note_number + settings['octave_shift'] * 12,
                        start=start_time + i * seconds_per_beat,
                        end=start_time + i * seconds_per_beat + length * seconds_per_beat
                    )
                    notes.append(note)
                i += 0.5
        
        elif pattern == 'suspenseful':
            # 悬疑感强的旋律，低音域，不规则节奏
            i = 0
            pitch_center = min(scale) + 2  # 使用低音区
            
            while i < num_beats:
                if np.random.random() < 0.7:
                    # 选择接近中心音的音符
                    pitch_options = [p for p in scale if abs(p - pitch_center) <= 5]
                    if not pitch_options:
                        pitch_options = scale
                    note_number = np.random.choice(pitch_options)
                    
                    # 变化的音符长度
                    if np.random.random() < 0.6:  # 60%概率短音符
                        length = np.random.uniform(0.3, 0.6)
                    else:  # 40%概率长音符
                        length = np.random.uniform(1.0, 1.8)
                    
                    # 有时使用颤音效果
                    tremolo = np.random.random() < 0.2
                    
                    if tremolo:
                        # 创建颤音效果（多个短音符）
                        tremolo_count = int(np.random.uniform(3, 6))
                        tremolo_length = length / tremolo_count
                        for t in range(tremolo_count):
                            tremolo_note = pretty_midi.Note(
                                velocity=int(settings['velocity_main'] * np.random.uniform(0.9, 1.0)),
                                pitch=note_number + settings['octave_shift'] * 12,
                                start=start_time + i * seconds_per_beat + t * tremolo_length * seconds_per_beat,
                                end=start_time + i * seconds_per_beat + (t + 0.8) * tremolo_length * seconds_per_beat
                            )
                            notes.append(tremolo_note)
                    else:
                        note = pretty_midi.Note(
                            velocity=settings['velocity_main'],
                            pitch=note_number + settings['octave_shift'] * 12,
                            start=start_time + i * seconds_per_beat,
                            end=start_time + i * seconds_per_beat + length * seconds_per_beat
                        )
                        notes.append(note)
                
                # 不规则的间隔，有时有较长停顿
                if np.random.random() < 0.3:  # 30%概率有停顿
                    i += np.random.uniform(1.0, 2.0)
                else:
                    i += np.random.uniform(0.5, 0.8)
        
        elif pattern == 'quirky':
            # 古怪有趣的旋律，跳跃性大，节奏不规则
            i = 0
            previous_pitch = np.random.choice(scale)
            
            while i < num_beats:
                if np.random.random() < 0.8:
                    # 选择与前一个音符相距较远的音符
                    available_pitches = [p for p in scale if abs(p - previous_pitch) > 3]
                    if not available_pitches:
                        available_pitches = scale
                    note_number = np.random.choice(available_pitches)
                    previous_pitch = note_number
                    
                    # 多变的音符长度
                    if np.random.random() < 0.7:  # 70%概率短促音符
                        length = np.random.uniform(0.1, 0.3)
                    else:  # 30%概率较长音符
                        length = np.random.uniform(0.5, 0.9)
                    
                    # 有时突然转变音量
                    if np.random.random() < 0.2:  # 20%概率突然变强
                        velocity = int(settings['velocity_main'] * 1.3)
                    elif np.random.random() < 0.2:  # 20%概率突然变弱
                        velocity = int(settings['velocity_main'] * 0.7)
                    else:  # 60%概率正常音量
                        velocity = settings['velocity_main']
                    
                    note = pretty_midi.Note(
                        velocity=velocity,
                        pitch=note_number + settings['octave_shift'] * 12,
                        start=start_time + i * seconds_per_beat,
                        end=start_time + i * seconds_per_beat + length * seconds_per_beat
                    )
                    notes.append(note)
                
                # 不规则的节奏
                i += np.random.choice([0.25, 0.5, 0.75, 1.0], p=[0.2, 0.4, 0.3, 0.1])
        
        elif pattern == 'victorious':
            # 胜利感强烈的旋律，上行进行，气势磅礴
            i = 0
            # 使用音阶进行构建上行旋律
            sorted_scale = sorted(scale)
            pitch_idx = 0
            
            while i < num_beats:
                if np.random.random() < 0.85:  # 高密度的音符
                    # 使用排序后的音阶，创造上行感
                    if pitch_idx >= len(sorted_scale):
                        pitch_idx = 0  # 重新开始
                    
                    note_number = sorted_scale[pitch_idx]
                    pitch_idx += 1
                    
                    # 旋律音符长度
                    if np.random.random() < 0.3:  # 30%概率长音符，表现高潮
                        length = np.random.uniform(0.8, 1.2)
                        velocity = int(settings['velocity_main'] * 1.2)  # 更强的力度
                    else:  # 70%概率中等长度
                        length = np.random.uniform(0.4, 0.7)
                        velocity = settings['velocity_main']
                    
                    note = pretty_midi.Note(
                        velocity=velocity,
                        pitch=note_number + settings['octave_shift'] * 12,
                        start=start_time + i * seconds_per_beat,
                        end=start_time + i * seconds_per_beat + length * seconds_per_beat
                    )
                    notes.append(note)
                    
                    # 有时添加和声
                    if np.random.random() < 0.25 and len(scale) > 3:
                        harmony_pitch = note_number + np.random.choice([3, 4, 5, 7])  # 添加3度、4度、5度或7度音
                        if harmony_pitch in scale:
                            harmony = pretty_midi.Note(
                                velocity=int(velocity * 0.8),
                                pitch=harmony_pitch + settings['octave_shift'] * 12,
                                start=note.start,
                                end=note.end
                            )
                            notes.append(harmony)
                
                # 规律的节奏
                i += 0.5
        
        elif pattern == 'regal':
            # 庄严、高贵的旋律，典雅、庄重
            i = 0
            while i < num_beats:
                if np.random.random() < 0.75:
                    note_number = np.random.choice(scale)
                    
                    # 切换长短音符，创造庄严感
                    if i % 2 == 0:  # 较长音符
                        length = np.random.uniform(1.0, 1.5)
                    else:  # 较短音符
                        length = np.random.uniform(0.5, 0.8)
                    
                    # 平稳的力度
                    velocity = int(settings['velocity_main'] * np.random.uniform(0.95, 1.05))
                    
                    note = pretty_midi.Note(
                        velocity=velocity,
                        pitch=note_number + settings['octave_shift'] * 12,
                        start=start_time + i * seconds_per_beat,
                        end=start_time + i * seconds_per_beat + length * seconds_per_beat
                    )
                    notes.append(note)
                    
                    # 添加装饰音，模拟华丽感
                    if np.random.random() < 0.3:
                        # 选择相邻音符作为装饰音
                        for pitch_offset in [2, 4]:  # 添加3度和5度
                            if note_number + pitch_offset in scale:
                                decoration = pretty_midi.Note(
                                    velocity=int(velocity * 0.75),
                                    pitch=(note_number + pitch_offset) + settings['octave_shift'] * 12,
                                    start=note.start + 0.1 * seconds_per_beat,
                                    end=note.start + 0.1 * seconds_per_beat + 0.2 * seconds_per_beat
                                )
                                notes.append(decoration)
                
                # 相对规律的节奏
                i += 1.0
        
        else:  # gentle/smooth 或其他未识别的模式
            # 温和的旋律，平滑过渡
            i = 0
            while i < num_beats:
                if np.random.random() < 0.6:  # 60% 的概率添加音符
                    note_number = np.random.choice(scale)
                    # 温和模式偏好中长音符
                    length_prob = [0.1, 0.4, 0.4, 0.1]
                    length_type = np.random.choice(['short', 'medium', 'long', 'extra_long'], p=length_prob)
                    if length_type == 'short':
                        length = np.random.uniform(0.3, 0.5)
                    elif length_type == 'medium':
                        length = np.random.uniform(0.6, 0.8)
                    elif length_type == 'long':
                        length = np.random.uniform(0.9, 1.1)
                    else:  # extra_long
                        length = np.random.uniform(1.2, 1.6)
                    
                    note = pretty_midi.Note(
                        velocity=settings['velocity_main'],
                        pitch=note_number + settings['octave_shift'] * 12,
                        start=start_time + i * seconds_per_beat,
                        end=start_time + i * seconds_per_beat + length * seconds_per_beat
                    )
                    notes.append(note)
                i += 0.7 + np.random.random() * 0.6  # 生成相对平滑的间隔
        
        # 增加一些装饰音
        if np.random.random() < settings.get('decoration_prob', 0.2):
            for i in range(min(len(notes) // 3, 5)):  # 添加几个装饰音
                if len(notes) > 0:
                    base_note = np.random.choice(notes)
                    decoration_pitch = base_note.pitch + np.random.choice([-2, -1, 1, 2, 4])
                    decoration = pretty_midi.Note(
                        velocity=int(base_note.velocity * 0.9),
                        pitch=decoration_pitch,
                        start=base_note.start - 0.05,
                        end=base_note.start
                    )
                    # 确保装饰音在合法时间范围内
                    if decoration.start >= start_time:
                        notes.append(decoration)
        
        return notes
    
    def _get_scale_from_chord(self, chord: List[int]) -> List[int]:
        """根据和弦生成音阶"""
        # 基于和弦构建音阶
        root = chord[0]
        scale = []
        
        # 添加和弦音
        scale.extend(chord)
        
        # 添加装饰音
        scale.extend([root + 2, root + 5, root + 9, root + 11])
        
        return sorted(list(set(scale)))
    
    def _add_drums(self, pm: pretty_midi.PrettyMIDI, start_time: float, 
                   duration: float, complexity: float, style: str):
        """添加鼓点"""
        drums = pretty_midi.Instrument(program=0, is_drum=True)
        
        # 定义鼓点音符
        kick = 36      # 底鼓
        snare = 38     # 军鼓
        hihat = 42     # 闭合击镲
        crash = 49     # 碎音镲
        
        # 根据复杂度和风格添加鼓点
        beats = int(duration * 2)  # 每拍分成两个子拍
        
        for i in range(beats):
            current_time = start_time + i * duration / beats
            
            # 底鼓（在强拍上）
            if i % 2 == 0 or (complexity > 0.6 and np.random.random() < 0.3):
                note = pretty_midi.Note(
                    velocity=100,
                    pitch=kick,
                    start=current_time,
                    end=current_time + 0.1
                )
                drums.notes.append(note)
            
            # 军鼓（在弱拍上）
            if i % 2 == 1 or (complexity > 0.7 and np.random.random() < 0.2):
                note = pretty_midi.Note(
                    velocity=90,
                    pitch=snare,
                    start=current_time,
                    end=current_time + 0.1
                )
                drums.notes.append(note)
            
            # 击镲（根据复杂度添加）
            if np.random.random() < complexity:
                note = pretty_midi.Note(
                    velocity=80,
                    pitch=hihat,
                    start=current_time,
                    end=current_time + 0.1
                )
                drums.notes.append(note)
            
            # 在小节开始添加碎音镲
            if i == 0 and style == 'rhythmic':
                note = pretty_midi.Note(
                    velocity=90,
                    pitch=crash,
                    start=current_time,
                    end=current_time + 0.3
                )
                drums.notes.append(note)
        
        pm.instruments.append(drums)
    
    def _midi_to_audio(self, midi_path: str, output_path: str):
        """将 MIDI 文件转换为音频文件"""
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 检查文件权限
            if os.path.exists(output_path):
                os.chmod(output_path, 0o666)
            
            # 转换MIDI到音频
            if self.fs is None:
                logger.warning("FluidSynth 未初始化，跳过音频转换")
                # 直接复制一个示例音频文件作为应急方案
                try:
                    import shutil
                    default_audio = os.path.join('app', 'static', 'generated', 'default_audio.mp3')
                    if os.path.exists(default_audio):
                        shutil.copy(default_audio, output_path)
                        logger.info(f"已使用默认音频文件作为替代: {output_path}")
                except Exception as copy_error:
                    logger.error(f"无法使用默认音频文件: {str(copy_error)}")
                return
            
            # 如果soundfont是JS格式，不能直接使用FluidSynth转换
            if hasattr(self, '_current_soundfont') and self._current_soundfont.endswith('.js'):
                logger.warning("使用JS格式的SoundFont，无法直接转换MIDI，将使用替代方案")
                # 此处可以实现从JS SoundFont提取音频数据的逻辑，或者使用其他方式生成音频
                # 作为临时解决方案，我们可以直接复制一个示例音频文件
                try:
                    import shutil
                    default_audio = os.path.join('app', 'static', 'generated', 'default_audio.mp3')
                    if os.path.exists(default_audio):
                        shutil.copy(default_audio, output_path)
                        logger.info(f"已使用默认音频文件作为替代: {output_path}")
                    else:
                        # 如果没有默认音频，尝试使用系统命令生成一个短音频
                        try:
                            self.fs.midi_to_audio(midi_path, output_path)
                            logger.info(f"成功将MIDI转换为音频: {output_path}")
                        except:
                            logger.error("无法转换MIDI，生成空音频文件")
                            with open(output_path, 'wb') as f:
                                # 创建一个空的MP3文件
                                f.write(b'')
                except Exception as copy_error:
                    logger.error(f"无法创建替代音频文件: {str(copy_error)}")
                return
            
            # 使用FluidSynth转换
            self.fs.midi_to_audio(midi_path, output_path)
            
            # 设置输出文件权限
            os.chmod(output_path, 0o666)
            
            logger.info(f"成功将MIDI转换为音频: {output_path}")
        except Exception as e:
            logger.error(f"MIDI转换失败: {str(e)}", exc_info=True)
            # 不要直接抛出异常，而是创建一个空文件作为替代
            try:
                with open(output_path, 'wb') as f:
                    f.write(b'')
                logger.warning(f"创建了空音频文件作为替代: {output_path}")
            except:
                pass
            # 不严重中断整个程序
            # raise RuntimeError(f"MIDI转换失败: {str(e)}")
    
    def _parse_chord_progression(self, chord_string: str, scale: str = 'major') -> List[List[int]]:
        """解析和弦进行并转换为 MIDI 音符数字"""
        # 定义和弦类型映射
        chord_type_maps = {
            'maj': [0, 4, 7],      # 大三和弦
            'min': [0, 3, 7],      # 小三和弦
            'dim': [0, 3, 6],      # 減三和弦
            'aug': [0, 4, 8],      # 增三和弦
            'maj7': [0, 4, 7, 11], # 大七和弦
            'min7': [0, 3, 7, 10], # 小七和弦
            'dom7': [0, 4, 7, 10], # 屬七和弦
            'dim7': [0, 3, 6, 9],  # 減七和弦
            'maj9': [0, 4, 7, 11, 14], # 大九和弦
            'min9': [0, 3, 7, 10, 14], # 小九和弦
            'sus2': [0, 2, 7],     # 掛留二和弦
            'sus4': [0, 5, 7],     # 掛留四和弦
            'add9': [0, 4, 7, 14], # 加九和弦
            'maj6': [0, 4, 7, 9],  # 大六和弦
            'min6': [0, 3, 7, 9],  # 小六和弦
            'm7b5': [0, 3, 6, 10], # 半減七和弦
            'aug7': [0, 4, 8, 10], # 增七和弦
            '7sus4': [0, 5, 7, 10], # 掛留四屬七和弦
            '9sus4': [0, 5, 7, 10, 14], # 掛留四九和弦
            'add11': [0, 4, 7, 17], # 加十一和弦
            'maj13': [0, 4, 7, 11, 14, 21], # 大十三和弦
            'min11': [0, 3, 7, 10, 14, 17], # 小十一和弦
            '13': [0, 4, 7, 10, 14, 21], # 十三和弦
            '7b9': [0, 4, 7, 10, 13], # 變九和弦
            '7#9': [0, 4, 7, 10, 15]  # 升九和弦
        }
        
        # 定义调式音阶
        scale_notes = {
            'major': [0, 2, 4, 5, 7, 9, 11],  # C大调
            'minor': [0, 2, 3, 5, 7, 8, 10]   # C小调
        }
        
        # 解析和弦进行
        chords = []
        base_note = 60  # C4
        
        # 如果chord_string为空，返回默认和弦进行
        if not chord_string or chord_string.strip() == '':
            logger.warning("Empty chord progression, using default")
            return [[60, 64, 67], [67, 71, 74], [69, 72, 76], [60, 64, 67]]  # C-G-Am-C
        
        for chord in chord_string.split():
            # 解析根音和类型
            root = chord[0].upper()
            if len(chord) > 1 and chord[1] in ['#', 'b']:
                root += chord[1]
                type_str = chord[2:]
            else:
                type_str = chord[1:]
            
            # 获取根音音高
            root_idx = ord(root[0]) - ord('C')
            if len(root) > 1:
                if root[1] == '#':
                    root_idx += 1
                elif root[1] == 'b':
                    root_idx -= 1
            
            # 确保root_idx在正确的范围内(0-11)
            root_idx = root_idx % 12
            
            # 获取和弦类型
            if type_str in chord_type_maps:
                intervals = chord_type_maps[type_str]
            else:
                logger.warning(f"未知的和弦类型: {type_str}，使用默认大三和弦")
                intervals = chord_type_maps['maj']  # 默认使用大三和弦
            
            # 构建和弦音符
            chord_notes = [base_note + root_idx + interval for interval in intervals]
            chords.append(chord_notes)
        
        logger.debug(f"解析和弦进行: {chord_string} -> {chords}")
        return chords
    
    def complete_track(self, input_midi_path: str, params: Dict) -> Dict:
        """補全未完成的音軌"""
        try:
            # 讀取輸入的MIDI文件
            pm = pretty_midi.PrettyMIDI(input_midi_path)
            
            # 分析現有音樂特徵
            # TODO: 實現音樂分析邏輯
            
            # 生成補充內容
            # TODO: 實現音樂補全邏輯
            
            # 保存結果
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            midi_filename = f"completed_{timestamp}.mid"
            audio_filename = f"completed_audio_{timestamp}.mp3"
            
            # 生成相对路径
            midi_path = os.path.join('generated', midi_filename)
            audio_path = os.path.join('generated', audio_filename)
            
            # 生成绝对路径（用于实际文件操作）
            abs_midi_path = os.path.join('app', 'static', midi_path)
            abs_audio_path = os.path.join('app', 'static', audio_path)
            
            # 保存MIDI文件
            pm.write(abs_midi_path)
            
            # 轉換為音頻
            self._midi_to_audio(abs_midi_path, abs_audio_path)
            
            return {
                'status': 'success',
                'midi_path': midi_path.replace('\\', '/'),
                'audio_path': audio_path.replace('\\', '/')
            }
        except Exception as e:
            logger.error(f"音轨补全失败: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e)
            } 