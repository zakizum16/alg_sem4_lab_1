"""
Тесты для всех компрессоров
"""
import os
import threading
import time
from base import Compressor
from rle_wrapper import RLECompressorWrapper
from huffman import HuffmanCompressor
from lz import LZSSCompressor, LZWCompressor
from combined import BWTRLECompressor, BWTMTFRLECompressor
from base import calculate_entropy


class TimeoutException(Exception):
    pass


def run_with_timeout(func, args, timeout=20):
    """Выполнить функцию с таймаутом"""
    result = [None]
    exception = [None]
    
    def target():
        try:
            result[0] = func(*args)
        except Exception as e:
            exception[0] = e
    
    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(timeout)
    
    if thread.is_alive():
        raise TimeoutException(f"Timeout after {timeout}s")
    
    if exception[0]:
        raise exception[0]
    
    return result[0]


def test_compressor(comp: Compressor, data: bytes, name: str, timeout: int = 20):
    """Протестировать один компрессор"""
    try:
        start_total = time.time()
        compressed = run_with_timeout(comp.compress, (data,), timeout)
        compress_time = time.time() - start_total
        
        decomp_start = time.time()
        decompressed = run_with_timeout(comp.decompress, (compressed,), timeout)
        decomp_time = time.time() - decomp_start
        
        # Проверка корректности
        if data != decompressed:
            return False, None
        
        comp.encode_time = compress_time
        comp.decode_time = decomp_time
        stats = comp.get_stats()
        ratio = stats['ratio']
        size_kb = stats['original'] / 1024
        
        print(f"  ✓ {name:<25} | {size_kb:>8.1f}KB -> {stats['compressed']:>8} | {ratio:>6.2f}x | E:{compress_time:.3f}s D:{decomp_time:.3f}s")
        return True, stats
    
    except TimeoutException:
        print(f"  ⊘ {name:<25} | TIMEOUT after {timeout}s")
        return False, None
    except Exception as e:
        error_msg = str(e)[:35]
        print(f"  ✗ {name:<25} | Error: {error_msg}")
        return False, None


def test_on_data(data: bytes, label: str, skip_slow: bool = False):
    """Протестировать все компрессоры на наборе данных"""
    print(f"\n{label} ({len(data)/1024:.1f}KB)")
    entropy = calculate_entropy(data)
    print(f"Энтропия: {entropy:.3f} бит/символ")
    print("-" * 130)
    
    compressors = [
        (RLECompressorWrapper(1, 1), "RLE(Ms=1,Mc=1)"),
        (LZWCompressor(12), "LZW(12 bits)"),
    ]
    
    if not skip_slow or len(data) < 100000:
        compressors += [
            (HuffmanCompressor(), "Huffman"),
        ]
    
    if not skip_slow or len(data) < 50000:
        compressors += [
            (LZSSCompressor(4096), "LZSS"),
            (BWTRLECompressor(900000), "BWT+RLE"),
            (BWTMTFRLECompressor(900000), "BWT+MTF+RLE"),
        ]
    
    results = []
    for comp, name in compressors:
        success, stats = test_compressor(comp, data, name, timeout=20)
        if success:
            results.append(stats)
    
    return results


def load_test_files():
    """Загрузить тестовые файлы"""
    files = []
    
    if os.path.exists("test_data"):
        for f in os.listdir("test_data"):
            path = os.path.join("test_data", f)
            if os.path.isfile(path):
                size = os.path.getsize(path)
                files.append((path, f, size))
    
    if os.path.exists("raw_images"):
        for f in os.listdir("raw_images"):
            path = os.path.join("raw_images", f)
            if os.path.isfile(path) and f.endswith('.raw'):
                size = os.path.getsize(path)
                files.append((path, f, size))
    
    return sorted(files, key=lambda x: x[2])


def main():
    print("\n" + "="*130)
    print("ТЕСТИРОВАНИЕ КОМПРЕССОРОВ")
    print("="*130)
    
    # Маленькие тестовые данные
    test_cases = [
        (b"AAAAAABBBBCCCD" * 100, "Простые данные (повторяемость)"),
        (bytes(range(256)) * 100, "Случайные данные (256 символов)"),
        (b"The quick brown fox jumps over the lazy dog. " * 100, "Текстовые данные (English)"),
        ("Быстрая коричневая лиса прыгает через ленивую собаку. ".encode('utf-8') * 100, "Текстовые данные (Russian)"),
    ]
    
    for data, label in test_cases:
        test_on_data(data, label, skip_slow=True)
    
    # Файлы из test_data и raw_images
    files = load_test_files()
    if files:
        print(f"\n\n{'='*130}")
        print("ТЕСТИРОВАНИЕ НА РЕАЛЬНЫХ ФАЙЛАХ")
        print(f"{'='*130}")
        
        for path, filename, size in files[:5]:  # Ограничиваем до 5 файлов
            try:
                with open(path, 'rb') as f:
                    data = f.read()
                test_on_data(data, f"Файл: {filename}", skip_slow=size > 100000)
            except Exception as e:
                print(f"Ошибка при чтении {filename}: {e}")
    
    print("\n" + "="*130)
    print("Тестирование завершено!")
    print("="*130 + "\n")


if __name__ == "__main__":
    main()
