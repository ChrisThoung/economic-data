# -*- coding: utf-8 -*-
"""
test_imf
========
Tests for IMF file readers.
"""

from pathlib import Path
import unittest

from imf import WEO, detect_encoding


class TestTSV(unittest.TestCase):
    def test_detect_infer_encoding(self):
        # Check that the results of `detect_encoding()` and `infer_encoding()`
        # match for a given set of input files
        for path in Path('test_data').glob('*.xls'):
            with self.subTest(path=path):
                self.assertEqual(WEO.infer_encoding(path), detect_encoding(path)['encoding'])

    def test_infer_encoding(self):
        # Check that `infer_encoding()` identifies the correct encoding
        test_cases = {
            'WEOSep2011all.xls': 'ISO-8859-1',  # Special case: No other IMF release in September
            'WEOApr2019all.xls': 'ISO-8859-1',
            'WEOOct2019all.xls': 'ISO-8859-1',
            'WEOApr2020all.xls': 'ISO-8859-1',
            'WEOOct2020all.xls': 'utf-16le',    # Special case: One-off difference, October 2020
            'WEOApr2021all.xls': 'ISO-8859-1',
            'WEOOct2021all.xls': 'ISO-8859-1',
            'WEOApr2022all.xls': 'utf-16le',    # April forecasts switch file encoding from now on
            'WEOOct2022all.xls': 'ISO-8859-1',
            'WEOApr2023all.xls': 'utf-16le',
            'WEOOct2023all.xls': 'ISO-8859-1',
            'WEOApr2024all.xls': 'utf-16le',
        }  # fmt: skip

        for name, expected_encoding in test_cases.items():
            with self.subTest(name=name):
                self.assertEqual(WEO.infer_encoding(name), expected_encoding)


if __name__ == '__main__':
    unittest.main()
