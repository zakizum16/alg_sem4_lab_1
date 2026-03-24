import struct
import os
from typing import Tuple

class RLECompressor:
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
                current_symbol = data[i:i+self.Ms]
                run_len = 1
                
                while (i + (run_len + 1) * self.Ms <= n and 
                       data[i + run_len * self.Ms:i + (run_len + 1) * self.Ms] == current_symbol and
                       run_len < self.max_run):
                    run_len += 1
                
                if run_len > 1:
                    result.extend(self._encode_length(run_len, is_non_run=False))
                    result.extend(current_symbol)
                    i += run_len * self.Ms
                    continue
            
            non_run_len = 0
            while i + (non_run_len + 1) * self.Ms <= n and non_run_len < self.max_run:
                next_pos = i + non_run_len * self.Ms
                next_symbol = data[next_pos:next_pos+self.Ms]
                
                next_run = 1
                while (next_pos + (next_run + 1) * self.Ms <= n and
                       data[next_pos + next_run * self.Ms:next_pos + (next_run + 1) * self.Ms] == next_symbol and
                       next_run < self.max_run):
                    next_run += 1
                
                if next_run >= 2 and non_run_len > 0:
                    break
                
                if non_run_len == 0 and i + self.Ms <= n:
                    next_next = i + self.Ms
                    if next_next + self.Ms <= n:
                        if data[next_next:next_next+self.Ms] == next_symbol:
                            break
                
                non_run_len += 1
            
            if non_run_len > 0:
                result.extend(self._encode_length(non_run_len, is_non_run=True))
                for j in range(non_run_len):
                    result.extend(data[i + j * self.Ms:i + (j + 1) * self.Ms])
                i += non_run_len * self.Ms
            else:
                result.extend(self._encode_length(1, is_non_run=True))
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


class RLEFileHandler:
    """Работа с файлами RLE"""
    
    def __init__(self, Ms: int = 1, Mc: int = 1, output_dir: str = "rlecoding"):
        self.Ms = Ms
        self.Mc = Mc
        self.compressor = RLECompressor(Ms, Mc)
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def compress_file(self, input_path: str) -> Tuple[int, int, str]:
        """Сжатие файла, сохраняет в папку rlecoding"""
        with open(input_path, 'rb') as f:
            data = f.read()
        
        compressed = self.compressor.encode(data)
        
        # Сохраняем в папку rlecoding
        base_name = os.path.basename(input_path)
        output_path = os.path.join(self.output_dir, base_name + '.rle')
        
        with open(output_path, 'wb') as f:
            f.write(struct.pack('BB', self.Ms, self.Mc))
            f.write(struct.pack('>I', len(data)))
            f.write(compressed)
        
        return len(data), len(compressed), output_path
    
    def decompress_file(self, input_path: str, output_path: str = None) -> Tuple[int, int, str]:
        """Распаковка файла"""
        with open(input_path, 'rb') as f:
            Ms, Mc = struct.unpack('BB', f.read(2))
            original_size = struct.unpack('>I', f.read(4))[0]
            compressed_data = f.read()
        
        compressor = RLECompressor(Ms, Mc)
        decompressed = compressor.decode(compressed_data)
        
        if output_path is None:
            base_name = os.path.basename(input_path).replace('.rle', '')
            output_path = os.path.join(self.output_dir, base_name + '.decoded')
        
        with open(output_path, 'wb') as f:
            f.write(decompressed)
        
        return original_size, len(compressed_data), output_path


def test_rle_basic():
    print("\n" + "="*70)
    print("ТЕСТ 1: БАЗОВАЯ ФУНКЦИОНАЛЬНОСТЬ RLE")
    print("="*70)
    
    compressor = RLECompressor(Ms=1, Mc=1)
    
    test_cases = [
        (b'\xcf\xcf\xcf\xcf\xcf', "5 повторов"),
        (b'\xcf\xce\xcf\xce\xcf', "чередование"),
        (b'\xcf\xce\xcf\xce\xcf\xcf\xcf\xcf\xcf\xcf', "смешанная"),
    ]
    
    for data, desc in test_cases:
        encoded = compressor.encode(data)
        decoded = compressor.decode(encoded)
        
        print(f"\n{desc}:")
        print(f"  Исходные: {data.hex().upper()}")
        print(f"  Сжатые:   {encoded.hex().upper()}")
        print(f"  Результат: {'OK' if data == decoded else 'FAIL'}")


def test_rle_with_Ms():
    print("\n" + "="*70)
    print("ТЕСТ 2: RLE С РАЗНЫМИ Ms")
    print("="*70)
    
    compressor = RLECompressor(Ms=2, Mc=1)
    data = bytes.fromhex('CF CE CF CE CF CE')
    encoded = compressor.encode(data)
    decoded = compressor.decode(encoded)
    
    print(f"\nMs=2, данные: {data.hex().upper()}")
    print(f"  Сжатые: {encoded.hex().upper()}")
    print(f"  Результат: {'OK' if data == decoded else 'FAIL'}")
    
    compressor = RLECompressor(Ms=3, Mc=1)
    data = bytes.fromhex('CF CE CF CF CE CF')
    encoded = compressor.encode(data)
    decoded = compressor.decode(encoded)
    
    print(f"\nMs=3, данные: {data.hex().upper()}")
    print(f"  Сжатые: {encoded.hex().upper()}")
    print(f"  Результат: {'OK' if data == decoded else 'FAIL'}")


def test_utf8_problem():
    print("\n" + "="*70)
    print("ТЕСТ 3: ПРОБЛЕМА UTF-8")
    print("="*70)
    
    text = "Привет мир! Это текст на русском языке."
    utf8_data = text.encode('utf-8')
    
    print(f"\nИсходный текст: {text}")
    
    # Решение: RLE на уровне символов Unicode
    codepoints = [ord(c) for c in text]
    char_data = b''.join(cp.to_bytes(4, byteorder='big') for cp in codepoints)
    
    compressor_char = RLECompressor(Ms=4, Mc=2)
    compressed_char = compressor_char.encode(char_data)
    decompressed_char = compressor_char.decode(compressed_char)
    
    recovered_codepoints = []
    for i in range(0, len(decompressed_char), 4):
        cp = int.from_bytes(decompressed_char[i:i+4], byteorder='big')
        recovered_codepoints.append(cp)
    recovered_text = ''.join(chr(cp) for cp in recovered_codepoints)
    
    print(f"\nRLE на символах (Ms=4):")
    print(f"  Исходный UTF-8: {len(utf8_data)} байт")
    print(f"  Символьное предст: {len(char_data)} байт")
    print(f"  Сжатый: {len(compressed_char)} байт")
    print(f"  Результат: {'OK' if text == recovered_text else 'FAIL'}")
    
    return utf8_data, char_data, compressed_char


def compress_all_files():
    """Сжатие всех тестовых файлов, сохранение в папку rlecoding"""
    print("\n" + "="*70)
    print("СЖАТИЕ ВСЕХ ТЕСТОВЫХ ФАЙЛОВ -> ПАПКА rlecoding")
    print("="*70)
    
    # Создаем папку rlecoding
    os.makedirs("rlecoding", exist_ok=True)
    
    test_files = []
    
    # Ищем файлы в test_data
    if os.path.exists('test_data'):
        for f in os.listdir('test_data'):
            full_path = os.path.join('test_data', f)
            if os.path.isfile(full_path):
                test_files.append(full_path)
    
    # Ищем raw файлы
    if os.path.exists('raw_images'):
        for f in os.listdir('raw_images'):
            if f.endswith('.raw'):
                test_files.append(os.path.join('raw_images', f))
    
    # Добавляем дополнительные файлы
    extra_files = ['test_data/russian_text.txt', 'test_data/enwik7.txt', 'test_data/binary_file.bin']
    for f in extra_files:
        if os.path.exists(f):
            test_files.append(f)
    
    if not test_files:
        print("Нет файлов для сжатия!")
        return []
    
    results = []
    
    for file_path in test_files:
        # Определяем Ms по типу файла
        if 'color' in file_path.lower():
            Ms = 3
        elif 'bw' in file_path.lower() or 'gray' in file_path.lower():
            Ms = 1
        else:
            Ms = 1
        
        Mc = 1
        
        print(f"\n{file_path}:")
        
        handler = RLEFileHandler(Ms=Ms, Mc=Mc, output_dir="rlecoding")
        
        # Сжатие
        original_size, compressed_size, compressed_path = handler.compress_file(file_path)
        
        # Распаковка
        decompressed_size, _, decompressed_path = handler.decompress_file(compressed_path)
        
        # Проверка
        with open(file_path, 'rb') as f1, open(decompressed_path, 'rb') as f2:
            original = f1.read()
            decompressed = f2.read()
            success = original == decompressed
        
        ratio = original_size / compressed_size if compressed_size > 0 else 1
        
        results.append({
            'file': os.path.basename(file_path),
            'path': file_path,
            'Ms': Ms,
            'original': original_size,
            'compressed': compressed_size,
            'ratio': ratio,
            'success': success,
            'compressed_path': compressed_path,
            'decompressed_path': decompressed_path
        })
        
        print(f"  Ms={Ms}, Mc={Mc}")
        print(f"  Исходный: {original_size:,} байт")
        print(f"  Сжатый:   {compressed_size:,} байт ({compressed_path})")
        print(f"  Коэф-т:   {ratio:.2f}x")
        print(f"  Результат: {'OK' if success else 'FAIL'}")
    
    return results


def analyze_rle_efficiency(results):
    """Анализ эффективности RLE"""
    print("\n" + "="*70)
    print("АНАЛИЗ ЭФФЕКТИВНОСТИ RLE")
    print("="*70)
    
    print("\n1. Оптимальные параметры Ms:")
    print("   - Черно-белое/серое изображение: Ms = 1 (1 байт/пиксель)")
    print("   - Цветное изображение: Ms = 3 (RGB пиксель)")
    print("   - Текст UTF-8: Ms = 1 (побайтово) или Ms = 4 (посимвольно)")
    
    print("\n2. Выбор Mc:")
    print("   - Mc = 1: макс. длина 127 повторов (достаточно для большинства)")
    print("   - Mc = 2: макс. длина 32767 повторов (для больших областей)")
    
    print("\n3. Проблема UTF-8:")
    print("   - Побайтовое сжатие может разорвать многобайтовые символы")
    print("   - Решение: Ms = 4 (4 байта на символ) и работа с кодовыми точками")
    
    print("\n4. Результаты сжатия:")
    print("-"*70)
    print(f"{'Файл':<35} {'Ms':<4} {'Исходный':>12} {'Сжатый':>12} {'Коэф.':>8}")
    print("-"*70)
    
    for r in results:
        orig_kb = f"{r['original']/1024:.1f}KB"
        comp_kb = f"{r['compressed']/1024:.1f}KB"
        print(f"{r['file'][:33]:<35} {r['Ms']:<4} {orig_kb:>11} {comp_kb:>11} {r['ratio']:>7.2f}x")
    
    print("\n5. Оценка:")
    for r in results:
        if r['ratio'] > 2:
            print(f"   [GOOD] {r['file']}: {r['ratio']:.2f}x - хорошее сжатие")
        elif r['ratio'] > 1:
            print(f"   [MEDIUM] {r['file']}: {r['ratio']:.2f}x - среднее сжатие")
        else:
            print(f"   [POOR] {r['file']}: {r['ratio']:.2f}x - плохое сжатие (данные случайные)")


def main():
    print("\n" + "="*70)
    print("RLE КОМПРЕССОР")
    print("="*70)
    
    # Тест базовой функциональности
    test_rle_basic()
    
    # Тест с разными Ms
    test_rle_with_Ms()
    
    # Тест UTF-8
    test_utf8_problem()
    
    # Сжатие всех файлов (сохраняем в rlecoding)
    results = compress_all_files()
    
    # Анализ
    if results:
        analyze_rle_efficiency(results)
        
        print("\n" + "="*70)
        print("ФАЙЛЫ СОХРАНЕНЫ В ПАПКЕ: rlecoding/")
        print("="*70)
        print("\nСодержимое папки rlecoding:")
        for f in os.listdir("rlecoding"):
            size = os.path.getsize(os.path.join("rlecoding", f))
            print(f"  {f:<40} {size:>10,} байт")
    
    print("\n" + "="*70)
    print("ГОТОВО!")
    print("="*70)


if __name__ == "__main__":
    main()