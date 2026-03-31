import os
import sys
import time
import struct
import math
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter

from base import Compressor
from rle import RLECompressor
from lz import LZSSCompressor, LZWCompressor
from combined import BWTRLECompressor, BWTMTFRLECompressor, BWTMTFHACompressor, LZSSHACompressor, LZWHACompressor
from bwt import BlockBWT
from mtf import MTFTransform


def generate_text_data(size: int = 1000) -> bytes:
    text = "The quick brown fox jumps over the lazy dog. " * (size // 45)
    return text[:size].encode('utf-8')


def generate_binary_data(size: int = 1000) -> bytes:
    return bytes(np.random.randint(0, 256, size, dtype=np.uint8))


def generate_repetitive_data(size: int = 1000) -> bytes:
    pattern = b"AAABBBCCCDDD"
    return (pattern * (size // len(pattern) + 1))[:size]


def calculate_entropy(data: bytes) -> float:
    if not data:
        return 0
    
    byte_counts = Counter(data)
    entropy = 0
    n = len(data)
    
    for count in byte_counts.values():
        p = count / n
        entropy -= p * math.log2(p)
    
    return entropy


def test_bwt_block_size(block_sizes: List[int] = None) -> Tuple[List[int], List[float], float]:
    if block_sizes is None:
        block_sizes = [256, 512, 1024]
    
    # Используем простые текстовые данные размером ~1000 байт
    data = generate_text_data(1000)
    
    # Исходная энтропия
    original_entropy = calculate_entropy(data)
    
    entropies = []
    
    for block_size in block_sizes:
        try:
            print(f"  Block size {block_size:>5}...", end='', flush=True)
            bwt = BlockBWT(min(block_size, len(data)))
            blocks, _ = bwt.forward(data)
            
            mtf = MTFTransform()
            all_mtf_data = bytearray()
            for block in blocks:
                mtf_block = mtf.encode(block)
                all_mtf_data.extend(mtf_block)
            
            entropy = calculate_entropy(bytes(all_mtf_data))
            entropies.append(entropy)
            print(f" entropy = {entropy:.4f}")
        except Exception as e:
            print(f" ошибка - {e}")
            entropies.append(None)
    
    return block_sizes, entropies, original_entropy


def test_lzss_buffer_size(buffer_sizes: List[int] = None) -> Tuple[List[int], List[float]]:
    if buffer_sizes is None:
        buffer_sizes = [256, 512, 1024, 2048]
    
    data = generate_text_data(1000)
    
    ratios = []
    
    for buffer_size in buffer_sizes:
        try:
            print(f"  Buffer {buffer_size:>5}...", end='', flush=True)
            compressor = LZSSCompressor(window_size=buffer_size)
            compressed = compressor.compress(data)
            ratio = len(data) / len(compressed) if len(compressed) > 0 else 1
            ratios.append(ratio)
            print(f" ratio = {ratio:.3f}")
        except Exception as e:
            print(f" ошибка - {e}")
            ratios.append(None)
    
    return buffer_sizes, ratios


def test_lzw_dict_size(dict_sizes: List[int] = None) -> Tuple[List[int], List[float]]:
    if dict_sizes is None:
        dict_sizes = [8, 9, 10, 11]
    
    data = generate_text_data(1000)
    
    ratios = []
    
    for code_bits in dict_sizes:
        try:
            print(f"  Code bits {code_bits:>2}...", end='', flush=True)
            compressor = LZWCompressor(max_code_bits=code_bits)
            compressed = compressor.compress(data)
            ratio = len(data) / len(compressed) if len(compressed) > 0 else 1
            ratios.append(ratio)
            print(f" ratio = {ratio:.3f}")
        except Exception as e:
            print(f" ошибка - {e}")
            ratios.append(None)
    
    return dict_sizes, ratios


def create_graphs(output_dir: str = "graphs"):
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n" + "="*70)
    print("ИССЛЕДОВАНИЕ 1: Энтропия BWT+MTF от размера блока")
    print("="*70 + "\n")
    
    block_sizes, entropies, orig_entropy = test_bwt_block_size()
    
    valid_indices = [i for i, e in enumerate(entropies) if e is not None]
    valid_sizes = [block_sizes[i] for i in valid_indices]
    valid_entropies = [entropies[i] for i in valid_indices]
    
    if valid_entropies:
        plt.figure(figsize=(10, 6))
        plt.plot(valid_sizes, valid_entropies, 'b-o', linewidth=2, markersize=8, label='Entropy after BWT+MTF')
        plt.axhline(y=orig_entropy, color='r', linestyle='--', linewidth=2, label=f'Original entropy ({orig_entropy:.4f})')
        plt.xlabel('Block Size (bytes)', fontsize=12)
        plt.ylabel('Entropy (bits/byte)', fontsize=12)
        plt.title('Зависимость энтропии от размера блока BWT+MTF', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=11)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/01_bwt_entropy.png', dpi=300)
        print(f"\n✓ График сохранён: {output_dir}/01_bwt_entropy.png")
        plt.close()
    
    print("\n" + "="*70)
    print("ИССЛЕДОВАНИЕ 2: Коэффициент сжатия LZSS от размера буфера")
    print("="*70 + "\n")
    
    buffer_sizes, ratios = test_lzss_buffer_size()
    
    valid_indices = [i for i, r in enumerate(ratios) if r is not None]
    valid_sizes = [buffer_sizes[i] for i in valid_indices]
    valid_ratios = [ratios[i] for i in valid_indices]
    
    if valid_ratios:
        plt.figure(figsize=(10, 6))
        plt.plot(valid_sizes, valid_ratios, 'g-s', linewidth=2, markersize=8)
        plt.xlabel('Buffer Size (bytes)', fontsize=12)
        plt.ylabel('Compression Ratio (original/compressed)', fontsize=12)
        plt.title('Зависимость коэффициента сжатия LZSS от размера буфера', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/02_lzss_buffer.png', dpi=300)
        print(f"\n✓ График сохранён: {output_dir}/02_lzss_buffer.png")
        plt.close()
    
    print("\n" + "="*70)
    print("ИССЛЕДОВАНИЕ 3: Коэффициент сжатия LZW от размера словаря")
    print("="*70 + "\n")
    
    dict_sizes, ratios = test_lzw_dict_size()
    
    valid_indices = [i for i, r in enumerate(ratios) if r is not None]
    valid_sizes = [dict_sizes[i] for i in valid_indices]
    valid_ratios = [ratios[i] for i in valid_indices]
    
    if valid_ratios:
        plt.figure(figsize=(10, 6))
        plt.plot(valid_sizes, valid_ratios, 'm-^', linewidth=2, markersize=8)
        plt.xlabel('Code bits', fontsize=12)
        plt.ylabel('Compression Ratio (original/compressed)', fontsize=12)
        plt.title('Зависимость коэффициента сжатия LZW от размера словаря', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/03_lzw_dict.png', dpi=300)
        print(f"\n✓ График сохранён: {output_dir}/03_lzw_dict.png")
        plt.close()


def test_all_compressors(output_dir: str = "graphs") -> pd.DataFrame:
    
    compressors = [
        ("RLE", RLECompressor(1, 1)),
        ("BWT+RLE", BWTRLECompressor(block_size=256)),
        ("BWT+MTF+RLE", BWTMTFRLECompressor(block_size=256)),
        ("BWT+MTF+HA", BWTMTFHACompressor(block_size=256)),
        ("LZSS", LZSSCompressor(window_size=256)),
        ("LZSS+HA", LZSSHACompressor(window_size=256)),
        ("LZW", LZWCompressor(max_code_bits=9)),
        ("LZW+HA", LZWHACompressor(max_code_bits=9)),
    ]
    
    test_data = [
        ('Text', 'Текст', generate_text_data(1000)),
        ('Binary', 'Бинар', generate_binary_data(1000)),
        ('Repetitive', 'Повтор', generate_repetitive_data(1000)),
    ]
    
    results = []
    
    print("\n" + "="*100)
    print("ТЕСТИРОВАНИЕ ВСЕХ КОМПРЕССОРОВ НА ПРОСТЫХ ДАННЫХ (1000 байт)")
    print("="*100 + "\n")
    
    for data_type, data_label, data in test_data:
        print(f"\nТип данных: {data_label} ({len(data)} байт)")
        print("-" * 100)
        
        original_size = len(data)
        
        for comp_name, compressor in compressors:
            try:
                start_time = time.time()
                compressed = compressor.compress(data)
                compress_time = time.time() - start_time
                compressed_size = len(compressed)
                
                start_time = time.time()
                decompressed = compressor.decompress(compressed)
                decompress_time = time.time() - start_time
                
                is_valid = data == decompressed
                
                ratio = original_size / compressed_size if compressed_size > 0 else 0
                saved = original_size - compressed_size
                
                status = "✓" if is_valid else "✗"
                
                print(f"  {status} {comp_name:<20} | Compr: {compressed_size:>5} | Ratio: {ratio:>6.2f}x | "
                      f"Saved: {saved:>6} | Time: {compress_time:>6.3f}s")
                
                results.append({
                    'Data Type': data_type,
                    'Original Size (bytes)': original_size,
                    'Compressor': comp_name,
                    'Compressed Size (bytes)': compressed_size,
                    'Compression Ratio': ratio,
                    'Bytes Saved': saved,
                    'Compress Time (s)': compress_time,
                    'Decompress Time (s)': decompress_time,
                    'Valid': is_valid
                })
            
            except Exception as e:
                print(f"  ✗ {comp_name:<20} | ОШИБКА: {str(e)[:40]}")
                results.append({
                    'Data Type': data_type,
                    'Original Size (bytes)': original_size,
                    'Compressor': comp_name,
                    'Compressed Size (bytes)': None,
                    'Compression Ratio': None,
                    'Bytes Saved': None,
                    'Compress Time (s)': None,
                    'Decompress Time (s)': None,
                    'Valid': False
                })
    
    df = pd.DataFrame(results)
    
    csv_path = f'{output_dir}/results_table.csv'
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"\n✓ Таблица сохранена: {csv_path}")
    
    try:
        excel_path = f'{output_dir}/results_table.xlsx'
        df.to_excel(excel_path, index=False)
        print(f"✓ Таблица сохранена: {excel_path}")
    except:
        pass
    
    print("\n" + "="*100)
    print("СВОДНАЯ ТАБЛИЦА РЕЗУЛЬТАТОВ")
    print("="*100 + "\n")
    
    summary_df = df[df['Valid'] == True].copy()
    if not summary_df.empty:
        summary_df = summary_df.sort_values(['Data Type', 'Compression Ratio'], 
                                            ascending=[True, False])
        
        for data_type in summary_df['Data Type'].unique():
            print(f"\n{data_type} данные:")
            print("-" * 100)
            type_data = summary_df[summary_df['Data Type'] == data_type]
            print(type_data[['Compressor', 'Original Size (bytes)', 
                             'Compressed Size (bytes)', 'Compression Ratio']].to_string(index=False))
    
    return df


def plot_comparison(df: pd.DataFrame, output_dir: str = "graphs"):
    
    valid_df = df[df['Valid'] == True].copy()
    
    if valid_df.empty:
        print("Нет валидных данных для графиков")
        return
    
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    
    data_types = ['Text', 'Binary', 'Repetitive']
    for idx, data_type in enumerate(data_types):
        type_data = valid_df[valid_df['Data Type'] == data_type]
        if type_data.empty:
            continue
        
        comp_avg = type_data.groupby('Compressor')['Compression Ratio'].mean().sort_values(ascending=False)
        
        axes[idx].barh(comp_avg.index, comp_avg.values, color='skyblue', edgecolor='navy')
        axes[idx].set_xlabel('Средний коэффициент сжатия', fontsize=11)
        axes[idx].set_title(f'{data_type}', fontsize=12, fontweight='bold')
        axes[idx].grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/04_compressor_comparison.png', dpi=300)
    print(f"✓ График сохранён: {output_dir}/04_compressor_comparison.png")
    plt.close()
    
    overall_avg = valid_df.groupby('Compressor')['Compression Ratio'].mean().sort_values(ascending=False)
    
    plt.figure(figsize=(12, 6))
    colors = plt.cm.viridis(np.linspace(0, 1, len(overall_avg)))
    bars = plt.barh(overall_avg.index, overall_avg.values, color=colors, edgecolor='black')
    
    plt.xlabel('Средний коэффициент сжатия', fontsize=12)
    plt.title('Сравнение эффективности всех компрессоров', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, axis='x')
    
    for bar in bars:
        width = bar.get_width()
        plt.text(width, bar.get_y() + bar.get_height()/2, f'{width:.2f}x',
                ha='left', va='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/05_overall_comparison.png', dpi=300)
    print(f"✓ График сохранён: {output_dir}/05_overall_comparison.png")
    plt.close()


def main():
    """Главная функция"""
    print("\n" + "="*70)
    print("ЛАБОРАТОРНАЯ РАБОТА: Исследование алгоритмов сжатия данных")
    print("="*70)
    
    output_dir = "graphs"
    
    create_graphs(output_dir)
    
    results_df = test_all_compressors(output_dir)
    
    plot_comparison(results_df, output_dir)
    
    print("\n" + "="*70)
    print("✓ ВСЕ ИССЛЕДОВАНИЯ ЗАВЕРШЕНЫ")
    print("="*70)
    print(f"\nРезультаты сохранены в папке: {output_dir}/")
    print("  - 01_bwt_entropy.png     : График энтропии BWT+MTF")
    print("  - 02_lzss_buffer.png     : График LZSS от размера буфера")
    print("  - 03_lzw_dict.png        : График LZW от размера словаря")
    print("  - 04_compressor_comparison.png : Сравнение по типам файлов")
    print("  - 05_overall_comparison.png    : Общее сравнение")
    print("  - results_table.csv      : Таблица результатов")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
