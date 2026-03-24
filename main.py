import os

def main():
    print("\n" + "="*70)
    print("КОМПРЕССОРЫ - Проект готов")
    print("="*70)
    
    modules = [
        ("rle.py", "Run-Length Encoding"),
        ("entropy_coding.py", "Энтропия, MTF, Huffman, Arithmetic"),
        ("bwt.py", "Преобразование Барроуза-Уиллера"),
        ("suffix_array_lz.py", "LZ77, LZSS, LZ78, LZW"),
        ("compressors.py", "Базовые классы компрессоров"),
    ]
    
    print("\nОсновные модули:")
    for file, desc in modules:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"  ✓ {file:<25} ({size:>6} байт) - {desc}")
        else:
            print(f"  ✗ {file:<25} - НЕ НАЙДЕН")
    
    print("\nТестирование:")
    print("  python test_simple.py")
    
    print("\nДанные:")
    if os.path.exists("test_data"):
        files = os.listdir("test_data")
        print(f"  test_data/ - {len(files)} файлов")
    if os.path.exists("raw_images"):
        files = os.listdir("raw_images")
        print(f"  raw_images/ - {len(files)} файлов")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
