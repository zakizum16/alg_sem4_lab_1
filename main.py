"""
Главная демонстрация проекта компрессоров
"""
import os


def main():
    print("\n" + "="*80)
    print("PROJETO DE COMPRESSORES")
    print("="*80)
    
    print("\n📁 СТРУКТУРА ФАЙЛОВ:\n")
    
    modules = [
        ("base.py", "Базовый класс Compressor и утилиты"),
        ("rle.py", "Run-Length Encoding (RLE)"),
        ("mtf.py", "Move-To-Front трансформация (MTF)"),
        ("huffman.py", "Huffman кодирование"),
        ("lz.py", "Семейство алгоритмов LZ (LZSS, LZ78, LZW)"),
        ("bwt.py", "Преобразование Барроуза-Уиллера (BWT)"),
        ("rle_wrapper.py", "Обёртка RLE в формате Compressor"),
        ("combined.py", "Комбинированные компрессоры (BWT+RLE, BWT+MTF+RLE)"),
        ("tests.py", "Автоматические тесты всех компрессоров"),
    ]
    
    for file, desc in modules:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"  ✓ {file:<20} ({size:>6} байт) - {desc}")
        else:
            print(f"  ✗ {file:<20} - НЕ НАЙДЕН")
    
    print("\n📋 ИСПОЛЬЗОВАНИЕ:\n")
    print("  1. Запусить тесты:")
    print("     python tests.py")
    print("\n  2. Использовать компрессоры в коде:")
    print("     from base import Compressor")
    print("     from huffman import HuffmanCompressor")
    print("     from combined import BWTRLECompressor, BWTMTFRLECompressor")
    print("\n  3. Создавать цепочки компрессоров:")
    print("     comp1 = HuffmanCompressor()")
    print("     comp2 = RLECompressorWrapper()")
    print("     data1 = comp1.compress(data)")
    print("     data2 = comp2.compress(data1)")
    
    print("\n📊 ДОСТУПНЫЕ КОМПРЕССОРЫ:\n")
    print("  Отдельные:")
    print("    • RLE (Run-Length Encoding)")
    print("    • Huffman (кодирование Хаффмана)")
    print("    • LZSS (LZ77-подобный)")
    print("    • LZW (Lempel-Ziv-Welch)")
    print("    • BWT (преобразование Барроуза-Уиллера)")
    print("\n  Комбинированные:")
    print("    • BWT+RLE (BWT дополнен RLE)")
    print("    • BWT+MTF+RLE (BWT + Move-To-Front + RLE)")
    
    print("\n  Преобразования:")
    print("    • MTF (Move-To-Front)")
    
    print("\n📂 ДАННЫЕ:\n")
    if os.path.exists("test_data"):
        files = os.listdir("test_data")
        print(f"  test_data/ - {len(files)} файлов")
    if os.path.exists("raw_images"):
        files = os.listdir("raw_images")
        print(f"  raw_images/ - {len(files)} файлов")
    if os.path.exists("rlecoding"):
        files = os.listdir("rlecoding")
        print(f"  rlecoding/ - {len(files)} файлов (результаты кодирования)")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()

