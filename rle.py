import struct
import os
import time
from typing import Tuple
from base import Compressor

class RLECompressor(Compressor):
    def __init__(self, Ms: int = 1, Mc: int = 1):
        super().__init__(f"RLE(Ms={Ms},Mc={Mc})")
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
    
    def compress(self, data: bytes) -> bytes:
        self.original_size = len(data)
        start = time.time()
        compressed = self.encode(data)
        self.encode_time = time.time() - start
        self.compressed_size = len(compressed)
        return compressed
    
    def decompress(self, data: bytes) -> bytes:
        start = time.time()
        decompressed = self.decode(data)
        self.decode_time = time.time() - start
        return decompressed
    
    def _encode_length(self, length: int, is_non_run: bool = False) -> bytes:
        if is_non_run:
            length = length | (1 << (self.Mc * 8 - 1))
        return length.to_bytes(self.Mc, byteorder='big')
    
    def _decode_length(self, length_bytes: bytes) -> int:
        return int.from_bytes(length_bytes, byteorder='big')


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
    
    def decompress_file(self, input_path: str, output_path: str = None) -> Tuple[int, int, str]:
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


def get_available_files():
    """Получить список доступных файлов из raw_images и test_data"""
    files = {}
    counter = 1
    
    # Файлы из test_data
    if os.path.exists('test_data'):
        for f in sorted(os.listdir('test_data')):
            full_path = os.path.join('test_data', f)
            if os.path.isfile(full_path):
                files[counter] = full_path
                counter += 1
    
    # Файлы из raw_images
    if os.path.exists('raw_images'):
        for f in sorted(os.listdir('raw_images')):
            full_path = os.path.join('raw_images', f)
            if os.path.isfile(full_path):
                files[counter] = full_path
                counter += 1
    
    return files


def select_file():
    """Интерактивный выбор файла для сжатия"""
    files = get_available_files()
    
    if not files:
        print("\n[ERR] Нет файлов в папках test_data и raw_images")
        return None
    
    print("\n" + "="*70)
    print("ДОСТУПНЫЕ ФАЙЛЫ")
    print("="*70)
    
    for idx, path in sorted(files.items()):
        size = os.path.getsize(path)
        print(f"{idx:2}. {path:<50} ({size:>10,} байт)")
    
    while True:
        try:
            choice = int(input("\nВыберите номер файла (или 0 для выхода): "))
            if choice == 0:
                return None
            if choice in files:
                return files[choice]
            else:
                print("[ERR] Неверный номер. Попробуйте снова.")
        except ValueError:
            print("[ERR] Введите число.")


def determine_ms(file_path: str) -> int:
    """Определить оптимальный Ms для файла"""
    name_lower = os.path.basename(file_path).lower()
    
    if 'color' in name_lower:
        return 3  # RGB
    elif 'bw' in name_lower or 'gray' in name_lower:
        return 1  # BW
    else:
        return 1  # Default


def main():
    """RLE компрессор - выбор файла и сжатие"""
    print("\n" + "="*70)
    print("RLE КОМПРЕССОР")
    print("="*70)
    
    # Выбор файла
    file_path = select_file()
    if not file_path:
        print("Выход.")
        return
    
    # Определяем Ms
    Ms = determine_ms(file_path)
    Mc = 1
    
    print("\n" + "="*70)
    print(f"СЖАТИЕ: {file_path}")
    print("="*70)
    
    # Создаем обработчик
    handler = RLEFileHandler(Ms=Ms, Mc=Mc, output_dir="rlecoding")
    
    # Сжатие
    print(f"\nПараметры: Ms={Ms}, Mc={Mc}")
    print("Сжатие...")
    original_size, compressed_size, compressed_path = handler.compress_file(file_path)
    ratio = original_size / compressed_size if compressed_size > 0 else 1
    
    print(f"  Исходный размер:  {original_size:>12,} байт")
    print(f"  Сжатый размер:    {compressed_size:>12,} байт")
    print(f"  Коэффициент:      {ratio:>23.2f}x")
    print(f"  Сохранено в:      {compressed_path}")
    
    # Распаковка
    print("\nРаспаковка...")
    decompressed_size, _, decompressed_path = handler.decompress_file(compressed_path)
    
    # Проверка корректности
    with open(file_path, 'rb') as f1, open(decompressed_path, 'rb') as f2:
        original = f1.read()
        decompressed = f2.read()
        is_correct = original == decompressed
    
    status = "[OK]" if is_correct else "[ERR]"
    print(f"  Статус проверки:  {status} (данные совпадают)" if is_correct else f"  Статус проверки:  {status} (НЕСОВПАДЕНИЕ ДАННЫХ!)")
    print(f"  Сохранено в:      {decompressed_path}")
    
    print("\n" + "="*70)
    print("ГОТОВО!")
    print("="*70)


if __name__ == "__main__":
    main()

