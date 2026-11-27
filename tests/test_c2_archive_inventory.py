import tempfile
import unittest
import zipfile
from pathlib import Path
from scripts.c2_archive_inventory import inspect_archive


class TestArchiveInventory(unittest.TestCase):
    def make_archive(self, root, content=None):
        dest = Path(root) / 'input.zip'
        with zipfile.ZipFile(dest, 'w') as z:
            z.writestr('results/paired.csv', content or 'ba,date\nSRP,2025-07-01\nSRP,2025-07-02\n')
        return dest

    def test_inventory(self):
        with tempfile.TemporaryDirectory() as td:
            report=inspect_archive(self.make_archive(td))
            self.assertTrue(report['crc_passed'])
            self.assertEqual(report['csv_count'], 1)
            self.assertEqual(report['files'][0]['data_rows'], 2)
            self.assertEqual(report['files'][0]['columns'], ['ba','date'])

    def test_wrong_hash_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
                inspect_archive(self.make_archive(td), '0'*64)

    def test_unsafe_path_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            dest=Path(td)/'bad.zip'
            with zipfile.ZipFile(dest,'w') as z:
                z.writestr('../escape.csv','a\n1\n')
            with self.assertRaisesRegex(ValueError, 'Unsafe ZIP entry'):
                inspect_archive(dest)

    def test_empty_csv_header(self):
        with tempfile.TemporaryDirectory() as td:
            report=inspect_archive(self.make_archive(td, 'a,b\n'))
            self.assertEqual(report['files'][0]['data_rows'],0)

if __name__=='__main__':
    unittest.main()
