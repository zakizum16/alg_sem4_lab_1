#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Задание 4: Эффективное BWT на основе суффиксного массива и канонические коды Хаффмана
"""

import struct
import heapq
from typing import Dict, List, Tuple, Optional
from collections import Counter
from suffix_array_lz import SuffixArray


# =============================================================================
# 1. ЭФФЕКТИВНОЕ BWT НА ОСНОВЕ СУФФИКСНОГО МАССИВА
# =============================================================================

class EfficientBWT:
    """
    Эффективное преобразование Барроуза-Уиллера через суффиксный массив.
    
    Временная сложность: O(n log n) для построения SA
    Пространственная сложность: O(n)
    """
    
    @staticmethod
    def forward(data: bytes) -> Tuple[bytes, int]:
        """
        Прямое BWT через суффиксный массив.
        
        Алгоритм:
        1. Строим суффиксный массив O(n log n)
        2. Преобразуем SA в BWT O(n)
        
        Args:
            data: Входные данные
        
        Returns:
            (BWT строка, индекс исходной строки)
        """
        if not data:
            return b'', 0
        
        # Шаг 1: Строим суффиксный массив
        suffix_array = SuffixArray.build_suffix_array(data)
        
        # Шаг 2: Преобразуем в BWT
        bwt, original_index = SuffixArray.suffix_array_to_bwt(suffix_array, data)
        
        return bwt, original_index
    
    @staticmethod
    def inverse(bwt: bytes, original_index: int) -> bytes:
        """
        Обратное BWT.
        
        Алгоритм:
        1. Строим матрицу счётчиков (LF mapping)
        2. Восстанавливаем оригинальную строку через first column
        
        Args:
            bwt: BWT строка
            original_index: Индекс исходной строки в матрице
        
        Returns:
            Оригинальная строка
        """
        if not bwt:
            return b''
        
        n = len(bwt)
        
        # Строим первый столбец (отсортированный BWT)
        first_col = sorted(bwt)
        
        # Строим LF mapping (Last-to-First)
        # Для каждого символа в последнем столбце найти его позицию в первом
        count = Counter(bwt)
        lf = [0] * n
        
        # Вычисляем сумму символов до каждого в первом столбце
        cumsum = 0
        pos_in_first = {}
        for i, ch in enumerate(first_col):
            if ch not in pos_in_first:
                pos_in_first[ch] = []
            pos_in_first[ch].append(i)
        
        # Строим LF mapping
        ch_count = Counter()
        for i, ch in enumerate(bwt):
            pos_in_first[ch]
            idx_in_positions = ch_count[ch]
            lf[i] = pos_in_first[ch][idx_in_positions]
            ch_count[ch] += 1
        
        # Восстанавливаем исходную строку
        result = bytearray()
        idx = original_index
        for _ in range(n):
            result.append(bwt[idx])
            idx = lf[idx]
        
        return bytes(reversed(result))


# =============================================================================
# 2. КАНОНИЧЕСКИЕ КОДЫ ХАФФМАНА
# =============================================================================

class CanonicalHuffman:
    """Канонические коды Хаффмана (оптимизированные)"""
    
    @staticmethod
    def _build_huffman_tree(frequencies: Dict[int, int]) -> Dict[int, Tuple[int, int]]:
        """
        Построение дерева Хаффмана и получение длин кодов.
        
        Returns:
            {symbol: (code_length, code_value)}
        """
        if not frequencies:
            return {}
        
        if len(frequencies) == 1:
            # Специальный случай: один символ
            symbol = list(frequencies.keys())[0]
            return {symbol: (1, 0)}
        
        # Строим дерево Хаффмана
        heap = [(freq, i, symbol) for i, (symbol, freq) in enumerate(frequencies.items())]
        heapq.heapify(heap)
        
        counter = len(heap)
        while len(heap) > 1:
            freq1, _, symbol1 = heapq.heappop(heap)
            freq2, _, symbol2 = heapq.heappop(heap)
            
            merged_freq = freq1 + freq2
            heapq.heappush(heap, (merged_freq, counter, (symbol1, symbol2)))
            counter += 1
        
        # Получаем длины кодов
        code_lengths = {}
        
        def get_depths(node, depth=0):
            if isinstance(node, tuple) and len(node) == 2:
                get_depths(node[0], depth + 1)
                get_depths(node[1], depth + 1)
            else:
                code_lengths[node] = depth
        
        _, _, root = heap[0]
        get_depths(root)
        
        return code_lengths
    
    @staticmethod
    def build_canonical_codes(code_lengths: Dict[int, int]) -> Dict[int, Tuple[int, int]]:
        """
        Построение канонических кодов из длин.
        
        Алгоритм:
        1. Сортируем символы по длине кода
        2. Назначаем коды в порядке возрастания
        
        Args:
            code_lengths: {symbol: code_length}
        
        Returns:
            {symbol: (code_length, code_value)}
        """
        if not code_lengths:
            return {}
        
        # Сортируем по длине, затем по символу
        sorted_symbols = sorted(code_lengths.items(), key=lambda x: (x[1], x[0]))
        
        canonical_codes = {}
        code = 0
        prev_length = 0
        
        for symbol, length in sorted_symbols:
            # Сдвигаем код если длина увеличилась
            code <<= (length - prev_length)
            canonical_codes[symbol] = (length, code)
            code += 1
            prev_length = length
        
        return canonical_codes
    
    @staticmethod
    def encode(data: bytes) -> Tuple[bytes, bytes, Dict[int, int]]:
        """
        Кодирование с каноническими кодами.
        
        Args:
            data: Входные данные
        
        Returns:
            (кодированные_данные, таблица_длин, словарь_таблицы)
        """
        if not data:
            return b'', b'', {}
        
        # Считаем частоты
        freq = Counter(data)
        
        # Получаем длины кодов
        code_lengths = CanonicalHuffman._build_huffman_tree(freq)
        
        # Строим канонические коды
        canonical = CanonicalHuffman.build_canonical_codes(code_lengths)
        
        # Кодируем данные
        bit_string = ''
        for byte in data:
            length, code = canonical[byte]
            bit_string += format(code, f'0{length}b')
        
        # Преобразуем в байты
        # Добавляем паддинг до кратности 8
        padding = (8 - len(bit_string) % 8) % 8
        bit_string += '0' * padding
        
        encoded = bytearray()
        for i in range(0, len(bit_string), 8):
            encoded.append(int(bit_string[i:i+8], 2))
        
        # Сохраняем таблицу длин в компактном формате
        table = bytearray()
        table.append(padding)  # количество паддинг бит
        table.extend(struct.pack('>H', len(code_lengths)))  # количество символов
        
        for symbol in sorted(code_lengths.keys()):
            length = code_lengths[symbol]
            table.extend(struct.pack('>BHH', length, symbol, 0))  # length, symbol, reserved
        
        return bytes(encoded), bytes(table), code_lengths
    
    @staticmethod
    def decode(data: bytes, table: bytes) -> bytes:
        """
        Декодирование с каноническими кодами.
        
        Args:
            data: Кодированные данные
            table: Таблица длин кодов
        
        Returns:
            Декодированные данные
        """
        if not data or not table:
            return b''
        
        # Читаем таблицу
        pos = 0
        padding = table[pos]
        pos += 1
        num_symbols = struct.unpack('>H', table[pos:pos+2])[0]
        pos += 2
        
        code_lengths = {}
        for _ in range(num_symbols):
            length, symbol, _ = struct.unpack('>BHH', table[pos:pos+5])
            pos += 5
            code_lengths[symbol] = length
        
        # Строим канонические коды
        canonical = CanonicalHuffman.build_canonical_codes(code_lengths)
        
        # Обратная таблица: (length, code) -> symbol
        reverse_table = {}
        for symbol, (length, code) in canonical.items():
            reverse_table[(length, code)] = symbol
        
        # Преобразуем данные в битовую строку
        bit_string = ''.join(format(b, '08b') for b in data)
        
        # Убираем паддинг
        if padding > 0:
            bit_string = bit_string[:-padding]
        
        # Декодируем
        result = bytearray()
        code = 0
        code_len = 0
        
        for bit in bit_string:
            code = (code << 1) | int(bit)
            code_len += 1
            
            if (code_len, code) in reverse_table:
                result.append(reverse_table[(code_len, code)])
                code = 0
                code_len = 0
        
        return bytes(result)


# =============================================================================
# 3. ОПТИМИЗИРОВАННОЕ КОДИРОВАНИЕ ХАФФМАНА
# =============================================================================

class OptimizedHuffmanCoding:
    """Оптимизированное кодирование Хаффмана с каноническими кодами"""
    
    @staticmethod
    def encode(data: bytes) -> Tuple[bytes, bytes]:
        """
        Кодирование Хаффмана с минимизацией метаданных.
        
        Returns:
            (кодированные_данные, метаданные)
        """
        encoded, table, _ = CanonicalHuffman.encode(data)
        return encoded, table
    
    @staticmethod
    def decode(encoded: bytes, table: bytes) -> bytes:
        """Декодирование"""
        return CanonicalHuffman.decode(encoded, table)


# =============================================================================
# 4. КОМПЛЕКСНЫЙ ТЕСТ
# =============================================================================

if __name__ == '__main__':
    test_data = b'the quick brown fox jumps over the lazy dog' * 5
    
    print("="*70)
    print("ЭФФЕКТИВНОЕ BWT (через суффиксный массив)")
    print("="*70)
    
    print("\nУтверждение о сложности:")
    print("  Временная: O(n log n) - построение суффиксного массива")
    print("  Пространственная: O(n) - хранение SA и BWT")
    
    # Тест BWT
    print("\nТест BWT:")
    bwt_data, idx = EfficientBWT.forward(test_data)
    print(f"  Размер: {len(test_data)} -> {len(bwt_data)}")
    recovered = EfficientBWT.inverse(bwt_data, idx)
    print(f"  Цикл: {test_data == recovered}")
    
    print("\n" + "="*70)
    print("КАНОНИЧЕСКИЕ КОДЫ ХАФФМАНА")
    print("="*70)
    
    # Простой тест
    simple_data = b'aaabbc'
    print("\nПримеры кодов:")
    print(f"  Данные: {simple_data}")
    
    # Получаем длины
    freq = Counter(simple_data)
    code_lengths = CanonicalHuffman._build_huffman_tree(freq)
    canonical = CanonicalHuffman.build_canonical_codes(code_lengths)
    
    for symbol, (length, code) in sorted(canonical.items()):
        print(f"    '{chr(symbol)}' ({symbol}): длина={length}, код={format(code, f'0{length}b')}")
    
    # Кодирование и декодирование
    print("\nТест кодирования:")
    encoded, table, _ = CanonicalHuffman.encode(test_data)
    decoded = CanonicalHuffman.decode(encoded, table)
    print(f"  Исходные: {len(test_data)} байт")
    print(f"  Закодированные: {len(encoded)} байт (+ {len(table)} байт метаданных)")
    print(f"  Коэффициент: {len(test_data) / (len(encoded) + len(table)):.2f}x")
    print(f"  Цикл: {test_data == decoded}")
