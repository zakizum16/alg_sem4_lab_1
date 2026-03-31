import os
import sys
from pathlib import Path

def print_header(text):
    print("\n" + "="*70)
    print(text.center(70))
    print("="*70 + "\n")

def print_menu(options):
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    print()

def main():
    while True:
        print_header("КОМПРЕССОРЫ - ГЛАВНОЕ МЕНЮ")
        
        print("Выберите действие:")
        options = [
            "Запустить тесты всех компрессоров",
            "Сжать файл с помощью RLE",
            "Информация о проекте",
            "Выход"
        ]
        print_menu(options)
        
        try:
            choice = input("Ваш выбор (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nВыход.")
            break
        
        if choice == "1":
            run_tests()
        elif choice == "2":
            run_rle()
        elif choice == "3":
            show_info()
        elif choice == "4":
            print("\nВыход.")
            break
        else:
            print("\n[ERR] Неверный выбор. Попробуйте снова.")
        
        input("\nНажмите Enter для продолжения...")

def run_tests():
    print_header("ЗАПУСК ТЕСТОВ")
    try:
        from tests import test_on_data
        from pathlib import Path
        
        test_data_path = Path("test_data")
        if test_data_path.exists():
            print("Запуск тестов на файлах из test_data...\n")
            
            test_files = {
                'test_data/russian_text.txt': 'Текст (русский)',
            }
            
            for file_path, desc in test_files.items():
                if Path(file_path).exists():
                    with open(file_path, 'rb') as f:
                        data = f.read()
                    test_on_data(data, desc, skip_slow=True)
        else:
            print("[ERR] Папка test_data не найдена")
    except Exception as e:
        print(f"[ERR] Ошибка при запуске тестов: {e}")

def run_rle():
    print_header("RLE КОМПРЕССОР")
    try:
        from rle import select_file
        
        file_path = select_file()
        if file_path:
            from rle import RLEFileHandler, determine_ms
            
            Ms = determine_ms(file_path)
            Mc = 1
            
            print(f"\nСжатие: {file_path}")
            print(f"Параметры: Ms={Ms}, Mc={Mc}")
            
            handler = RLEFileHandler(Ms=Ms, Mc=Mc, output_dir="rlecoding")
            
            print("Сжатие...")
            original_size, compressed_size, compressed_path = handler.compress_file(file_path)
            ratio = original_size / compressed_size if compressed_size > 0 else 1
            
            print(f"\nИсходный размер:  {original_size:>12,} байт")
            print(f"Сжатый размер:    {compressed_size:>12,} байт")
            print(f"Коэффициент:      {ratio:>23.2f}x")
            print(f"Сохранено в:      {compressed_path}")
            
            print("\nРаспаковка...")
            decompressed_size, _, decompressed_path = handler.decompress_file(compressed_path)
            
            with open(file_path, 'rb') as f1, open(decompressed_path, 'rb') as f2:
                original = f1.read()
                decompressed = f2.read()
                is_correct = original == decompressed
            
            status = "[OK]" if is_correct else "[ERR]"
            print(f"Статус проверки:  {status} (данные совпадают)" if is_correct else f"Статус проверки:  {status}")
            print(f"Сохранено в:      {decompressed_path}")
    except Exception as e:
        print(f"[ERR] Ошибка: {e}")

def show_info():
    print_header("ИНФОРМАЦИЯ О ПРОЕКТЕ")
    
    info = {
        "Проект": "Компрессоры данных",
        "Язык": "Python 3.7+",
        "Версия": "1.0",
    }
    
    print("Основная информация:")
    for key, value in info.items():
        print(f"  {key:<20}: {value}")
    
    print("\n\nДоступные компрессоры:")
    compressors = [
        ("RLE", "Run-Length Encoding"),
        ("Huffman", "Кодирование Хаффмана"),
        ("LZSS", "LZ77-подобный алгоритм"),
        ("LZW", "Lempel-Ziv-Welch"),
        ("BWT", "Преобразование Барроуза-Уиллера"),
        ("BWT+RLE", "Комбинированный (BWT + RLE)"),
        ("BWT+MTF+RLE", "Комбинированный (BWT + MTF + RLE)"),
    ]
    
    for name, desc in compressors:
        print(f"  • {name:<15} - {desc}")
    
    print("\n\nМодули проекта:")
    modules = [
        ("base.py", "Базовый класс Compressor"),
        ("rle.py", "RLE компрессор"),
        ("huffman.py", "Huffman кодирование"),
        ("lz.py", "Семейство LZ алгоритмов"),
        ("bwt.py", "BWT преобразование"),
        ("mtf.py", "Move-To-Front трансформация"),
        ("combined.py", "Комбинированные компрессоры"),
        ("tests.py", "Автоматические тесты"),
        ("raw_converter.py", "Конвертирование изображений в RAW"),
        ("raw_opener.py", "Просмотр RAW файлов"),
    ]
    
    for file, desc in modules:
        if os.path.exists(file):
            size = os.path.getsize(file)
            status = "[OK]"
        else:
            size = 0
            status = "[ERR]"
        print(f"  {status} {file:<20} - {desc}")
    
    print("\n\nКаталоги данных:")
    dirs = [
        ("test_data", "Тестовые файлы для сжатия"),
        ("raw_images", "RAW изображения"),
        ("rlecoding", "Результаты RLE кодирования"),
    ]
    
    for dirname, desc in dirs:
        if os.path.exists(dirname):
            count = len(os.listdir(dirname))
            status = "[OK]"
        else:
            count = 0
            status = "[ERR]"
        print(f"  {status} {dirname:<20} - {desc} ({count} файлов)")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана.")
        sys.exit(0)
