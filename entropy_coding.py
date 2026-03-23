#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Энтропийное кодирование: Энтропия, MTF, Хаффман, Арифметическое кодирование
"""

import math
from collections import defaultdict, Counter
import struct
import heapq
from typing import Dict, List, Tuple, Optional


# ============================================================
# 1. РАСЧЕТ ЭНТРОПИИ
# ============================================================

def calculate_entropy(data: bytes, Ms: int = 1) -> float:
    """
    Расчет энтропии сообщения на основе длины кода символа.
    
    Args:
        data: Байтовая строка
        Ms: Длина кода символа в байтах (1-4)
    
    Returns:
        Значение энтропии H (бит на символ)
    
    Формула: H = -Σ p_i * log2(p_i)
    """
    if len(data) < Ms:
        return 0.0
    
    # Разбиваем данные на символы длины Ms
    symbols = []
    for i in range(0, len(data) - Ms + 1, Ms):
        symbol = data[i:i+Ms]
        symbols.append(symbol)
    
    # Считаем частоты
    total = len(symbols)
    freq = Counter(symbols)
    
    # Вычисляем энтропию
    entropy = 0.0
    for count in freq.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    
    return entropy


def analyze_entropy_vs_ms(text: str, max_ms: int = 4) -> Dict[int, float]:
    """
    Исследует зависимость энтропии от длины кода символа Ms
    """
    # Фильтруем символы с юникодом < 128 (ASCII)
    filtered_text = ''.join(c for c in text if ord(c) < 128)
    data = filtered_text.encode('ascii')
    
    results = {}
    for ms in range(1, max_ms + 1):
        if len(data) >= ms:
            entropy = calculate_entropy(data, Ms=ms)
            results[ms] = entropy
    
    return results


# ============================================================
# 2. MOVE-TO-FRONT (MTF) TRANSFORM
# ============================================================

class MTFTransform:
    """Move-To-Front трансформация"""
    
    @staticmethod
    def encode(data: bytes) -> bytes:
        """
        Прямое преобразование MTF
        
        Алгоритм:
        1. Инициализируем алфавит [0, 1, 2, ..., 255]
        2. Для каждого байта:
           - Находим его позицию в алфавите
           - Выводим позицию
           - Перемещаем байт в начало алфавита
        """
        # Инициализируем алфавит
        alphabet = list(range(256))
        result = bytearray()
        
        for byte in data:
            # Находим позицию байта в алфавите
            index = alphabet.index(byte)
            result.append(index)
            
            # Перемещаем в начало
            alphabet.pop(index)
            alphabet.insert(0, byte)
        
        return bytes(result)
    
    @staticmethod
    def decode(data: bytes) -> bytes:
        """
        Обратное преобразование MTF
        """
        alphabet = list(range(256))
        result = bytearray()
        
        for index in data:
            # Получаем символ с позиции index
            byte = alphabet[index]
            result.append(byte)
            
            # Перемещаем в начало
            alphabet.pop(index)
            alphabet.insert(0, byte)
        
        return bytes(result)
    
    @staticmethod
    def encode_utf8(text: str) -> List[int]:
        """
        MTF для UTF-8 текста (посимвольно, на уровне кодовых точек)
        """
        # Получаем все уникальные символы (кодовые точки)
        unique_chars = sorted(set(text))
        alphabet = unique_chars.copy()
        
        result = []
        for char in text:
            index = alphabet.index(char)
            result.append(index)
            
            # Перемещаем в начало
            alphabet.remove(char)
            alphabet.insert(0, char)
        
        return result
    
    @staticmethod
    def decode_utf8(data: List[int], alphabet: List[str]) -> str:
        """
        Обратное MTF для UTF-8
        """
        alph = alphabet.copy()
        result = []
        
        for index in data:
            char = alph[index]
            result.append(char)
            
            alph.remove(char)
            alph.insert(0, char)
        
        return ''.join(result)


# ============================================================
# 3. ХАФФМАН КОДИРОВАНИЕ
# ============================================================

class HuffmanNode:
    def __init__(self, symbol=None, freq=0, left=None, right=None):
        self.symbol = symbol
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        return self.freq < other.freq


class HuffmanCoding:
    """Кодирование по Хаффману"""
    
    @staticmethod
    def build_tree(frequencies: Dict[int, int]) -> HuffmanNode:
        """Построение дерева Хаффмана"""
        if not frequencies:
            return None
        
        # Создаем очередь приоритета (heap)
        heap = []
        for symbol, freq in frequencies.items():
            node = HuffmanNode(symbol=symbol, freq=freq)
            heapq.heappush(heap, node)
        
        # Строим дерево
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            
            parent = HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
            heapq.heappush(heap, parent)
        
        return heap[0]
    
    @staticmethod
    def build_codes(node: HuffmanNode, code: str = '', codes: Dict[int, str] = None) -> Dict[int, str]:
        """Построение таблицы кодов из дерева"""
        if codes is None:
            codes = {}
        
        if node is None:
            return codes
        
        if node.symbol is not None:  # Листовой узел
            codes[node.symbol] = code if code else '0'
            return codes
        
        HuffmanCoding.build_codes(node.left, code + '0', codes)
        HuffmanCoding.build_codes(node.right, code + '1', codes)
        
        return codes
    
    @staticmethod
    def encode(data: bytes) -> Tuple[str, Dict[int, str], Dict[int, int]]:
        """
        Кодирование данных по Хаффману
        
        Returns:
            (битовая_строка, таблица_кодов, частоты)
        """
        # Считаем частоты
        frequencies = Counter(data)
        
        # Строим дерево
        tree = HuffmanCoding.build_tree(dict(frequencies))
        
        # Построение кодов
        codes = HuffmanCoding.build_codes(tree)
        
        # Кодируем данные
        encoded_bits = ''
        for byte in data:
            encoded_bits += codes[byte]
        
        return encoded_bits, codes, dict(frequencies)
    
    @staticmethod
    def decode(encoded_bits: str, codes: Dict[int, str]) -> bytes:
        """
        Декодирование данных по Хаффману
        """
        # Создаем обратную таблицу: код -> символ
        reverse_codes = {v: k for k, v in codes.items()}
        
        result = bytearray()
        current_code = ''
        
        for bit in encoded_bits:
            current_code += bit
            
            if current_code in reverse_codes:
                result.append(reverse_codes[current_code])
                current_code = ''
        
        return bytes(result)
    
    @staticmethod
    def compute_entropy(frequencies: Dict[int, int]) -> float:
        """
        Вычисляет теоретическую энтропию кодирования Хаффмана
        """
        total = sum(frequencies.values())
        codes = {}
        
        # Строим дерево и коды
        tree = HuffmanCoding.build_tree(frequencies)
        codes = HuffmanCoding.build_codes(tree)
        
        # Средняя длина кода
        avg_bits = sum(len(codes[sym]) * freq / total 
                       for sym, freq in frequencies.items())
        
        return avg_bits


# ============================================================
# 4. АРИФМЕТИЧЕСКОЕ КОДИРОВАНИЕ
# ============================================================

class ArithmeticCoding:
    """Арифметическое кодирование"""
    
    @staticmethod
    def encode(data: bytes, frequencies: Dict[int, int] = None) -> float:
        """
        Арифметическое кодирование
        
        Returns:
            Число в диапазоне [0, 1) в формате double
        """
        if frequencies is None:
            frequencies = Counter(data)
        
        total = sum(frequencies.values())
        
        # Вычисляем интервалы для каждого символа
        intervals = {}
        cumsum = 0
        for symbol in sorted(frequencies.keys()):
            freq = frequencies[symbol]
            intervals[symbol] = (cumsum / total, (cumsum + freq) / total)
            cumsum += freq
        
        # Инициализируем границы
        left = 0.0
        right = 1.0
        
        # Обрабатываем каждый символ
        for byte in data:
            l, r = intervals[byte]
            
            # Сужаем интервал
            new_left = left + (right - left) * l
            new_right = left + (right - left) * r
            
            left = new_left
            right = new_right
            
            # Проверяем, не совпадают ли границы (точность double)
            if abs(right - left) < 1e-16:
                print(f"[PRECISION] Границы совпали после {data.index(byte)} символов")
                print(f"  Осталось символов: {len(data) - data.index(byte) - 1}")
                break
        
        return (left + right) / 2
    
    @staticmethod
    def decode(encoded_value: float, frequencies: Dict[int, int], length: int) -> bytes:
        """
        Декодирование арифметического кода
        """
        total = sum(frequencies.values())
        
        # Вычисляем интервалы
        intervals = {}
        cumsum = 0
        for symbol in sorted(frequencies.keys()):
            freq = frequencies[symbol]
            intervals[symbol] = (cumsum / total, (cumsum + freq) / total)
            cumsum += freq
        
        # Инициализируем границы
        left = 0.0
        right = 1.0
        result = bytearray()
        
        for _ in range(length):
            # Находим символ, чей интервал содержит encoded_value
            for symbol in sorted(frequencies.keys()):
                l, r = intervals[symbol]
                
                sym_left = left + (right - left) * l
                sym_right = left + (right - left) * r
                
                if sym_left <= encoded_value < sym_right:
                    result.append(symbol)
                    left = sym_left
                    right = sym_right
                    break
        
        return bytes(result)


# ============================================================
# 5. ТЕСТИРОВАНИЕ
# ============================================================

def test_entropy():
    """Тестирование расчета энтропии"""
    print("\n" + "="*70)
    print("ТЕСТ 1: РАСЧЕТ ЭНТРОПИИ")
    print("="*70)
    
    # Простые тестовые данные
    test_cases = [
        (b'\x00\x00\x00\x00', "Один символ (0x00)"),
        (b'\x00\x01\x02\x03', "Все разные"),
        (b'aaaaaabbbbcc', "Разные частоты"),
    ]
    
    for data, desc in test_cases:
        entropy = calculate_entropy(data, Ms=1)
        print(f"\n{desc}:")
        print(f"  Данные: {data[:20]}")
        print(f"  Энтропия: {entropy:.4f} бит/символ")


def test_mtf():
    """Тестирование MTF"""
    print("\n" + "="*70)
    print("ТЕСТ 2: MTF ТРАНСФОРМАЦИЯ")
    print("="*70)
    
    test_data = b'banana'
    print(f"\nИсходные данные: {test_data}")
    
    encoded = MTFTransform.encode(test_data)
    print(f"MTF кодированы: {list(encoded)}")
    
    decoded = MTFTransform.decode(encoded)
    print(f"MTF декодированы: {decoded}")
    print(f"Проверка: {'OK' if test_data == decoded else 'FAIL'}")
    
    # Анализируем энтропию до и после MTF
    entropy_before = calculate_entropy(test_data, Ms=1)
    entropy_after = calculate_entropy(encoded, Ms=1)
    print(f"\nЭнтропия до MTF: {entropy_before:.4f}")
    print(f"Энтропия после MTF: {entropy_after:.4f}")
    print(f"Изменение энтропии: {entropy_after - entropy_before:+.4f}")


def test_huffman():
    """Тестирование Хаффмана"""
    print("\n" + "="*70)
    print("ТЕСТ 3: КОДИРОВАНИЕ ХАФФМАНА")
    print("="*70)
    
    test_data = b'hello world'
    print(f"\nИсходные данные: {test_data}")
    
    encoded_bits, codes, frequencies = HuffmanCoding.encode(test_data)
    print(f"Кодовая таблица: {codes}")
    print(f"Закодировано бит: {len(encoded_bits)}")
    print(f"Исходный размер: {len(test_data) * 8} бит")
    print(f"Коэффициент: {len(test_data) * 8 / len(encoded_bits):.2f}x")
    
    decoded = HuffmanCoding.decode(encoded_bits, codes)
    print(f"Декодировано: {decoded}")
    print(f"Проверка: {'OK' if test_data == decoded else 'FAIL'}")


def test_arithmetic():
    """Тестирование арифметического кодирования"""
    print("\n" + "="*70)
    print("ТЕСТ 4: АРИФМЕТИЧЕСКОЕ КОДИРОВАНИЕ")
    print("="*70)
    
    test_data = b'aaabbc'
    frequencies = Counter(test_data)
    
    print(f"\nИсходные данные: {test_data}")
    print(f"Частоты: {dict(frequencies)}")
    
    encoded = ArithmeticCoding.encode(test_data, dict(frequencies))
    print(f"Закодированное значение: {encoded:.15f}")
    
    decoded = ArithmeticCoding.decode(encoded, dict(frequencies), len(test_data))
    print(f"Декодировано: {decoded}")
    print(f"Проверка: {'OK' if test_data == decoded else 'FAIL'}")


def main():
    print("\n" + "="*70)
    print("ЭНТРОПИЙНОЕ КОДИРОВАНИЕ")
    print("="*70)
    
    test_entropy()
    test_mtf()
    test_huffman()
    test_arithmetic()
    
    print("\n" + "="*70)
    print("ГОТОВО!")
    print("="*70)


if __name__ == "__main__":
    main()
