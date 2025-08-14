import os
from pydub import AudioSegment
from typing import Optional

class AudioConverter:
    """音頻格式轉換器"""
    
    @staticmethod
    def convert_to_mp3(input_path: str, output_path: Optional[str] = None) -> str:
        """將音頻文件轉換為MP3格式"""
        if output_path is None:
            output_path = os.path.splitext(input_path)[0] + '.mp3'
            
        audio = AudioSegment.from_file(input_path)
        audio.export(output_path, format='mp3')
        return output_path
    
    @staticmethod
    def convert_to_wav(input_path: str, output_path: Optional[str] = None) -> str:
        """將音頻文件轉換為WAV格式"""
        if output_path is None:
            output_path = os.path.splitext(input_path)[0] + '.wav'
            
        audio = AudioSegment.from_file(input_path)
        audio.export(output_path, format='wav')
        return output_path
    
    @staticmethod
    def adjust_volume(input_path: str, volume_change: float) -> str:
        """調整音頻音量"""
        audio = AudioSegment.from_file(input_path)
        adjusted_audio = audio + volume_change
        output_path = f"adjusted_{os.path.basename(input_path)}"
        adjusted_audio.export(output_path, format=os.path.splitext(input_path)[1][1:])
        return output_path
    
    @staticmethod
    def trim_audio(input_path: str, start_ms: int, end_ms: int) -> str:
        """裁剪音頻"""
        audio = AudioSegment.from_file(input_path)
        trimmed_audio = audio[start_ms:end_ms]
        output_path = f"trimmed_{os.path.basename(input_path)}"
        trimmed_audio.export(output_path, format=os.path.splitext(input_path)[1][1:])
        return output_path 