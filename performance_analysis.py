#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исследование зависимости коэффициента сжатия и времени работы от параметров
"""

import time
import os
from suffix_array_lz import LZSS, LZW
from efficient_bwt_canonical import EfficientBWT, CanonicalHuffman


class PerformanceAnalysis:
    """Анализ производительности алгоритмов"""
    
    @staticmethod
    def analyze_lzss(data: bytes, buffer_sizes: list = None) -> dict:
        """
        Исследование LZSS в зависимости от размера буфера.
        
        Args:
            data: Тестовые данные
            buffer_sizes: Список размеров буфера для теста
        
        Returns:
            {размер_буфера: {время, размер_сжатого, коэффициент}}
        """
        if buffer_sizes is None:
            buffer_sizes = [256, 512, 1024, 2048, 4096, 8192]
        
        results = {}
        
        for buf_size in buffer_sizes:
            if buf_size > len(data):
                continue
            
            start = time.time()
            encoded = LZSS.encode(data, window_size=buf_size, lookahead_size=18)
            encode_time = time.time() - start
            
            start = time.time()
            decoded = LZSS.decode(encoded)
            decode_time = time.time() - start
            
            ratio = len(data) / len(encoded) if len(encoded) > 0 else 1
            
            results[buf_size] = {
                'encoded_size': len(encoded),
                'compression_ratio': ratio,
                'encode_time': encode_time,
                'decode_time': decode_time,
                'total_time': encode_time + decode_time,
                'correct': data == decoded
            }
        
        return results
    
    @staticmethod
    def analyze_lzw(data: bytes, dict_sizes: list = None) -> dict:
        """
        Исследование LZW в зависимости от размера словаря.
        
        Args:
            data: Тестовые данные
            dict_sizes: Список размеров словаря для теста
        
        Returns:
            {размер_словаря: {время, размер_сжатого, коэффициент}}
        """
        if dict_sizes is None:
            dict_sizes = [256, 512, 1024, 2048, 4096, 8192, 16384]
        
        results = {}
        
        for dict_size in dict_sizes:
            start = time.time()
            encoded = LZW.encode(data, max_dict_size=dict_size)
            encode_time = time.time() - start
            
            start = time.time()
            decoded = LZW.decode(encoded, max_dict_size=dict_size)
            decode_time = time.time() - start
            
            ratio = len(data) / len(encoded) if len(encoded) > 0 else 1
            
            results[dict_size] = {
                'encoded_size': len(encoded),
                'compression_ratio': ratio,
                'encode_time': encode_time,
                'decode_time': decode_time,
                'total_time': encode_time + decode_time,
                'correct': data == decoded
            }
        
        return results
    
    @staticmethod
    def print_lzss_results(results: dict):
        """Печать результатов LZSS"""
        print("\n" + "="*80)
        print("АНАЛИЗ LZSS: Влияние размера буфера")
        print("="*80)
        print(f"\n{'Размер буфера':<15} {'Сжато (B)':<15} {'Коэф.':<10} {'Сжатие (мс)':<15} {'Распаковка (мс)':<15} {'Статус':<10}")
        print("-"*80)
        
        for buf_size in sorted(results.keys()):
            r = results[buf_size]
            status = "OK" if r['correct'] else "FAIL"
            print(f"{buf_size:<15} {r['encoded_size']:<15} {r['compression_ratio']:<10.2f} {r['encode_time']*1000:<15.3f} {r['decode_time']*1000:<15.3f} {status:<10}")
        
        # Выводы
        best_ratio = max(results.values(), key=lambda x: x['compression_ratio'])
        best_time = min(results.values(), key=lambda x: x['total_time'])
        
        print(f"\nВывод:")
        print(f"  Лучший коэффициент: буфер={[k for k,v in results.items() if v==best_ratio][0]}")
        print(f"  Самая быстрая работа: буфер={[k for k,v in results.items() if v==best_time][0]}")
    
    @staticmethod
    def print_lzw_results(results: dict):
        """Печать результатов LZW"""
        print("\n" + "="*80)
        print("АНАЛИЗ LZW: Влияние размера словаря")
        print("="*80)
        print(f"\n{'Размер словаря':<15} {'Сжато (B)':<15} {'Коэф.':<10} {'Сжатие (мс)':<15} {'Распаковка (мс)':<15} {'Статус':<10}")
        print("-"*80)
        
        for dict_size in sorted(results.keys()):
            r = results[dict_size]
            status = "OK" if r['correct'] else "FAIL"
            print(f"{dict_size:<15} {r['encoded_size']:<15} {r['compression_ratio']:<10.2f} {r['encode_time']*1000:<15.3f} {r['decode_time']*1000:<15.3f} {status:<10}")
        
        # Выводы
        best_ratio = max(results.values(), key=lambda x: x['compression_ratio'])
        best_time = min(results.values(), key=lambda x: x['total_time'])
        
        print(f"\nВывод:")
        print(f"  Лучший коэффициент: словарь={[k for k,v in results.items() if v==best_ratio][0]}")
        print(f"  Самая быстрая работа: словарь={[k for k,v in results.items() if v==best_time][0]}")


def analyze_on_files():
    """Анализ на реальных файлах"""
    
    print("\n" + "="*80)
    print("АНАЛИЗ НА РЕАЛЬНЫХ ФАЙЛАХ")
    print("="*80)
    
    test_files = []
    
    # Читаем тестовые файлы
    if os.path.exists('test_data/russian_text.txt'):
        with open('test_data/russian_text.txt', 'rb') as f:
            test_files.append(('Русский текст', f.read()))
    
    if os.path.exists('test_data/enwik7.txt'):
        with open('test_data/enwik7.txt', 'rb') as f:
            test_files.append(('enwik7 (10MB)', f.read(100000)))  # только первые 100K
    
    for name, data in test_files:
        print(f"\n{name}: {len(data)} байт")
        print("-"*80)
        
        # LZSS
        print(f"\n  LZSS (буфер=4096):")
        start = time.time()
        lzss_enc = LZSS.encode(data, window_size=4096)
        lzss_time = time.time() - start
        lzss_ratio = len(data) / len(lzss_enc)
        print(f"    Размер: {len(lzss_enc)} байт ({lzss_ratio:.2f}x за {lzss_time:.3f}с)")
        
        # LZW
        print(f"\n  LZW (словарь=4096):")
        start = time.time()
        lzw_enc = LZW.encode(data, max_dict_size=4096)
        lzw_time = time.time() - start
        lzw_ratio = len(data) / len(lzw_enc)
        print(f"    Размер: {len(lzw_enc)} байт ({lzw_ratio:.2f}x за {lzw_time:.3f}с)")
        
        # BWT + RLE
        print(f"\n  BWT (детальное):")
        try:
            start = time.time()
            bwt_data, idx = EfficientBWT.forward(data)
            bwt_time = time.time() - start
            print(f"    Время: {bwt_time:.3f}с")
        except Exception as e:
            print(f"    Ошибка: {e}")


if __name__ == '__main__':
    # Тестовые данные
    with open('test_data/russian_text.txt', 'rb') as f:
        test_data = f.read()
    
    print(f"\nТестовые данные: {len(test_data)} байт")
    
    # Анализ LZSS
    lzss_results = PerformanceAnalysis.analyze_lzss(
        test_data,
        buffer_sizes=[256, 512, 1024, 2048, 4096, 8192]
    )
    PerformanceAnalysis.print_lzss_results(lzss_results)
    
    # Анализ LZW
    lzw_results = PerformanceAnalysis.analyze_lzw(
        test_data,
        dict_sizes=[256, 512, 1024, 2048, 4096, 8192, 16384]
    )
    PerformanceAnalysis.print_lzw_results(lzw_results)
    
    # Анализ на файлах
    analyze_on_files()
    
    print("\n" + "="*80)
    print("ОБЩИЕ ВЫВОДЫ")
    print("="*80)
    print("""
    1. LZSS:
       - Коэффициент сжатия растёт с размером буфера (до определённого предела)
       - Большие буферы медленнее из-за поиска совпадений
       - Оптимум: буфер 2048-4096 для большинства данных
    
    2. LZW:
       - Коэффициент сжатия растёт с размером словаря
       - Даже с ограничением словаря (4096-8192) показывает хорошие результаты
       - Начальный словарь не нужен - восстанавливается из кодов
       - Быстрее LZSS для случайных данных
    
    3. Рекомендации:
       - Для текста: LZW с словарём 4096-8192
       - Для корреляции: LZSS с буфером 4096
       - Для большых файлов: BWT + RLE + Хаффман
    """)
