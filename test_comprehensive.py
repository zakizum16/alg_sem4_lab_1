#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Полный тест: RLE + Entropy Coding + BWT + Compression Analysis
"""

import os
import struct
from collections import Counter
from typing import Tuple, Dict, List

from rle import RLECompressor, RLEFileHandler
from entropy_coding import (
    calculate_entropy, MTFTransform, HuffmanCoding, ArithmeticCoding,
    analyze_entropy_vs_ms
)
from bwt import BWT, BlockBWT


# ============================================================
# 1. ENTROPY ANALYSIS
# ============================================================

def analyze_entropy_with_graph():
    """
    Анализ энтропии текста в зависимости от длины кода символа Ms
    """
    print("\n" + "="*70)
    print("АНАЛИЗ ЭНТРОПИИ")
    print("="*70)
    
    # Загружаем текст
    text_files = []
    if os.path.exists('test_data/enwik7.txt'):
        with open('test_data/enwik7.txt', 'r', encoding='utf-8', errors='ignore') as f:
            text_files.append(('enwik7.txt', f.read()[:100000]))  # Первые 100KB
    
    for text_name, text in text_files:
        print(f"\nТекст: {text_name}")
        
        # Фильтруем только ASCII символы
        filtered_text = ''.join(c for c in text if ord(c) < 128)
        data = filtered_text.encode('ascii')
        
        print(f"Размер текста (ASCII): {len(data)} байт")
        
        # Рассчитываем энтропию для разных Ms
        results = {}
        for ms in range(1, 5):
            if len(data) >= ms:
                entropy = calculate_entropy(data, Ms=ms)
                results[ms] = entropy
                print(f"  Ms={ms}: {entropy:.4f} бит/символ")
        
        return results


def test_mtf_entropy():
    """
    Исследуем влияние MTF на энтропию
    """
    print("\n" + "="*70)
    print("ВЛИЯНИЕ MTF НА ЭНТРОПИЮ")
    print("="*70)
    
    test_texts = [
        (b'aaabbbccaa', "Повторяющиеся последовательности"),
        (b'the quick brown fox jumps over the lazy dog', "Обычный текст"),
    ]
    
    for data, desc in test_texts:
        print(f"\n{desc}:")
        print(f"  Данные: {data[:50]}")
        
        # До MTF
        entropy_before = calculate_entropy(data, Ms=1)
        print(f"  Энтропия ДО MTF: {entropy_before:.4f}")
        
        # После MTF
        mtf_data = MTFTransform.encode(data)
        entropy_after = calculate_entropy(mtf_data, Ms=1)
        print(f"  Энтропия ПОСЛЕ MTF: {entropy_after:.4f}")
        print(f"  Изменение: {entropy_after - entropy_before:+.4f}")
        
        # Вывод
        if entropy_after < entropy_before:
            print(f"  Вывод: MTF УЛУЧШАЕТ сжатие на {entropy_before - entropy_after:.4f} бит")
        else:
            print(f"  Вывод: MTF НЕ ПОМОГАЕТ (энтропия выросла)")


# ============================================================
# 2. COMPRESSION WITH DIFFERENT ALGORITHMS
# ============================================================

def compress_with_huffman(data: bytes) -> Tuple[float, Dict]:
    """
    Сжатие с помощью Хаффмана
    """
    encoded_bits, codes, frequencies = HuffmanCoding.encode(data)
    
    # Метаданные: таблица кодов (размер в байтах)
    # Сериализуем таблицу кодов
    codes_size = len(str(codes).encode())
    
    original_bits = len(data) * 8
    compressed_bits = len(encoded_bits) + codes_size * 8
    
    ratio = original_bits / compressed_bits if compressed_bits > 0 else 1
    
    return ratio, {
        'original_bits': original_bits,
        'compressed_bits': compressed_bits,
        'ratio': ratio,
        'codes_size': codes_size
    }


def compress_with_rle_huffman(data: bytes) -> Tuple[float, Dict]:
    """
    Последовательное применение RLE + Хаффман
    """
    # RLE
    comp = RLECompressor(Ms=1, Mc=1)
    rle_data = comp.encode(data)
    
    # Хаффман
    ratio, _ = compress_with_huffman(rle_data)
    
    return ratio, {
        'rle_size': len(rle_data),
        'huffman_ratio': ratio,
        'final_ratio': len(data) / len(rle_data) * ratio if len(rle_data) > 0 else 1
    }


def compress_with_bwt_rle(data: bytes, block_size: int = 100000) -> Tuple[float, Dict]:
    """
    Последовательное применение BWT + RLE
    """
    # BWT с блочной обработкой
    block_bwt = BlockBWT(block_size=block_size)
    bwt_blocks, indices = block_bwt.forward(data)
    
    # Объединяем блоки
    bwt_data = b''.join(bwt_blocks)
    
    # RLE
    comp = RLECompressor(Ms=1, Mc=1)
    rle_data = comp.encode(bwt_data)
    
    ratio = len(data) / len(rle_data) if len(rle_data) > 0 else 1
    
    return ratio, {
        'bwt_size': len(bwt_data),
        'rle_size': len(rle_data),
        'ratio': ratio,
        'num_blocks': len(bwt_blocks)
    }


# ============================================================
# 3. COMPREHENSIVE TEST
# ============================================================

def comprehensive_test():
    """
    Полное тестирование всех алгоритмов на всех файлах
    """
    print("\n" + "="*70)
    print("ПОЛНОЕ ТЕСТИРОВАНИЕ АЛГОРИТМОВ СЖАТИЯ")
    print("="*70)
    
    # Находим тестовые файлы
    test_files = []
    
    if os.path.exists('test_data'):
        for f in os.listdir('test_data'):
            if f.endswith('.txt'):
                test_files.append(os.path.join('test_data', f))
    
    if os.path.exists('rlecoding'):
        for f in os.listdir('rlecoding'):
            if f.endswith('.rle'):
                test_files.append(os.path.join('rlecoding', f))
    
    if not test_files:
        print("Нет тестовых файлов!")
        return
    
    results = []
    
    for file_path in test_files[:5]:  # Тестируем первые 5 файлов
        print(f"\n{os.path.basename(file_path)}:")
        
        with open(file_path, 'rb') as f:
            data = f.read(100000)  # Читаем первые 100KB
        
        if len(data) == 0:
            continue
        
        print(f"  Размер: {len(data)} байт")
        
        # RLE
        try:
            comp_rle = RLECompressor(Ms=1, Mc=1)
            rle_data = comp_rle.encode(data)
            ratio_rle = len(data) / len(rle_data) if len(rle_data) > 0 else 1
            print(f"  RLE: {ratio_rle:.2f}x")
        except Exception as e:
            ratio_rle = 0
            print(f"  RLE: ERROR - {e}")
        
        # MTF + Entropy
        try:
            mtf_data = MTFTransform.encode(data)
            entropy_mtf = calculate_entropy(mtf_data, Ms=1)
            print(f"  MTF энтропия: {entropy_mtf:.4f} бит/символ")
        except Exception as e:
            print(f"  MTF: ERROR - {e}")
        
        # Huffman
        try:
            ratio_huffman, _ = compress_with_huffman(data)
            print(f"  Huffman: {ratio_huffman:.2f}x")
        except Exception as e:
            print(f"  Huffman: ERROR - {e}")
        
        # BWT + RLE
        try:
            ratio_bwt_rle, info = compress_with_bwt_rle(data, block_size=50000)
            print(f"  BWT+RLE: {ratio_bwt_rle:.2f}x ({info['num_blocks']} blocks)")
        except Exception as e:
            print(f"  BWT+RLE: ERROR - {e}")
        
        results.append({
            'file': os.path.basename(file_path),
            'size': len(data),
            'rle': ratio_rle,
            'huffman': ratio_huffman if ratio_huffman > 0 else None,
            'bwt_rle': ratio_bwt_rle if ratio_bwt_rle > 0 else None
        })
    
    return results


# ============================================================
# 4. MAIN
# ============================================================

def main():
    print("\n" + "="*70)
    print("ЭНТРОПИЙНОЕ КОДИРОВАНИЕ И BWT")
    print("="*70)
    
    # 1. Анализ энтропии
    entropy_results = analyze_entropy_with_graph()
    
    # 2. Влияние MTF
    test_mtf_entropy()
    
    # 3. Полное тестирование
    comp_results = comprehensive_test()
    
    print("\n" + "="*70)
    print("ВЫВОДЫ")
    print("="*70)
    print("""
1. ЭНТРОПИЯ:
   - Зависит от разнообразия символов в данных
   - Для текстов обычно 4-6 бит/символ
   - Для случайных данных близка к 8 бит/символ

2. MTF:
   - Преобразует данные, улучшая локальность
   - Помогает RLE лучше работать
   - Сам по себе не снижает энтропию

3. ХАФФМАН:
   - Оптимален для источников с известным распределением
   - Требует передачи таблицы кодов (метаданные)
   - Средняя длина кода близка к энтропии

4. BWT:
   - Группирует похожие символы вместе
   - Улучшает работу RLE
   - Требует блочной обработки для больших файлов
   - O(n) для распаковки (с перестановкой)

5. РЕКОМЕНДАЦИИ:
   - Для текстов: BWT -> MTF -> RLE -> Huffman
   - Для изображений: RLE + Huffman
   - Для случайных данных: Huffman только (не поможет RLE)
    """)
    
    print("\n" + "="*70)
    print("ГОТОВО!")
    print("="*70)


if __name__ == "__main__":
    main()
