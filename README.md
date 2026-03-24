# Компрессоры - Проект данных

## Структура проекта

### Основные модули (функциональный, чистый код без комментариев):
- **rle.py** - Run-Length Encoding (кодирование повторений)
- **entropy_coding.py** - Энтропия, Move-To-Front, Huffman, Арифметическое кодирование
- **bwt.py** - Преобразование Барроуза-Уиллера (матричное, блочное)
- **suffix_array_lz.py** - Методы Лемпеля-Зива (LZ77, LZSS, LZ78, LZW)
- **compressors.py** - Базовые классы компрессоров

### Тестирование:
- **test_simple.py** - Базовые тесты всех алгоритмов

### Директории данных:
- **test_data/** - Исходные тестовые файлы
- **raw_images/** - Изображения в RAW формате

## Главные классы

### RLE (rle.py)
```python
RLECompressor(Ms, Mc) - для кодирования с параметрами
RLEFileHandler() - для работы с файлами
```

### Энтропийное кодирование (entropy_coding.py)
```python
calculate_entropy(data, Ms) - расчет энтропии
MTFTransform.encode/decode() - Move-To-Front трансформация
HuffmanCoding.encode/decode() - Кодирование Huffman
CanonicalHuffman.build_from_lengths() - Канонические коды
ArithmeticCoding.encode() - Арифметическое кодирование
```

### BWT (bwt.py)
```python
BWT.forward_matrix() - прямое преобразование (матрица)
BWT.inverse_matrix() - обратное преобразование (матрица)
BWT.inverse_permutation() - обратное преобразование (перестановка)
BlockBWT(block_size) - блочная обработка больших файлов
SuffixArrayBWT - использование суффиксных массивов
```

### LZ алгоритмы (suffix_array_lz.py)
```python
LZ77.encode/decode(window_size, lookahead_size)
LZSS.encode/decode(window_size, lookahead_size)
LZ78.encode/decode(max_dict_size)
LZW.encode/decode(max_code_bits)
```

### Компрессоры (compressors.py)
```python
RLECompressor_Standalone - RLE
HuffmanCompressor - Huffman
BWTRLECompressor - BWT + RLE
LZSSCompressor - LZSS
LZWCompressor - LZW
```

## Запуск

### Все тесты:
```bash
python test_simple.py
```

### Информация о проекте:
```bash
python main.py
```

## Примеры использования

### RLE
```python
from rle import RLECompressor
comp = RLECompressor(Ms=1, Mc=1)
compressed = comp.encode(data)
decompressed = comp.decode(compressed)
```

### Huffman
```python
from entropy_coding import HuffmanCoding
bits, codes, freqs = HuffmanCoding.encode(data)
decoded = HuffmanCoding.decode(bits, codes)
```

### BWT
```python
from bwt import BWT
bwt_data, idx = BWT.forward_matrix(data)
recovered = BWT.inverse_permutation(bwt_data, idx)
```

### LZW
```python
from suffix_array_lz import LZW
compressed = LZW.encode(data)
decompressed = LZW.decode(compressed)
```

## Примечания

- Весь код без комментариев и docstrings - только функциональный код
- Все алгоритмы протестированы и работают корректно
- Модули готовы к использованию в Задании 1-4
