from typing import List, Dict, Optional
import numpy as np

class ChordProcessor:
    """和弦處理器"""
    
    # 定義基本音符
    NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # 定義常見和弦類型
    CHORD_TYPES = {
        'major': [0, 4, 7],
        'minor': [0, 3, 7],
        'dim': [0, 3, 6],
        'aug': [0, 4, 8],
        'maj7': [0, 4, 7, 11],
        'min7': [0, 3, 7, 10],
        'dom7': [0, 4, 7, 10],
    }
    
    # 定義常見和弦進行
    COMMON_PROGRESSIONS = {
        'pop': ['I', 'V', 'vi', 'IV'],
        'jazz': ['ii', 'V', 'I'],
        'blues': ['I', 'IV', 'I', 'V', 'IV', 'I'],
        'classical': ['I', 'IV', 'V', 'I']
    }
    
    @classmethod
    def get_chord_notes(cls, root: str, chord_type: str = 'major') -> List[str]:
        """獲取和弦的所有音符"""
        try:
            root_idx = cls.NOTES.index(root)
            intervals = cls.CHORD_TYPES[chord_type]
            return [cls.NOTES[(root_idx + interval) % 12] for interval in intervals]
        except (ValueError, KeyError):
            return []
    
    @classmethod
    def get_progression(cls, style: str, key: str = 'C') -> List[str]:
        """根據風格獲取和弦進行"""
        if style not in cls.COMMON_PROGRESSIONS:
            return []
            
        progression = cls.COMMON_PROGRESSIONS[style]
        return cls._convert_roman_to_chords(progression, key)
    
    @classmethod
    def suggest_next_chord(cls, current_chord: str, style: str = 'pop') -> List[str]:
        """根據當前和弦建議下一個和弦"""
        # 簡單的和弦建議邏輯
        common_follows = {
            'C': ['F', 'G', 'Am'],
            'F': ['C', 'G', 'Dm'],
            'G': ['C', 'Am', 'Em'],
            'Am': ['F', 'G', 'C'],
        }
        return common_follows.get(current_chord, ['C', 'F', 'G'])
    
    @classmethod
    def _convert_roman_to_chords(cls, progression: List[str], key: str) -> List[str]:
        """將羅馬數字和弦級數轉換為實際和弦"""
        key_idx = cls.NOTES.index(key)
        major_scale = [cls.NOTES[(key_idx + i) % 12] for i in [0, 2, 4, 5, 7, 9, 11]]
        
        chord_map = {
            'I': major_scale[0],
            'ii': f"{major_scale[1]}m",
            'iii': f"{major_scale[2]}m",
            'IV': major_scale[3],
            'V': major_scale[4],
            'vi': f"{major_scale[5]}m",
            'vii': f"{major_scale[6]}dim"
        }
        
        return [chord_map.get(degree, degree) for degree in progression]
    
    @staticmethod
    def transpose_chord(chord: str, semitones: int) -> str:
        """移調和弦"""
        # TODO: 實現和弦移調邏輯
        pass
    
    @staticmethod
    def analyze_progression(chords: List[str]) -> Dict:
        """分析和弦進行"""
        # TODO: 實現和弦進行分析邏輯
        pass 