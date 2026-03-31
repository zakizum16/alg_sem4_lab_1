from PIL import Image
import os
import struct

def convert_and_analyze(image_path, output_path):
    img = Image.open(image_path)
    filename = os.path.basename(image_path).lower()
    
    if 'bw' in filename or 'black' in filename:
        img_gray = img.convert('L')
        pixels = img_gray.tobytes()
        img_type = 0
        bytes_per_pixel = 1
    elif 'gray' in filename or 'grey' in filename or 'semitones' in filename:
        img_gray = img.convert('L')
        pixels = img_gray.tobytes()
        img_type = 1
        bytes_per_pixel = 1
    elif 'color' in filename or 'colored' in filename:
        img_rgb = img.convert('RGB')
        pixels = img_rgb.tobytes()
        img_type = 2
        bytes_per_pixel = 3
    else:
        if img.mode == 'RGB':
            pixels = img.tobytes()
            img_type = 2
            bytes_per_pixel = 3
        else:
            img_gray = img.convert('L')
            pixels = img_gray.tobytes()
            unique = set(img_gray.getdata())
            if unique <= {0, 255}:
                img_type = 0
            else:
                img_type = 1
            bytes_per_pixel = 1
    
    with open(output_path, 'wb') as f:
        f.write(struct.pack('B', img_type))
        f.write(struct.pack('>H', img.width))
        f.write(struct.pack('>H', img.height))
        f.write(pixels)
    
    original_size = os.path.getsize(image_path)
    raw_size = os.path.getsize(output_path)
    
    return {
        'name': os.path.basename(image_path),
        'original_size': original_size,
        'raw_size': raw_size,
        'ratio': raw_size / original_size,
        'pixels': img.width * img.height
    }
