#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Задание 3: Суффиксные массивы и методы Лемпеля-Зива (LZ77, LZSS, LZ78, LZW)
"""

import struct
from typing import Tuple, List, Dict, Optional
from collections import defaultdict


# =============================================================================
# 1. СУФФИКСНЫЙ МАССИВ → BWT
# =============================================================================

class SuffixArray:
    """Работа с суффиксными массивами"""
    
    @staticmethod
    def build_suffix_array(data: bytes) -> List[int]:
        """
        Построение суффиксного массива.
        Использует встроенную сортировку - O(n log n).
        
        Args:
            data: Входные данные
        
        Returns:
            Массив индексов суффиксов в лексикографическом порядке
        """
        if not data:
            return []
        
        n = len(data)
        suffixes = [(data[i:], i) for i in range(n)]
        suffixes.sort(key=lambda x: x[0])
        return [idx for _, idx in suffixes]
    
    @staticmethod
    def suffix_array_to_bwt(suffix_array: List[int], data: bytes) -> Tuple[bytes, int]:
        """
        Преобразование суффиксного массива в последний столбец BWT.
        
        Args:
            suffix_array: Суффиксный массив
            data: Исходные данные
        
        Returns:
            (BWT строка, индекс исходной строки)
        
        Алгоритм:
        - BWT[i] = data[(suffix_array[i] - 1) % n]
        - Находим позицию, где suffix_array[i] == 0 (это исходная строка)
        """
        if not suffix_array:
            return b'', 0
        
        n = len(data)
        bwt = bytearray()
        original_index = 0
        
        for i, sa_val in enumerate(suffix_array):
            # Последний столбец BWT - это symbol перед suffix_array[i]
            prev_idx = (sa_val - 1) % n
            bwt.append(data[prev_idx])
            
            # Запоминаем позицию исходной строки
            if sa_val == 0:
                original_index = i
        
        return bytes(bwt), original_index


# =============================================================================
# 2. LZ77 - КОДИРОВАНИЕ
# =============================================================================

class LZ77:
    """Алгоритм LZ77"""
    
    @staticmethod
    def encode(data: bytes, window_size: int = 4096, lookahead_size: int = 18) -> bytes:
        """
        Кодирование LZ77.
        
        Args:
            data: Входные данные
            window_size: Размер скользящего буфера (макс. расстояние)
            lookahead_size: Размер буфера просмотра (макс. длина совпадения)
        
        Returns:
            Кодированная последовательность (offset, length, next_char)
        
        Формат: каждый токен = [2 байта offset, 1 байт length, 1 байт next_char]
        """
        if not data:
            return b''
        
        result = bytearray()
        pos = 0
        n = len(data)
        
        while pos < n:
            # Ищем самое длинное совпадение в окне перед текущей позицией
            best_offset = 0
            best_length = 0
            
            # Начало окна
            window_start = max(0, pos - window_size)
            
            # Ищем совпадение
            for i in range(window_start, pos):
                length = 0
                while (length < lookahead_size and
                       pos + length < n and
                       data[i + length] == data[pos + length]):
                    length += 1
                
                if length > best_length:
                    best_length = length
                    best_offset = pos - i
            
            # Если найдено совпадение длины >= 3, кодируем его
            if best_length >= 3:
                next_char = data[pos + best_length] if pos + best_length < n else 0
                result.extend(struct.pack('>HBB', best_offset, best_length, next_char))
                pos += best_length + 1
            else:
                # Иначе - кодируем символ как есть (offset=0, length=0)
                result.extend(struct.pack('>HBB', 0, 0, data[pos]))
                pos += 1
        
        return bytes(result)
    
    @staticmethod
    def decode(data: bytes) -> bytes:
        """
        Декодирование LZ77.
        
        Args:
            data: Кодированная последовательность
        
        Returns:
            Декодированная последовательность
        """
        result = bytearray()
        pos = 0
        
        while pos + 4 <= len(data):
            offset, length, next_char = struct.unpack('>HBB', data[pos:pos+4])
            pos += 4
            
            if length > 0:
                # Копируем из истории
                start = len(result) - offset
                for i in range(length):
                    result.append(result[start + i])
            
            # Добавляем следующий символ
            result.append(next_char)
        
        return bytes(result)


# =============================================================================
# 3. LZSS - LZ77 с флагом
# =============================================================================

class LZSS:
    """Алгоритм LZSS (оптимизированный LZ77 с флагами)"""
    
    @staticmethod
    def encode(data: bytes, window_size: int = 4096, lookahead_size: int = 18) -> bytes:
        """
        Кодирование LZSS - похоже на LZ77, но с флагом.
        
        Формат: [флаг (1 бит)] + данные
        - флаг=0: 1 байт литерал
        - флаг=1: (offset, length)
        """
        if not data:
            return b''
        
        result = bytearray()
        pos = 0
        n = len(data)
        
        while pos < n:
            best_offset = 0
            best_length = 0
            
            window_start = max(0, pos - window_size)
            
            for i in range(window_start, pos):
                length = 0
                while (length < lookahead_size and
                       pos + length < n and
                       data[i + length] == data[pos + length]):
                    length += 1
                
                if length > best_length:
                    best_length = length
                    best_offset = pos - i
            
            if best_length >= 3:
                # Флаг 1: совпадение
                result.append(1)  # флаг
                result.extend(struct.pack('>HB', best_offset, best_length))
                pos += best_length
            else:
                # Флаг 0: литерал
                result.append(0)  # флаг
                result.append(data[pos])
                pos += 1
        
        return bytes(result)
    
    @staticmethod
    def decode(data: bytes) -> bytes:
        """Декодирование LZSS"""
        result = bytearray()
        pos = 0
        
        while pos < len(data):
            flag = data[pos]
            pos += 1
            
            if flag == 1:
                # Совпадение
                if pos + 3 <= len(data):
                    offset, length = struct.unpack('>HB', data[pos:pos+3])
                    pos += 3
                    start = len(result) - offset
                    for i in range(length):
                        result.append(result[start + i])
            else:
                # Литерал
                if pos < len(data):
                    result.append(data[pos])
                    pos += 1
        
        return bytes(result)


# =============================================================================
# 4. LZ78 - КОДИРОВАНИЕ
# =============================================================================

class LZ78:
    """Алгоритм LZ78 (адаптивный словарь)"""
    
    @staticmethod
    def encode(data: bytes, max_dict_size: int = 4096) -> bytes:
        """
        Кодирование LZ78.
        
        Алгоритм:
        - Ведём словарь фраз
        - Каждый токен: [индекс_в_словаре, символ]
        - Добавляем новую фразу в словарь
        
        Args:
            data: Входные данные
            max_dict_size: Максимальный размер словаря
        
        Returns:
            Кодированная последовательность
        """
        if not data:
            return b''
        
        dictionary = {b'': 0}  # phrase -> index (пустая фраза имеет индекс 0)
        dict_index = 1  # Следующий индекс для добавления
        result = bytearray()
        n = len(data)
        pos = 0
        
        while pos < n:
            # Ищем самую длинную фразу в словаре
            phrase = b''
            matched_index = 0
            
            # Ищем совпадение
            while pos + len(phrase) < n:
                new_phrase = phrase + bytes([data[pos + len(phrase)]])
                if new_phrase in dictionary:
                    phrase = new_phrase
                    matched_index = dictionary[phrase]
                else:
                    break
            
            # Если нашли фразу, добавляем символ
            if pos + len(phrase) < n:
                next_char = data[pos + len(phrase)]
                result.extend(struct.pack('>HB', matched_index, next_char))
                
                # Добавляем в словарь
                new_phrase = phrase + bytes([next_char])
                if dict_index < max_dict_size:
                    dictionary[new_phrase] = dict_index
                    dict_index += 1
                
                pos += len(phrase) + 1
            else:
                # Конец данных
                break
        
        return bytes(result)
    
    @staticmethod
    def decode(data: bytes, max_dict_size: int = 4096) -> bytes:
        """Декодирование LZ78"""
        dictionary = {0: b''}  # index -> phrase
        dict_index = 1
        
        result = bytearray()
        pos = 0
        
        while pos + 3 <= len(data):
            index, char = struct.unpack('>HB', data[pos:pos+3])
            pos += 3
            
            # Получаем фразу из словаря
            if index in dictionary:
                phrase = dictionary[index] + bytes([char])
            else:
                # index=0 означает пустую фразу
                phrase = bytes([char])
            
            result.extend(phrase)
            
            # Добавляем в словарь для будущего использования
            if dict_index < max_dict_size:
                dictionary[dict_index] = phrase
                dict_index += 1
        
        return bytes(result)


# =============================================================================
# 5. LZW - ЛЕМПЕЛЯ-ЗИВА-ВЕЛША
# =============================================================================

class LZW:
    """Алгоритм LZW (LZ78 с расширением)"""
    
    @staticmethod
    def encode(data: bytes, max_dict_size: int = 4096) -> bytes:
        """
        Кодирование LZW.
        
        Алгоритм:
        - Инициализируем словарь символами (0-255)
        - Для каждой строки X: если X в словаре, выводим индекс
        - Если X+char не в словаре, добавляем в словарь
        
        Args:
            data: Входные данные
            max_dict_size: Максимальный размер словаря
        
        Returns:
            Кодированная последовательность (индексы в словаре)
        """
        if not data:
            return b''
        
        # Инициализируем словарь
        dict_size = 256
        dictionary = {bytes([i]): i for i in range(256)}
        
        result = bytearray()
        w = bytes([data[0]])
        
        for i in range(1, len(data)):
            c = bytes([data[i]])
            wc = w + c
            
            if wc in dictionary:
                w = wc
            else:
                # Выводим код для w
                result.extend(struct.pack('>H', dictionary[w]))
                
                # Добавляем wc в словарь
                if dict_size < max_dict_size:
                    dictionary[wc] = dict_size
                    dict_size += 1
                
                w = c
        
        # Выводим последний код
        result.extend(struct.pack('>H', dictionary[w]))
        
        return bytes(result)
    
    @staticmethod
    def decode(data: bytes, max_dict_size: int = 4096) -> bytes:
        """
        Декодирование LZW.
        
        Примечание: Словарь не нужно передавать - восстанавливается из кодов
        """
        if not data:
            return b''
        
        # Инициализируем словарь
        dict_size = 256
        dictionary = {i: bytes([i]) for i in range(256)}
        
        result = bytearray()
        pos = 0
        
        if pos + 2 <= len(data):
            k = struct.unpack('>H', data[pos:pos+2])[0]
            pos += 2
            entry = dictionary[k]
            result.extend(entry)
            w = entry
        
        while pos + 2 <= len(data):
            k = struct.unpack('>H', data[pos:pos+2])[0]
            pos += 2
            
            if k in dictionary:
                entry = dictionary[k]
            elif k == dict_size:
                entry = w + bytes([w[0]])
            else:
                entry = dictionary.get(k, b'')
            
            result.extend(entry)
            
            # Добавляем в словарь
            if dict_size < max_dict_size:
                dictionary[dict_size] = w + bytes([entry[0]])
                dict_size += 1
            
            w = entry
        
        return bytes(result)


# =============================================================================
# 6. УТИЛИТЫ ДЛЯ ФАЙЛОВ
# =============================================================================

class LZFileHandler:
    """Работа с LZ-сжатыми файлами"""
    
    @staticmethod
    def save_lz77(filename: str, data: bytes, window_size: int = 4096):
        """Сохранение LZ77 в файл с метаданными"""
        compressed = LZ77.encode(data, window_size=window_size)
        with open(filename, 'wb') as f:
            f.write(struct.pack('>I', len(data)))  # оригинальный размер
            f.write(struct.pack('>H', window_size))  # размер окна
            f.write(compressed)
    
    @staticmethod
    def load_lz77(filename: str) -> bytes:
        """Загрузка LZ77 из файла"""
        with open(filename, 'rb') as f:
            original_size = struct.unpack('>I', f.read(4))[0]
            window_size = struct.unpack('>H', f.read(2))[0]
            compressed = f.read()
        return LZ77.decode(compressed)
    
    @staticmethod
    def save_lzw(filename: str, data: bytes, max_dict_size: int = 4096):
        """Сохранение LZW в файл"""
        compressed = LZW.encode(data, max_dict_size=max_dict_size)
        with open(filename, 'wb') as f:
            f.write(struct.pack('>I', len(data)))  # оригинальный размер
            f.write(struct.pack('>H', max_dict_size))  # макс. размер словаря
            f.write(compressed)
    
    @staticmethod
    def load_lzw(filename: str) -> bytes:
        """Загрузка LZW из файла"""
        with open(filename, 'rb') as f:
            original_size = struct.unpack('>I', f.read(4))[0]
            max_dict_size = struct.unpack('>H', f.read(2))[0]
            compressed = f.read()
        return LZW.decode(compressed, max_dict_size=max_dict_size)


if __name__ == '__main__':
    # Простой тест
    test_data = b'banana' * 10
    
    print("Суффиксный массив → BWT")
    sa = SuffixArray.build_suffix_array(test_data)
    bwt, idx = SuffixArray.suffix_array_to_bwt(sa, test_data)
    print(f"  BWT: {bwt}")
    
    print("\nLZ77")
    lz77_enc = LZ77.encode(test_data)
    lz77_dec = LZ77.decode(lz77_enc)
    print(f"  Исходная: {len(test_data)} байт")
    print(f"  Сжатая: {len(lz77_enc)} байт")
    print(f"  Цикл: {test_data == lz77_dec}")
    
    print("\nLZSS")
    lzss_enc = LZSS.encode(test_data)
    lzss_dec = LZSS.decode(lzss_enc)
    print(f"  Исходная: {len(test_data)} байт")
    print(f"  Сжатая: {len(lzss_enc)} байт")
    print(f"  Цикл: {test_data == lzss_dec}")
    
    print("\nLZ78")
    lz78_enc = LZ78.encode(test_data)
    lz78_dec = LZ78.decode(lz78_enc)
    print(f"  Исходная: {len(test_data)} байт")
    print(f"  Сжатая: {len(lz78_enc)} байт")
    print(f"  Цикл: {test_data == lz78_dec}")
    
    print("\nLZW")
    lzw_enc = LZW.encode(test_data)
    lzw_dec = LZW.decode(lzw_enc)
    print(f"  Исходная: {len(test_data)} байт")
    print(f"  Сжатая: {len(lzw_enc)} байт")
    print(f"  Цикл: {test_data == lzw_dec}")
