from PIL import Image
import os
import struct
from datetime import datetime

def convert_and_analyze(image_path, output_path):
   
    img = Image.open(image_path)
    
    filename = os.path.basename(image_path).lower()
    
    if 'bw' in filename or 'black' in filename:
       
        img_gray = img.convert('L')
        pixels = img_gray.tobytes()
        img_type = 0
        type_name = "Черно-белое"
        bytes_per_pixel = 1
        
    elif 'gray' in filename or 'grey' in filename or 'semitones' in filename:
      
        img_gray = img.convert('L')
        pixels = img_gray.tobytes()
        img_type = 1
        type_name = "Оттенки серого"
        bytes_per_pixel = 1
        
    elif 'color' in filename or 'colored' in filename:
        # Цветное
        img_rgb = img.convert('RGB')
        pixels = img_rgb.tobytes()
        img_type = 2
        type_name = "Цветное"
        bytes_per_pixel = 3
        
    else:
        # Автоопределение
        if img.mode == 'RGB':
            pixels = img.tobytes()
            img_type = 2
            type_name = "Цветное"
            bytes_per_pixel = 3
        else:
            img_gray = img.convert('L')
            pixels = img_gray.tobytes()
            unique = set(img_gray.getdata())
            if unique <= {0, 255}:
                img_type = 0
                type_name = "Черно-белое"
            else:
                img_type = 1
                type_name = "Оттенки серого"
            bytes_per_pixel = 1
    
    # Создаем RAW файл
    with open(output_path, 'wb') as f:
        f.write(struct.pack('B', img_type))
        f.write(struct.pack('>H', img.width))
        f.write(struct.pack('>H', img.height))
        f.write(pixels)
    
    # Размеры
    original_size = os.path.getsize(image_path)
    raw_size = os.path.getsize(output_path)
    theoretical_raw = img.width * img.height * bytes_per_pixel + 5
    
    # Коэффициент: во сколько раз RAW больше исходного
    raw_vs_original = raw_size / original_size
    
    print(f"\n{'='*70}")
    print(f"ФАЙЛ: {os.path.basename(image_path)}")
    print(f"{'='*70}")
    print(f"Тип: {type_name}")
    print(f"Размер: {img.width} x {img.height} = {img.width * img.height:,} пикселей")
    print(f"Байт на пиксель: {bytes_per_pixel}")
    print(f"\nРАЗМЕРЫ:")
    print(f"  Исходный ({image_path.split('.')[-1].upper()}): {original_size:>10,} байт ({original_size/1024:.1f} KB)")
    print(f"  RAW файл:                              {raw_size:>10,} байт ({raw_size/1024:.1f} KB)")
    print(f"\nКОЭФФИЦИЕНТЫ:")
    print(f"  RAW БОЛЬШЕ исходного в {raw_vs_original:.2f} раз")
    print(f"  Исходный формат СЖАЛ в {raw_vs_original:.2f} раз лучше")
    
    return {
        'name': os.path.basename(image_path),
        'type': type_name,
        'format': image_path.split('.')[-1].upper(),
        'original_size': original_size,
        'raw_size': raw_size,
        'ratio': raw_vs_original,
        'pixels': img.width * img.height
    }

def main():
    """Главная функция"""
    
    print("\n" + "="*70)
    print("АНАЛИЗ ИЗОБРАЖЕНИЙ ИЗ ПАПКИ test_data")
    print("="*70)
    
    test_data_path = 'C:/Users/dream/PycharmProjects/Alg_l1_2sem/test_data'
   
  
    if not os.path.exists(test_data_path):
        print(f"\nПапка не найдена: {test_data_path}")
        print("Ищу в текущей папке...")
        test_data_path = 'test_data'  
        
        if not os.path.exists(test_data_path):
            print("Папка test_data не найдена!")
            print("Создаю тестовые изображения в текущей папке...")
            create_test_images()
         
            analyze_current_folder()
            return
    
 
    raw_images_path = os.path.join(test_data_path, '..', 'raw_images')
    os.makedirs(raw_images_path, exist_ok=True)
    
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')
    image_files = []
    
    try:
        for file in os.listdir(test_data_path):
            if file.lower().endswith(image_extensions):
                image_files.append(file)
    except Exception as e:
        print(f"Ошибка при чтении папки: {e}")
        return
    
    if not image_files:
        print(f"\nВ папке {test_data_path} нет изображений!")
        print("Создаю тестовые изображения...")
        create_test_images()
        analyze_current_folder()
        return
    
    print(f"\nНайдено изображений: {len(image_files)}")
    
    results = []
    for img_file in image_files:
        img_path = os.path.join(test_data_path, img_file)
        raw_name = img_file.rsplit('.', 1)[0] + '.raw'
        raw_path = os.path.join(raw_images_path, raw_name)
        
        try:
            result = convert_and_analyze(img_path, raw_path)
            results.append(result)
        except Exception as e:
            print(f"Ошибка при обработке {img_file}: {e}")
    
    if results:
        print("\n" + "="*70)
        print("СВОДНАЯ ТАБЛИЦА")
        print("="*70)
        print(f"\n{'Изображение':<25} {'Формат':<6} {'Исходный':>10} {'RAW':>10} {'RAW >':>8} {'Оценка'}")
        print("-" * 70)
        
        for r in results:
            # Оценка
            if r['ratio'] > 20:
                rating = "Отлично!"
            elif r['ratio'] > 10:
                rating = "Хорошо"
            elif r['ratio'] > 5:
                rating = "Средне"
            else:
                rating = "Плохо"
            
            orig_kb = f"{r['original_size']/1024:.1f}KB"
            raw_kb = f"{r['raw_size']/1024:.1f}KB"
            
            print(f"{r['name'][:23]:<25} {r['format']:<6} {orig_kb:>9} {raw_kb:>9} {r['ratio']:>7.1f}x  {rating}")
        
        # Итоги
        print("\n" + "="*70)
        print("ИТОГИ:")
        print("="*70)
        
        total_original = sum(r['original_size'] for r in results)
        total_raw = sum(r['raw_size'] for r in results)
        avg_ratio = total_raw / total_original
        
        print(f"\nВсего изображений: {len(results)}")
        print(f"Суммарный размер исходников: {total_original/1024:.1f} KB")
        print(f"Суммарный размер RAW: {total_raw/1024:.1f} KB")
        print(f"Средний коэффициент: {avg_ratio:.1f}x")
        
        print(f"\nRAW файлы сохранены в: {raw_images_path}")

def analyze_current_folder():
    """Анализирует изображения в текущей папке"""
    
    print("\n" + "="*70)
    print("АНАЛИЗ ИЗОБРАЖЕНИЙ В ТЕКУЩЕЙ ПАПКЕ")
    print("="*70)
    
    os.makedirs("raw_images", exist_ok=True)
    
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
    image_files = [f for f in os.listdir('.') if f.lower().endswith(image_extensions)]
    
    if not image_files:
        print("Нет изображений для анализа!")
        return
    
    results = []
    for img_file in image_files:
        raw_name = img_file.rsplit('.', 1)[0] + '.raw'
        result = convert_and_analyze(img_file, f"raw_images/{raw_name}")
        results.append(result)
    
    # Сводная таблица
    if results:
        print("\n" + "="*70)
        print("СВОДНАЯ ТАБЛИЦА")
        print("="*70)
        print(f"\n{'Изображение':<25} {'Формат':<6} {'Исходный':>10} {'RAW':>10} {'RAW >':>8} {'Оценка'}")
        print("-" * 70)
        
        for r in results:
            if r['ratio'] > 20:
                rating = "Отлично!"
            elif r['ratio'] > 10:
                rating = "Хорошо"
            elif r['ratio'] > 5:
                rating = "Средне"
            else:
                rating = "Плохо"
            
            orig_kb = f"{r['original_size']/1024:.1f}KB"
            raw_kb = f"{r['raw_size']/1024:.1f}KB"
            
            print(f"{r['name'][:23]:<25} {r['format']:<6} {orig_kb:>9} {raw_kb:>9} {r['ratio']:>7.1f}x  {rating}")

def create_test_images():
   
    
    width, height = 800, 600
    
    print("\nСоздание тестовых изображений...")
    
    bw = Image.new('L', (width, height))
    for y in range(height):
        for x in range(width):
            if (x // 20 + y // 20) % 2 == 0:
                bw.putpixel((x, y), 255)
    bw.save("test_bw.png")
    print("  ✓ test_bw.png (черно-белое)")
    
    gray = Image.new('L', (width, height))
    for y in range(height):
        for x in range(width):
            gray.putpixel((x, y), int(x / width * 255))
    gray.save("test_gray.png")
    print("  ✓ test_gray.png (градиент)")
    
  
    color = Image.new('RGB', (width, height))
    for y in range(height):
        for x in range(width):
            color.putpixel((x, y), (
                int(x / width * 255),
                int(y / height * 255),
                int((x+y) / (width+height) * 255)
            ))
    color.save("test_color.png")
    print("  ✓ test_color.png (цветное)")
    
    print("\nТестовые изображения созданы!")

if __name__ == "__main__":
    main()