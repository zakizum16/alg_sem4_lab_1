"""
Базовые классы и утилиты для всех компрессоров
"""
import time
import math
from abc import ABC, abstractmethod
from typing import Dict
from collections import Counter


def calculate_entropy(data: bytes, Ms: int = 1) -> float:
    """Вычисляет энтропию данных"""
    if len(data) < Ms:
        return 0.0
    symbols = []
    for i in range(0, len(data) - Ms + 1, Ms):
        symbol = data[i:i+Ms]
        symbols.append(symbol)
    total = len(symbols)
    freq = Counter(symbols)
    entropy = 0.0
    for count in freq.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


class Compressor(ABC):
    """Базовый класс для всех компрессоров"""
    
    def __init__(self, name: str):
        self.name = name
        self.original_size = 0
        self.compressed_size = 0
        self.encode_time = 0.0
        self.decode_time = 0.0

    @abstractmethod
    def compress(self, data: bytes) -> bytes:
        """Сжать данные"""
        pass

    @abstractmethod
    def decompress(self, data: bytes) -> bytes:
        """Распаковать данные"""
        pass

    def get_ratio(self) -> float:
        """Получить коэффициент сжатия"""
        if self.compressed_size == 0:
            return 0.0
        return self.original_size / self.compressed_size

    def get_stats(self) -> Dict:
        """Получить статистику сжатия"""
        return {
            'name': self.name,
            'original': self.original_size,
            'compressed': self.compressed_size,
            'ratio': self.get_ratio(),
            'encode_time': self.encode_time,
            'decode_time': self.decode_time
        }

    def __repr__(self) -> str:
        return f"{self.name}: {self.original_size} -> {self.compressed_size} ({self.get_ratio():.2f}x)"
