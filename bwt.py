#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Преобразование Барроуза-Уиллера (BWT)
"""

from typing import Tuple, List
import sys


# ============================================================
# 1. DIRECT BWT - WITH MATRIX CONSTRUCTION
# ============================================================

class BWT:
    """Преобразование Барроуза-Уиллера"""
    
    @staticmethod
    def forward_matrix(data: bytes) -> Tuple[bytes, int]:
        """
        Прямое BWT с построением матрицы
        
        Алгоритм:
        1. Создаем циклические сдвиги строки
        2. Сортируем сдвиги лексикографически
        3. Выводим последний столбец
        4. Запоминаем первоначальную позицию оригинальной строки
        
        Returns:
            (преобразованное_значение, первоначальный_индекс)
        """
        if not data:
            return b'', 0
        
        n = len(data)
        
        # Создаем все циклические сдвиги
        rotations = []
        for i in range(n):
            rotation = data[i:] + data[:i]
            rotations.append((rotation, i))
        
        # Сортируем по сдвигам
        rotations.sort(key=lambda x: x[0])
        
        # Берем последний столбец и запоминаем позицию оригинальной строки
        bwt_result = b''.join(r[0][-1:] for r in rotations)
        
        # Находим позицию, где находится оригинальная строка (сдвиг на 0)
        original_index = 0
        for i, (rotation, shift_index) in enumerate(rotations):
            if shift_index == 0:
                original_index = i
                break
        
        return bwt_result, original_index
    
    @staticmethod
    def inverse_matrix(bwt_data: bytes, original_index: int) -> bytes:
        """
        Обратное BWT с построением матрицы  
        
        Алгоритм:
        1. Создаем пары (i, bwt_data[i])
        2. На каждом шаге сортируем пары по (bwt_data[i], i)
        3. Это дает нам соответствия между позициями в последнем и первом столбцах
        4. Следуем цепочке от original_index
        """
        if not bwt_data:
            return b''
        
        n = len(bwt_data)
        
        # Создаем таблицу счета для каждого байта
        counts = {}
        for byte in bwt_data:
            counts[byte] = counts.get(byte, 0) + 1
        
        # Вычисляем кумулятивные суммы (позиции в первом столбце)
        positions = {}
        pos = 0
        for byte_val in sorted(counts.keys()):
            positions[byte_val] = pos
            pos += counts[byte_val]
        
        # Строим таблицу соответствия: из позиции в последнем столбце 
        # в позицию в первом столбце
        next_idx = [0] * n
        count = {}
        
        for i in range(n):
            byte_val = bwt_data[i]
            if byte_val not in count:
                count[byte_val] = 0
            
            # j - позиция этого байта в первом столбце
            j = positions[byte_val] + count[byte_val]
            next_idx[j] = i
            count[byte_val] += 1
        
        # Следуем по цепочке
        result = bytearray()
        idx = original_index
        
        for _ in range(n):
            result.append(bwt_data[next_idx[idx]])
            idx = next_idx[idx]
        
        return bytes(result)
    
    @staticmethod
    def inverse_permutation(bwt_data: bytes, original_index: int) -> bytes:
        """
        Обратное BWT с использованием порождаемой перестановки
        
        Алгоритм:
        1. Сортируем BWT данные, создавая таблицу счета
        2. Для каждого уникального символа в BWT:
           - Используем счетную сортировку
           - Строим функцию преобразования next_index
        3. Начиная с original_index, следуем по цепочке преобразований
        """
        if not bwt_data:
            return b''
        
        n = len(bwt_data)
        
        # Создаем таблицу счета
        counts = {}  # symbol -> count
        for byte in bwt_data:
            counts[byte] = counts.get(byte, 0) + 1
        
        # Вычисляем позиции символов в первом столбце
        first_column_positions = {}
        pos = 0
        for byte in sorted(counts.keys()):
            first_column_positions[byte] = pos
            pos += counts[byte]
        
        # Построение функции преобразования (перестановки)
        # next[i] = j означает: если мы в позиции i в последнем столбце,
        # то в первом столбце это перейдет в позицию j
        
        next_index = [0] * n
        count = {}  # Текущий счетчик для каждого символа
        
        for i in range(n):
            byte = bwt_data[i]
            if byte not in count:
                count[byte] = 0
            
            # Позиция этого символа в первом столбце
            j = first_column_positions[byte] + count[byte]
            next_index[j] = i
            count[byte] += 1
        
        # Следуем по цепочке преобразований
        result = bytearray()
        idx = original_index
        
        for _ in range(n):
            result.append(bwt_data[next_index[idx]])
            idx = next_index[idx]
        
        return bytes(result)


# ============================================================
# 2. BLOCK-BASED BWT FOR LARGE FILES
# ============================================================

class BlockBWT:
    """Блочная обработка BWT для больших файлов"""
    
    def __init__(self, block_size: int = 900000):
        """
        Args:
            block_size: Размер блока в байтах (по умолчанию 900KB как в bzip2)
        """
        self.block_size = block_size
    
    def forward(self, data: bytes) -> Tuple[List[bytes], List[int]]:
        """
        Прямое BWT с блочной обработкой
        
        Returns:
            (список_блоков_BWT, список_индексов)
        """
        blocks = []
        indices = []
        
        # Разбиваем на блоки
        for i in range(0, len(data), self.block_size):
            block = data[i:i+self.block_size]
            
            bwt_block, idx = BWT.forward_matrix(block)
            blocks.append(bwt_block)
            indices.append(idx)
        
        return blocks, indices
    
    def inverse(self, blocks: List[bytes], indices: List[int]) -> bytes:
        """
        Обратное BWT с блочной обработкой
        """
        result = bytearray()
        
        for bwt_block, idx in zip(blocks, indices):
            original_block = BWT.inverse_permutation(bwt_block, idx)
            result.extend(original_block)
        
        return bytes(result)


# ============================================================
# 3. АНАЛИЗ СЛОЖНОСТИ
# ============================================================

def analyze_complexity():
    """Анализ пространственной и временной сложности"""
    print("\n" + "="*70)
    print("АНАЛИЗ СЛОЖНОСТИ BWT")
    print("="*70)
    
    print("""
1. FORWARD BWT (matrix):
   Time: O(n * n log n)
   - Create n rotations: O(n)
   - Sort rotations: O(n log n) * O(n) comparisons = O(n^2 log n)
   
   Space: O(n^2)
   - Matrix of n rotations by n bytes = n^2 bytes
   
   PROBLEM: For 10 MB file = 10^7 bytes need 10^14 bytes = 100 TB!

   SOLUTION: Use blocks (like bzip2)
   - Block size: 900 KB
   - Memory per block: 900K^2 approx 810 GB (still too much!)
   
   BETTER: Use suffix arrays or other algorithms

2. INVERSE BWT (matrix):
   Time: O(n^2)
   - On each of n iterations join columns: O(n) ops
   - Sort on each iteration: O(n log n)
   - Total: O(n * n log n) = O(n^2 log n)
   
   Space: O(n^2)

3. INVERSE BWT (permutation):
   Time: O(n)
   - Counting sort of BWT: O(n)
   - Build transform function next_index: O(n)
   - Follow chain n times: O(n)
   - Total: O(n)
   
   Space: O(n)
   - Array next_index: O(n)
   - Result: O(n)

4. BLOCK BWT:
   For n blocks of size b:
   Time: O(n * b^2 log b)
   Space: O(b^2)
   
   Example: 10 MB file, block 900 KB, blocks approx 11
   - Memory per block: 900K * 900K approx 81 GB (too much!)
   - Need suffix code calculation of rotations
    """)


# ============================================================
# 4. ТЕСТИРОВАНИЕ
# ============================================================

def test_bwt_basic():
    """Базовое тестирование BWT"""
    print("\n" + "="*70)
    print("ТЕСТ 1: БАЗОВОЕ BWT")
    print("="*70)
    
    test_data = bytes.fromhex('62616e616e61')  # "banana"
    print(f"\nИсходные данные: {test_data} ({test_data.decode()})")
    
    # Прямое преобразование
    bwt_result, idx = BWT.forward_matrix(test_data)
    print(f"BWT результат: {bwt_result}")
    print(f"Индекс: {idx}")
    
    # Обратное преобразование (матрица)
    recovered1 = BWT.inverse_matrix(bwt_result, idx)
    print(f"Восстановлено (матрица): {recovered1}")
    print(f"Проверка (матрица): {'OK' if test_data == recovered1 else 'FAIL'}")
    
    # Обратное преобразование (перестановка)
    recovered2 = BWT.inverse_permutation(bwt_result, idx)
    print(f"Восстановлено (перестановка): {recovered2}")
    print(f"Проверка (перестановка): {'OK' if test_data == recovered2 else 'FAIL'}")


def test_bwt_properties():
    """Тестирование свойств BWT"""
    print("\n" + "="*70)
    print("ТЕСТ 2: СВОЙСТВА BWT")
    print("="*70)
    
    text = "mississippi"
    data = text.encode()
    
    print(f"\nИсходный текст: {text}")
    
    bwt_result, idx = BWT.forward_matrix(data)
    print(f"BWT результат: {bwt_result.decode()}")
    print(f"Индекс: {idx}")
    
    # Проверяем, что количество каждого символа сохраняется
    sample_byte = b'm'[0]
    count_original = data.count(sample_byte)
    count_bwt = bwt_result.count(sample_byte)
    print(f"\nКоличество '{chr(sample_byte)}' в исходном: {count_original}")
    print(f"Количество '{chr(sample_byte)}' в BWT: {count_bwt}")
    print(f"Проверка: {'OK' if count_original == count_bwt else 'FAIL'}")
    
    # Проверяем, что буквы группируются
    print(f"\nВизуально видно, что буквы группируются вместе")


def test_block_bwt():
    """Тестирование блочного BWT"""
    print("\n" + "="*70)
    print("ТЕСТ 3: БЛОЧНОЕ BWT")
    print("="*70)
    
    # Генерируем тестовые данные
    data = b"abc" * 100  # 300 байт
    print(f"\nИсходные данные: {len(data)} байт")
    
    block_bwt = BlockBWT(block_size=100)
    
    blocks, indices = block_bwt.forward(data)
    print(f"Количество блоков: {len(blocks)}")
    print(f"Индексы: {indices}")
    
    recovered = block_bwt.inverse(blocks, indices)
    print(f"Восстановлено: {len(recovered)} байт")
    print(f"Проверка: {'OK' if data == recovered else 'FAIL'}")


def main():
    print("\n" + "="*70)
    print("ПРЕОБРАЗОВАНИЕ БАРРОУЗА-УИЛЛЕРА (BWT)")
    print("="*70)
    
    test_bwt_basic()
    test_bwt_properties()
    test_block_bwt()
    analyze_complexity()
    
    print("\n" + "="*70)
    print("ГОТОВО!")
    print("="*70)


if __name__ == "__main__":
    main()
