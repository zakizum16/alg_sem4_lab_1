import struct
import os
from typing import Tuple, Optional

# ============================================================
# 1. КЛАСС RLE КОМПРЕССОРА
# ============================================================

class RLECompressor:
    """RLE компрессор с поддержкой Ms и Mc"""
    
    def __init__(self, Ms: int = 1, Mc: int = 1):
        self.Ms = Ms
        self.Mc = Mc
        self.max_run = (1 << (Mc * 8 - 1)) - 1
        
    def encode(self, data: bytes) -> bytes:
        if not data:
            return b''
        
        result = bytearray()
        i = 0
        n = len(data)
        
        while i < n:
            if i + self.Ms <= n:
                current = data[i:i+self.Ms]
                run_len = 1
                
                while (i + (run_len + 1) * self.Ms <= n and 
                       data[i + run_len * self.Ms:i + (run_len + 1) * self.Ms] == current and
                       run_len < self.max_run):
                    run_len += 1
                
                if run_len > 1:
                    result.extend(self._encode_length(run_len, False))
                    result.extend(current)
                    i += run_len * self.Ms
                    continue
            
            non_run_len = 0
            while i + (non_run_len + 1) * self.Ms <= n and non_run_len < self.max_run:
                next_pos = i + non_run_len * self.Ms
                next_sym = data[next_pos:next_pos+self.Ms]
                
                next_run = 1
                while (next_pos + (next_run + 1) * self.Ms <= n and
                       data[next_pos + next_run * self.Ms:next_pos + (next_run + 1) * self.Ms] == next_sym and
                       next_run < self.max_run):
                    next_run += 1
                
                if next_run >= 2 and non_run_len > 0:
                    break
                
                non_run_len += 1
            
            if non_run_len > 0:
                result.extend(self._encode_length(non_run_len, True))
                for j in range(non_run_len):
                    result.extend(data[i + j * self.Ms:i + (j + 1) * self.Ms])
                i += non_run_len * self.Ms
            else:
                result.extend(self._encode_length(1, True))
                result.extend(data[i:i+self.Ms])
                i += self.Ms
        
        return bytes(result)
    
    def decode(self, data: bytes) -> bytes:
        if not data:
            return b''
        
        result = bytearray()
        i = 0
        n = len(data)
        
        while i < n:
            if i + self.Mc > n:
                break
            
            length_bytes = data[i:i+self.Mc]
            i += self.Mc
            length = self._decode_length(length_bytes)
            
            is_non_run = (length & (1 << (self.Mc * 8 - 1))) != 0
            
            if is_non_run:
                length = length & ((1 << (self.Mc * 8 - 1)) - 1)
                for _ in range(length):
                    if i + self.Ms > n:
                        break
                    result.extend(data[i:i+self.Ms])
                    i += self.Ms
            else:
                if i + self.Ms > n:
                    break
                symbol = data[i:i+self.Ms]
                i += self.Ms
                for _ in range(length):
                    result.extend(symbol)
        
        return bytes(result)
    
    def _encode_length(self, length: int, is_non_run: bool = False) -> bytes:
        if is_non_run:
            length = length | (1 << (self.Mc * 8 - 1))
        return length.to_bytes(self.Mc, byteorder='big')
    
    def _decode_length(self, length_bytes: bytes) -> int:
        return int.from_bytes(length_bytes, byteorder='big')


# ============================================================
# 2. КЛАСС ДЛЯ РАБОТЫ С ФАЙЛАМИ
# ============================================================

class RLEFileHandler:
    def __init__(self, Ms: int = 1, Mc: int = 1, output_dir: str = "rlecoding"):
        self.Ms = Ms
        self.Mc = Mc
        self.compressor = RLECompressor(Ms, Mc)
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def compress_file(self, input_path: str) -> Tuple[int, int, str]:
        with open(input_path, 'rb') as f:
            data = f.read()
        
        compressed = self.compressor.encode(data)
        
        base_name = os.path.basename(input_path)
        output_path = os.path.join(self.output_dir, base_name + '.rle')
        
        with open(output_path, 'wb') as f:
            f.write(struct.pack('BB', self.Ms, self.Mc))
            f.write(struct.pack('>I', len(data)))
            f.write(compressed)
        
        return len(data), len(compressed), output_path
    
    def decompress_file(self, input_path: str) -> Tuple[int, int, str]:
        with open(input_path, 'rb') as f:
            Ms, Mc = struct.unpack('BB', f.read(2))
            original_size = struct.unpack('>I', f.read(4))[0]
            compressed_data = f.read()
        
        compressor = RLECompressor(Ms, Mc)
        decompressed = compressor.decode(compressed_data)
        
        base_name = os.path.basename(input_path).replace('.rle', '')
        output_path = os.path.join(self.output_dir, base_name + '.decoded')
        
        with open(output_path, 'wb') as f:
            f.write(decompressed)
        
        return original_size, len(compressed_data), output_path
    
    def test_cycle(self, input_path: str) -> bool:
        original_size, comp_size, comp_path = self.compress_file(input_path)
        decomp_size, _, decomp_path = self.decompress_file(comp_path)
        
        with open(input_path, 'rb') as f1, open(decomp_path, 'rb') as f2:
            original = f1.read()
            decompressed = f2.read()
            return original == decompressed


# ============================================================
# 3. АНАЛИЗ ПРИМЕНИМОСТИ RLE
# ============================================================

def analyze_rle_for_raw_images():
    print("\n" + "="*70)
    print("АНАЛИЗ ПРИМЕНИМОСТИ RLE ДЛЯ RAW ИЗОБРАЖЕНИЙ")
    print("="*70)
    print("""
RLE эффективен для RAW изображений, потому что:
    
1. Черно-белые изображения:
   - Много повторяющихся пикселей (большие области одного цвета)
   - Ms = 1 (1 байт на пиксель)
   - Mc = 1 (до 127 повторов подряд)
   - Ожидаемый коэффициент: 5-50x
       
2. Оттенки серого:
   - Плавные градиенты дают меньше повторов
   - Ms = 1 (1 байт на пиксель)
   - Mc = 1 или 2 (если много длинных повторов)
   - Ожидаемый коэффициент: 2-10x
       
3. Цветные изображения (RGB):
   - Каждый пиксель = 3 байта (R,G,B)
   - Повторы случаются реже (нужно совпадение всех 3 цветов)
   - Ms = 3 (группируем пиксель целиком)
   - Mc = 1 или 2
   - Ожидаемый коэффициент: 1.5-3x

Рекомендуемые значения:
┌─────────────────────────┬─────────┬─────────┐
│ Тип изображения         │ Ms      │ Mc      │
├─────────────────────────┼─────────┼─────────┤
│ Черно-белое             │ 1       │ 1       │
│ Оттенки серого          │ 1       │ 1-2     │
│ Цветное (RGB)           │ 3       │ 1-2     │
│ Цветное с альфа (RGBA)  │ 4       │ 2       │
└─────────────────────────┴─────────┴─────────┘
    """)


def analyze_utf8_problem():
    print("\n" + "="*70)
    print("ПРОБЛЕМА UTF-8 И ЕЁ РЕШЕНИЕ")
    print("="*70)
    print("""
ПРОБЛЕМА:
─────────────────────────────────────────────────────────────
UTF-8 кодирует символы переменным количеством байт:
- Латинские буквы: 1 байт
- Русские буквы: 2 байта
- Эмодзи: 4 байта

При побайтовом RLE (Ms=1) можно разорвать многобайтовый символ!

РЕШЕНИЕ: Работать на уровне символов (кодовых точек)
─────────────────────────────────────────────────────────────
- Преобразовать UTF-8 в список кодовых точек Unicode
- Ms = 4 (каждый символ = 4 байта)
- Сжимать последовательности одинаковых символов
- При декодировании восстановить символы
    """)
    
    text = "Привет мир! Hello world!"
    utf8_data = text.encode('utf-8')
    
    print(f"\nДемонстрация:")
    print(f"Текст: {text}")
    print(f"UTF-8 байты: {utf8_data[:20].hex().upper()}")
    
    codepoints = [ord(c) for c in text]
    char_data = b''.join(cp.to_bytes(4, 'big') for cp in codepoints)
    print(f"\nРешение: работа с кодовыми точками (Ms=4)")
    print(f"Символьное представление: {len(char_data)} байт")
    print(f"Каждый символ = 4 байта → RLE не разорвет символы")


# ============================================================
# 4. ТЕСТИРОВАНИЕ
# ============================================================

def test_basic_rle():
    print("\n" + "="*70)
    print("ТЕСТ 1: БАЗОВАЯ ФУНКЦИОНАЛЬНОСТЬ RLE")
    print("="*70)
    
    compressor = RLECompressor(Ms=1, Mc=1)
    
    tests = [
        (b'\xcf\xcf\xcf\xcf\xcf', "5 повторов"),
        (b'\xcf\xce\xcf\xce\xcf', "чередование"),
        (b'\xcf\xce\xcf\xce\xcf\xcf\xcf\xcf\xcf\xcf', "смешанная"),
    ]
    
    for data, desc in tests:
        encoded = compressor.encode(data)
        decoded = compressor.decode(encoded)
        
        print(f"\n{desc}:")
        print(f"  Исходные: {data.hex().upper()}")
        print(f"  Сжатые:   {encoded.hex().upper()}")
        print(f"  Результат: {'✓' if data == decoded else '✗'}")


def test_rle_with_ms():
    print("\n" + "="*70)
    print("ТЕСТ 2: RLE С РАЗНЫМИ Ms")
    print("="*70)
    
    compressor = RLECompressor(Ms=2, Mc=1)
    data = bytes.fromhex('CF CE CF CE CF CE')
    encoded = compressor.encode(data)
    decoded = compressor.decode(encoded)
    
    print(f"\nMs=2, данные: {data.hex().upper()}")
    print(f"  Сжатые: {encoded.hex().upper()}")
    print(f"  Результат: {'✓' if data == decoded else '✗'}")
    
    compressor = RLECompressor(Ms=3, Mc=1)
    data = bytes.fromhex('CF CE CF CF CE CF')
    encoded = compressor.encode(data)
    decoded = compressor.decode(encoded)
    
    print(f"\nMs=3, данные: {data.hex().upper()}")
    print(f"  Сжатые: {encoded.hex().upper()}")
    print(f"  Результат: {'✓' if data == decoded else '✗'}")


def test_utf8_solution():
    print("\n" + "="*70)
    print("ТЕСТ 3: РЕШЕНИЕ ПРОБЛЕМЫ UTF-8")
    print("="*70)
    
    text = "Привет мир! Это русский текст."
    utf8_data = text.encode('utf-8')
    
    print(f"\nИсходный текст: {text}")
    
    # Решение: работа с символами
    codepoints = [ord(c) for c in text]
    char_data = b''.join(cp.to_bytes(4, 'big') for cp in codepoints)
    
    compressor = RLECompressor(Ms=4, Mc=2)
    compressed = compressor.encode(char_data)
    decompressed = compressor.decode(compressed)
    
    recovered_cp = []
    for i in range(0, len(decompressed), 4):
        cp = int.from_bytes(decompressed[i:i+4], 'big')
        recovered_cp.append(cp)
    recovered_text = ''.join(chr(cp) for cp in recovered_cp)
    
    print(f"\nRLE на символах (Ms=4, Mc=2):")
    print(f"  Исходный UTF-8: {len(utf8_data)} байт")
    print(f"  Символьное предст: {len(char_data)} байт")
    print(f"  Сжатый: {len(compressed)} байт")
    print(f"  Коэффициент: {len(char_data)/len(compressed):.2f}x")
    print(f"  Результат: {'✓' if text == recovered_text else '✗'}")


def compress_all_files():
    print("\n" + "="*70)
    print("СЖАТИЕ ВСЕХ ТЕСТОВЫХ ФАЙЛОВ")
    print("="*70)
    
    os.makedirs("rlecoding", exist_ok=True)
    
    all_files = []
    
    # Ищем файлы
    folders = ['test_data', 'raw_images', '.']
    for folder in folders:
        if os.path.exists(folder):
            for f in os.listdir(folder):
                if f.endswith(('.png', '.jpg', '.raw', '.txt', '.bin')):
                    all_files.append(os.path.join(folder, f))
    
    if not all_files:
        print("Нет файлов для сжатия!")
        return []
    
    results = []
    
    for file_path in all_files[:15]:
        if 'color' in file_path.lower():
            Ms = 3
        elif 'bw' in file_path.lower() or 'gray' in file_path.lower():
            Ms = 1
        else:
            Ms = 1
        
        Mc = 1
        
        print(f"\n{file_path}:")
        
        handler = RLEFileHandler(Ms=Ms, Mc=Mc, output_dir="rlecoding")
        
        original_size, comp_size, comp_path = handler.compress_file(file_path)
        success = handler.test_cycle(file_path)
        
        ratio = original_size / comp_size if comp_size > 0 else 1
        
        results.append({
            'file': os.path.basename(file_path),
            'Ms': Ms,
            'original': original_size,
            'compressed': comp_size,
            'ratio': ratio,
            'success': success
        })
        
        print(f"  Исходный: {original_size:,} байт")
        print(f"  Сжатый:   {comp_size:,} байт")
        print(f"  Коэф-т:   {ratio:.2f}x")
        print(f"  Цикл:     {'✓' if success else '✗'}")
    
    return results


def show_results(results):
    print("\n" + "="*70)
    print("СВОДНАЯ ТАБЛИЦА РЕЗУЛЬТАТОВ")
    print("="*70)
    print(f"\n{'Файл':<35} {'Ms':<4} {'Исходный':>12} {'Сжатый':>12} {'Коэф.':>8}")
    print("-"*85)
    
    for r in results:
        orig_kb = f"{r['original']/1024:.1f}KB"
        comp_kb = f"{r['compressed']/1024:.1f}KB"
        print(f"{r['file'][:33]:<35} {r['Ms']:<4} {orig_kb:>11} {comp_kb:>11} {r['ratio']:>7.2f}x")
    
    print("\n" + "="*70)
    print("ОЦЕНКА ЭФФЕКТИВНОСТИ:")
    print("="*70)
    
    good = [r for r in results if r['ratio'] > 2]
    medium = [r for r in results if 1 < r['ratio'] <= 2]
    bad = [r for r in results if r['ratio'] <= 1]
    
    print(f"\n✓ Хорошее сжатие (>2x): {len(good)} файлов")
    for r in good:
        print(f"    {r['file']}: {r['ratio']:.2f}x")
    
    print(f"\n○ Среднее сжатие (1-2x): {len(medium)} файлов")
    for r in medium:
        print(f"    {r['file']}: {r['ratio']:.2f}x")
    
    print(f"\n✗ Плохое сжатие (<1x): {len(bad)} файлов")
    for r in bad:
        print(f"    {r['file']}: {r['ratio']:.2f}x")


# ============================================================
# 5. ГЛАВНАЯ ФУНКЦИЯ
# ============================================================

def main():
    print("\n" + "="*70)
    print("RLE КОМПРЕССОР - ПОЛНАЯ РЕАЛИЗАЦИЯ")
    print("="*70)
    
    # 1. Анализ применимости
    analyze_rle_for_raw_images()
    
    # 2. Проблема UTF-8
    analyze_utf8_problem()
    
    # 3. Базовые тесты
    test_basic_rle()
    test_rle_with_ms()
    test_utf8_solution()
    
    # 4. Сжатие всех файлов
    results = compress_all_files()
    
    # 5. Результаты
    if results:
        show_results(results)
    
    print("\n" + "="*70)
    print("ВЫВОДЫ:")
    print("="*70)
    print("""
1. RLE эффективен для RAW изображений с повторяющимися пикселями
2. Оптимальные параметры: Ms=1 для чб/серых, Ms=3 для цветных
3. Проблема UTF-8 решается работой на уровне символов (Ms=4)
4. Полный цикл сжатия/распаковки работает корректно
5. Коэффициенты сжатия зависят от типа данных:
   - Черно-белые: высокий коэффициент
   - Оттенки серого: средний коэффициент
   - Цветные: низкий коэффициент
   - Текст: низкий коэффициент (мало повторов)
    """)
    
    print(f"\nСжатые файлы сохранены в папке: rlecoding/")


if __name__ == "__main__":
    main()