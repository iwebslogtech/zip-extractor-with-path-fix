import tempfile
import unittest
import zipfile
import sys
import types
from pathlib import Path

# Allow core-function tests in headless environments where Tk is not installed.
tk = types.ModuleType("tkinter")
tk.Tk = object
tk.TclError = Exception
tk.StringVar = tk.IntVar = tk.BooleanVar = object
tk.Listbox = tk.Text = object
tk.filedialog = types.SimpleNamespace()
tk.messagebox = types.SimpleNamespace()
tk.ttk = types.SimpleNamespace()
sys.modules.setdefault("tkinter", tk)
sys.modules.setdefault("tkinter.filedialog", tk.filedialog)
sys.modules.setdefault("tkinter.messagebox", tk.messagebox)
sys.modules.setdefault("tkinter.ttk", tk.ttk)
from app import ExtractOptions, clean_component, extract_one, safe_member_parts

class ExtractorTests(unittest.TestCase):
    def test_invalid_and_reserved_names(self):
        self.assertEqual(clean_component('bad:name?.txt'), 'bad_name_.txt')
        self.assertEqual(clean_component('CON.txt'), '_CON.txt')

    def test_zip_slip_is_rejected(self):
        with self.assertRaises(ValueError):
            safe_member_parts('../outside.txt')

    def test_extract_and_shorten(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            archive = base / 'sample.zip'
            with zipfile.ZipFile(archive, 'w') as z:
                z.writestr('folder/' + 'a' * 120 + '.txt', b'hello')
                z.writestr('../outside.txt', b'blocked')
            output = base / 'out'
            logs = []
            result = extract_one(archive, ExtractOptions(output, max_path=100), logs.append, lambda a,b: None, lambda: False)
            self.assertEqual(result[0], 1)
            self.assertEqual(result[2], 1)
            self.assertFalse((base / 'outside.txt').exists())
            extracted = list(output.rglob('*.txt'))
            self.assertEqual(len(extracted), 1)
            self.assertEqual(extracted[0].read_bytes(), b'hello')

if __name__ == '__main__':
    unittest.main()
