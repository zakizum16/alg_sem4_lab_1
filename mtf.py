"""
Move-To-Front трансформация
"""


class MTFTransform:
    """Move-To-Front трансформация для предварительной обработки данных"""
    
    @staticmethod
    def encode(data: bytes) -> bytes:
        """
        Кодировать данные MTF преобразованием.
        
        Каждый байт заменяется на его позицию в текущем алфавите,
        а затем этот элемент перемещается в начало.
        """
        alphabet = list(range(256))
        result = bytearray()
        for byte in data:
            index = alphabet.index(byte)
            result.append(index)
            alphabet.pop(index)
            alphabet.insert(0, byte)
        return bytes(result)

    @staticmethod
    def decode(data: bytes) -> bytes:
        """Декодировать данные MTF преобразованием"""
        alphabet = list(range(256))
        result = bytearray()
        for index in data:
            byte = alphabet[index]
            result.append(byte)
            alphabet.pop(index)
            alphabet.insert(0, byte)
        return bytes(result)
