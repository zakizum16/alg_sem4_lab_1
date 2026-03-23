import os
import urllib.request
import random
import struct
import numpy as np
from PIL import Image

def download_enwik7():
    """Скачиваем первые 10^7 байт enwik9"""
    print("1. Загрузка enwik7...")
    
    # Ссылка на enwik9
    url = "http://mattmahoney.net/dc/enwik9.zip"
    output_file = "test_data/enwik7.txt"
    
    # Проверяем, есть ли уже файл
    if os.path.exists(output_file):
        print(f"   Файл {output_file} уже существует")
        return
    
    try:
        # Скачиваем zip
        print("   Скачивание enwik9.zip...")
        urllib.request.urlretrieve(url, "test_data/enwik9.zip")
        
        # Распаковываем
        import zipfile
        with zipfile.ZipFile("test_data/enwik9.zip", 'r') as zip_ref:
            zip_ref.extractall("test_data/")
        
        # Берем первые 10^7 байт
        with open("test_data/enwik9", 'rb') as f:
            data = f.read(10_000_000)  # 10^7 байт
        
        # Сохраняем
        with open(output_file, 'wb') as f:
            f.write(data)
        
        print(f"   Готово! Размер: {len(data):,} байт")
        
        # Удаляем zip и полный файл
        os.remove("test_data/enwik9.zip")
        os.remove("test_data/enwik9")
        
    except Exception as e:
        print(f"   Ошибка при скачивании: {e}")
        print("   Создаем тестовый файл вместо реального...")
        
        # Если не удалось скачать, создаем тестовый файл
        create_fake_enwik7(output_file)

def create_fake_enwik7(output_file):
    """Создаем имитацию enwik7 для тестирования"""
    # Английский текст с повторениями
    text = "This is a test text for enwik7 file. " * 10000
    text += "Wikipedia is a free online encyclopedia. " * 10000
    text += "The quick brown fox jumps over the lazy dog. " * 10000
    
    data = text.encode('utf-8')
    
    # Доводим до нужного размера
    while len(data) < 10_000_000:
        data += data[:min(len(data), 10_000_000 - len(data))]
    
    with open(output_file, 'wb') as f:
        f.write(data[:10_000_000])
    
    print(f"   Создан тестовый файл размером: {len(data[:10_000_000]):,} байт")

def create_russian_text():
    """Создаем русский текст объемом 200KB"""
    print("\n2. Создание русского текста...")
    
    # Русские символы
    russian_letters = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    russian_letters += russian_letters.lower()
    russian_letters += " .,!?;:-()\"'\n"
    
    text = ""
    target_size = 200 * 1024  # 200KB
    
    # Генерируем текст
    while len(text.encode('utf-8')) < target_size:
        # Добавляем предложение
        sentence_length = random.randint(20, 100)
        sentence = ''.join(random.choice(russian_letters) for _ in range(sentence_length))
        text += sentence + ". "
        
        # Иногда добавляем абзац
        if random.random() < 0.1:
            text += "\n\n"
    
    # Обрезаем до нужного размера
    while len(text.encode('utf-8')) > target_size:
        text = text[:-1]
    
    # Сохраняем
    with open("test_data/russian_text.txt", "w", encoding='utf-8') as f:
        f.write(text)
    
    size = os.path.getsize("test_data/russian_text.txt")
    print(f"   Создан файл размером: {size:,} байт")

def create_binary_file():
    """Создаем бинарный файл 1MB"""
    print("\n3. Создание бинарного файла...")
    
    # Создаем 1MB случайных байт
    data = os.urandom(1024 * 1024)  # 1 MB
    
    with open("test_data/binary_file.bin", "wb") as f:
        f.write(data)
    
    size = os.path.getsize("test_data/binary_file.bin")
    print(f"   Создан файл размером: {size:,} байт")

def create_images():
    """Создаем изображения"""
    print("\n4. Создание изображений...")
    
    width, height = 800, 600
    
    # 4.1 Черно-белое изображение (только черный и белый)
    print("   Создание черно-белого изображения...")
    bw_array = np.random.choice([0, 255], size=(height, width), p=[0.5, 0.5]).astype(np.uint8)
    bw_image = Image.fromarray(bw_array, mode='L')
    bw_image.save("test_data/bw_image.png")
    print(f"      Сохранено: test_data/bw_image.png")
    
    # 4.2 Изображение в оттенках серого
    print("   Создание изображения в оттенках серого...")
    gray_array = np.random.randint(0, 256, size=(height, width), dtype=np.uint8)
    gray_image = Image.fromarray(gray_array, mode='L')
    gray_image.save("test_data/gray_image.png")
    print(f"      Сохранено: test_data/gray_image.png")
    
    # 4.3 Цветное изображение
    print("   Создание цветного изображения...")
    color_array = np.random.randint(0, 256, size=(height, width, 3), dtype=np.uint8)
    color_image = Image.fromarray(color_array, mode='RGB')
    color_image.save("test_data/color_image.jpg")
    color_image.save("test_data/color_image.png")
    print(f"      Сохранено: test_data/color_image.jpg и test_data/color_image.png")

def convert_to_raw():
    """Переводим изображения в raw формат"""
    print("\n5. Конвертация изображений в raw формат...")
    
    images = [
        ("test_data/bw_image.png", "raw_images/bw_image.raw", "bw"),
        ("test_data/gray_image.png", "raw_images/gray_image.raw", "gray"),
        ("test_data/color_image.jpg", "raw_images/color_image.raw", "color")
    ]
    
    results = []
    
    for input_path, output_path, img_type in images:
        print(f"\n   Обработка: {img_type}")
        
        # Открываем изображение
        img = Image.open(input_path)
        
        # Определяем тип и байты на пиксель
        if img_type == "bw":
            # Черно-белое: конвертируем в 1 байт (0 или 255)
            img_gray = img.convert('L')
            pixels = np.array(img_gray)
            type_code = 0  # 0 = черно-белое
            bytes_per_pixel = 1
            pixel_data = pixels.tobytes()
            
        elif img_type == "gray":
            # Оттенки серого: 1 байт на пиксель
            img_gray = img.convert('L')
            pixels = np.array(img_gray)
            type_code = 1  # 1 = оттенки серого
            bytes_per_pixel = 1
            pixel_data = pixels.tobytes()
            
        else:  # color
            # Цветное: 3 байта на пиксель (RGB)
            img_rgb = img.convert('RGB')
            pixels = np.array(img_rgb)
            type_code = 2  # 2 = цветное
            bytes_per_pixel = 3
            pixel_data = pixels.tobytes()
        
        # Создаем raw файл с метаданными
        with open(output_path, 'wb') as f:
            # Метаданные:
            # - тип изображения (1 байт)
            # - ширина (2 байта, big-endian)
            # - высота (2 байта, big-endian)
            f.write(struct.pack('B', type_code))
            f.write(struct.pack('>H', img.width))
            f.write(struct.pack('>H', img.height))
            # Пиксельные данные
            f.write(pixel_data)
        
        # Получаем размеры файлов
        raw_size = os.path.getsize(output_path)
        original_size = os.path.getsize(input_path)
        
        # Теоретический несжатый размер
        theoretical_size = img.width * img.height * bytes_per_pixel + 5  # +5 байт метаданных
        
        results.append({
            'type': img_type,
            'original_path': input_path,
            'original_size': original_size,
            'raw_size': raw_size,
            'theoretical_size': theoretical_size,
            'width': img.width,
            'height': img.height,
            'bytes_per_pixel': bytes_per_pixel
        })
        
        print(f"      Ширина: {img.width}, Высота: {img.height}")
        print(f"      Байт на пиксель: {bytes_per_pixel}")
        print(f"      Теоретический размер RAW: {theoretical_size:,} байт")
        print(f"      Реальный размер RAW: {raw_size:,} байт")
        print(f"      Размер исходного файла: {original_size:,} байт")
    
    return results

def compare_compression_ratios(results):
    """Сравниваем коэффициенты сжатия"""
    print("\n" + "="*60)
    print("СРАВНЕНИЕ КОЭФФИЦИЕНТОВ СЖАТИЯ")
    print("="*60)
    
    for res in results:
        print(f"\n{res['type'].upper()} изображение ({res['width']}x{res['height']}):")
        print("-" * 40)
        
        # RAW файл (несжатый)
        print(f"RAW (несжатый):          {res['raw_size']:,} байт")
        
        # Исходный файл (сжатый)
        print(f"Исходный файл:           {res['original_size']:,} байт")
        
        # Коэффициент сжатия
        compression_ratio = res['raw_size'] / res['original_size']
        print(f"Коэффициент сжатия:      {compression_ratio:.2f}x")
        print(f"(RAW в {compression_ratio:.1f} раз БОЛЬШЕ исходного)")
        
        # Экономия места
        space_saved = res['raw_size'] - res['original_size']
        space_saved_percent = (space_saved / res['raw_size']) * 100
        print(f"Исходный формат экономит: {space_saved:,} байт ({space_saved_percent:.1f}%)")
        
        # Теоретический максимальный коэффициент сжатия
        if res['bytes_per_pixel'] == 1:
            print(f"\nПояснение: RAW хранит каждый пиксель как 1 байт ({res['width']*res['height']:,} байт)")
            print(f"           + 5 байт метаданных")
        else:
            print(f"\nПояснение: RAW хранит каждый пиксель как 3 байта (RGB)")
            print(f"           ({res['width']*res['height']*3:,} байт) + 5 байт метаданных")
        
        print(f"Исходный формат сжимает данные, удаляя избыточность")
        print(f"Наша задача RLE - приблизиться к такому же коэффициенту сжатия")

def print_summary():
    """Выводим итоговую информацию"""
    print("\n" + "="*60)
    print("ИТОГОВАЯ СТРУКТУРА ТЕСТОВЫХ ДАННЫХ")
    print("="*60)
    
    print("\nСозданные файлы:")
    
    files = [
        ("test_data/enwik7.txt", "Английский текст (enwik7)"),
        ("test_data/russian_text.txt", "Русский текст"),
        ("test_data/binary_file.bin", "Бинарный файл"),
        ("test_data/bw_image.png", "Черно-белое изображение"),
        ("test_data/gray_image.png", "Изображение в оттенках серого"),
        ("test_data/color_image.jpg", "Цветное изображение (JPG)"),
        ("test_data/color_image.png", "Цветное изображение (PNG)"),
        ("raw_images/bw_image.raw", "RAW: черно-белое"),
        ("raw_images/gray_image.raw", "RAW: оттенки серого"),
        ("raw_images/color_image.raw", "RAW: цветное")
    ]
    
    for file_path, description in files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"  {description:35} {size:>10,} байт")
        else:
            print(f"  {description:35} {'НЕ НАЙДЕН':>10}")

def main():
    """Главная функция"""
    
    print("НАЧАЛО ПОДГОТОВКИ ТЕСТОВЫХ ДАННЫХ")
    print("="*60)
    
    # Создаем папки
    os.makedirs("test_data", exist_ok=True)
    os.makedirs("raw_images", exist_ok=True)
    
    # 1. Скачиваем enwik7
    download_enwik7()
    
    # 2. Создаем русский текст
    create_russian_text()
    
    # 3. Создаем бинарный файл
    create_binary_file()
    
    # 4. Создаем изображения
    create_images()
    
    # 5. Конвертируем в raw формат и сравниваем
    results = convert_to_raw()
    
    # 6. Сравниваем коэффициенты сжатия
    compare_compression_ratios(results)
    
    # 7. Выводим итоговую информацию
    print_summary()
    
    print("\n" + "="*60)
    print("ГОТОВО! Все тестовые данные созданы.")
    print("Теперь можно приступать к реализации RLE.")

if __name__ == "__main__":
    main()