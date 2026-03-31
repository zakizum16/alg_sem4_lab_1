import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import threading
from pathlib import Path


class CompressorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Компрессоры данных")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        style = ttk.Style()
        style.theme_use('clam')
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.create_tabs()
    
    def create_tabs(self):
        self.tab_tests = ttk.Frame(self.notebook)
        self.tab_rle = ttk.Frame(self.notebook)
        self.tab_raw = ttk.Frame(self.notebook)
        self.tab_info = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_tests, text="Тесты")
        self.notebook.add(self.tab_rle, text="RLE Компрессор")
        self.notebook.add(self.tab_raw, text="RAW Файлы")
        self.notebook.add(self.tab_info, text="Информация")
        
        self.setup_tests_tab()
        self.setup_rle_tab()
        self.setup_raw_tab()
        self.setup_info_tab()
    
    def setup_tests_tab(self):
        frame = ttk.Frame(self.tab_tests, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Запуск тестов компрессоров", font=("Arial", 14, "bold")).pack(pady=10)
        
        desc = "Тестирование всех компрессоров на файлах из test_data.\nВключены: RLE, Huffman, LZSS, LZW, BWT+RLE, BWT+MTF+RLE"
        ttk.Label(frame, text=desc, justify=tk.LEFT).pack(pady=10)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Запустить тесты", command=self.run_tests).pack(padx=5)
        
        self.tests_output = tk.Text(frame, height=20, width=80, wrap=tk.WORD)
        self.tests_output.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tests_output.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tests_output.config(yscrollcommand=scrollbar.set)
    
    def setup_rle_tab(self):
        frame = ttk.Frame(self.tab_rle, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="RLE Компрессор", font=("Arial", 14, "bold")).pack(pady=10)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Выбрать файл", command=self.select_and_compress_rle).pack(padx=5, side=tk.LEFT)
        ttk.Button(button_frame, text="Очистить", command=lambda: self.rle_output.delete(1.0, tk.END)).pack(padx=5, side=tk.LEFT)
        
        self.rle_output = tk.Text(frame, height=20, width=80, wrap=tk.WORD)
        self.rle_output.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.rle_output.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.rle_output.config(yscrollcommand=scrollbar.set)
    
    def setup_raw_tab(self):
        frame = ttk.Frame(self.tab_raw, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Работа с RAW файлами", font=("Arial", 14, "bold")).pack(pady=10)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Конвертировать в RAW", command=self.convert_to_raw).pack(padx=5, side=tk.LEFT)
        ttk.Button(button_frame, text="Просмотреть RAW", command=self.view_raw).pack(padx=5, side=tk.LEFT)
        ttk.Button(button_frame, text="Очистить", command=lambda: self.raw_output.delete(1.0, tk.END)).pack(padx=5, side=tk.LEFT)
        
        self.raw_output = tk.Text(frame, height=20, width=80, wrap=tk.WORD, font=("Courier", 9))
        self.raw_output.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.raw_output.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.raw_output.config(yscrollcommand=scrollbar.set)
    
    def setup_info_tab(self):
        frame = ttk.Frame(self.tab_info, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Информация о проекте", font=("Arial", 14, "bold")).pack(pady=10)
        
        self.info_output = tk.Text(frame, height=25, width=80, wrap=tk.WORD)
        self.info_output.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.info_output.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_output.config(yscrollcommand=scrollbar.set)
        
        self.display_info()
    
    def log_output(self, text_widget, message):
        text_widget.insert(tk.END, message + "\n")
        text_widget.see(tk.END)
        self.root.update()
    
    def run_tests(self):
        self.tests_output.delete(1.0, tk.END)
        
        def run_in_thread():
            try:
                from tests import test_on_data
                from pathlib import Path
                
                self.log_output(self.tests_output, "="*70)
                self.log_output(self.tests_output, "ЗАПУСК ТЕСТОВ КОМПРЕССОРОВ")
                self.log_output(self.tests_output, "="*70 + "\n")
                
                test_data_path = Path("test_data")
                if test_data_path.exists():
                    test_files = {
                        'test_data/russian_text.txt': 'Текст (русский)',
                    }
                    
                    for file_path, desc in test_files.items():
                        if Path(file_path).exists():
                            with open(file_path, 'rb') as f:
                                data = f.read()
                            self.log_output(self.tests_output, f"\n\nТестирование: {desc}")
                            self.log_output(self.tests_output, "-"*70)
                            test_on_data(data, desc, skip_slow=True)
                else:
                    self.log_output(self.tests_output, "[ERR] Папка test_data не найдена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при запуске тестов: {e}")
        
        thread = threading.Thread(target=run_in_thread, daemon=True)
        thread.start()
    
    def select_and_compress_rle(self):
        self.rle_output.delete(1.0, tk.END)
        
        try:
            from rle import get_available_files
            files = get_available_files()
            
            if not files:
                messagebox.showwarning("Нет файлов", "Нет файлов для сжатия в test_data и raw_images")
                return
            
            file_path = filedialog.askopenfilename(
                initialdir=".",
                title="Выберите файл для сжатия",
                filetypes=[("Все файлы", "*.*")]
            )
            
            if not file_path:
                return
            
            def compress_in_thread():
                try:
                    from rle import RLEFileHandler, determine_ms
                    import os
                    
                    Ms = determine_ms(file_path)
                    Mc = 1
                    
                    self.log_output(self.rle_output, f"Файл: {file_path}")
                    self.log_output(self.rle_output, f"Параметры: Ms={Ms}, Mc={Mc}\n")
                    self.log_output(self.rle_output, "Сжатие...")
                    
                    handler = RLEFileHandler(Ms=Ms, Mc=Mc, output_dir="rlecoding")
                    original_size, compressed_size, compressed_path = handler.compress_file(file_path)
                    ratio = original_size / compressed_size if compressed_size > 0 else 1
                    
                    self.log_output(self.rle_output, f"\nИсходный размер:  {original_size:>12,} байт")
                    self.log_output(self.rle_output, f"Сжатый размер:    {compressed_size:>12,} байт")
                    self.log_output(self.rle_output, f"Коэффициент:      {ratio:>23.2f}x")
                    self.log_output(self.rle_output, f"Сохранено в:      {compressed_path}")
                    
                    self.log_output(self.rle_output, "\nРаспаковка...")
                    decompressed_size, _, decompressed_path = handler.decompress_file(compressed_path)
                    
                    with open(file_path, 'rb') as f1, open(decompressed_path, 'rb') as f2:
                        original = f1.read()
                        decompressed = f2.read()
                        is_correct = original == decompressed
                    
                    status = "[OK]" if is_correct else "[ERR]"
                    self.log_output(self.rle_output, f"Статус проверки:  {status} (данные совпадают)" if is_correct else f"Статус проверки:  {status}")
                    self.log_output(self.rle_output, f"Сохранено в:      {decompressed_path}")
                    self.log_output(self.rle_output, "\n[OK] Готово!")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка при сжатии: {e}")
            
            thread = threading.Thread(target=compress_in_thread, daemon=True)
            thread.start()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def convert_to_raw(self):
        self.raw_output.delete(1.0, tk.END)
        
        file_path = filedialog.askopenfilename(
            initialdir="test_data",
            title="Выберите изображение для конвертирования",
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        
        if not file_path:
            return
        
        def convert_in_thread():
            try:
                from raw_converter import convert_and_analyze
                
                os.makedirs("raw_images", exist_ok=True)
                base_name = os.path.basename(file_path).rsplit('.', 1)[0]
                output_path = os.path.join("raw_images", base_name + '.raw')
                
                self.log_output(self.raw_output, "Конвертирование...")
                result = convert_and_analyze(file_path, output_path)
                
                self.log_output(self.raw_output, f"\n{'='*70}")
                self.log_output(self.raw_output, f"РЕЗУЛЬТАТ КОНВЕРТИРОВАНИЯ")
                self.log_output(self.raw_output, f"{'='*70}\n")
                self.log_output(self.raw_output, f"Файл: {result['name']}")
                self.log_output(self.raw_output, f"Тип: {result['type']}")
                self.log_output(self.raw_output, f"Размер: {result['pixels']:,} пикселей")
                self.log_output(self.raw_output, f"\nИсходный формат ({result['format']}): {result['original_size']:>10,} байт")
                self.log_output(self.raw_output, f"RAW файл:                        {result['raw_size']:>10,} байт")
                self.log_output(self.raw_output, f"Коэффициент: {result['ratio']:.2f}x")
                self.log_output(self.raw_output, f"\nСохранено в: {output_path}")
                self.log_output(self.raw_output, "\n[OK] Конвертирование завершено!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при конвертировании: {e}")
        
        thread = threading.Thread(target=convert_in_thread, daemon=True)
        thread.start()
    
    def view_raw(self):
        self.raw_output.delete(1.0, tk.END)
        
        file_path = filedialog.askopenfilename(
            initialdir="raw_images",
            title="Выберите RAW файл для просмотра",
            filetypes=[("RAW файлы", "*.raw"), ("Все файлы", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            from raw_opener import show_raw
            
            with open(file_path, 'rb') as f:
                data = f.read()
            
            self.log_output(self.raw_output, f"Файл: {os.path.basename(file_path)}")
            self.log_output(self.raw_output, f"Размер: {len(data)} байт\n")
            self.log_output(self.raw_output, "-"*70)
            
            info = show_raw(file_path)
            
            if info:
                self.log_output(self.raw_output, f"\nТип изображения: {info['type']}")
                self.log_output(self.raw_output, f"Размер: {info['width']} x {info['height']}")
                self.log_output(self.raw_output, f"Всего пикселей: {info['width'] * info['height']:,}")
                self.log_output(self.raw_output, f"Размер пиксельных данных: {len(info['pixel_data']):,} байт")
                
                self.log_output(self.raw_output, "\n\nПервые 16 байт (HEX):")
                hex_data = ' '.join(f'{b:02X}' for b in data[:16])
                self.log_output(self.raw_output, hex_data)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при просмотре RAW: {e}")
    
    def display_info(self):
        self.info_output.delete(1.0, tk.END)
        
        info_text = """ИНФОРМАЦИЯ О ПРОЕКТЕ
================================================================================

ОСНОВНАЯ ИНФОРМАЦИЯ:
  Проект: Компрессоры данных
  Язык: Python 3.7+
  Версия: 1.0

ДОСТУПНЫЕ КОМПРЕССОРЫ:
  • RLE              - Run-Length Encoding
  • Huffman          - Кодирование Хаффмана
  • LZSS             - LZ77-подобный алгоритм
  • LZW              - Lempel-Ziv-Welch
  • BWT              - Преобразование Барроуза-Уиллера
  • BWT+RLE          - Комбинированный (BWT + RLE)
  • BWT+MTF+RLE      - Комбинированный (BWT + MTF + RLE)

МОДУЛИ ПРОЕКТА:
"""
        
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
                status = "[OK]"
            else:
                status = "[ERR]"
            info_text += f"\n  {status} {file:<20} - {desc}"
        
        info_text += "\n\nКАТАЛОГИ ДАННЫХ:\n"
        
        dirs = [
            ("test_data", "Тестовые файлы"),
            ("raw_images", "RAW изображения"),
            ("rlecoding", "Результаты RLE кодирования"),
        ]
        
        for dirname, desc in dirs:
            if os.path.exists(dirname):
                count = len(os.listdir(dirname))
                status = "[OK]"
                info_text += f"\n  {status} {dirname:<20} - {desc} ({count} файлов)"
            else:
                status = "[ERR]"
                info_text += f"\n  {status} {dirname:<20} - {desc} (не найдена)"
        
        self.info_output.insert(1.0, info_text)


def main():
    root = tk.Tk()
    app = CompressorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
