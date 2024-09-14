# -*- coding: utf-8 -*-
"""
test_imf
========
Tests for IMF file readers.
"""

import unittest

from imf import WEO


class TestTSV(unittest.TestCase):
    def test_infer_encoding(self):
        # Check that `infer_encoding()` identifies the correct encoding
        test_cases = {
            'WEOApr2022all.xls': 'utf-16le',
            'WEOApr2023all.xls': 'utf-16le',
            'WEOApr2024all.xls': 'utf-16le',
            'WEOOct2021all.xls': 'ISO-8859-1',
            'WEOOct2022all.xls': 'ISO-8859-1',
            'WEOOct2023all.xls': 'ISO-8859-1',
            'WEOSep2011all.xls': 'ISO-8859-1',
        }

        for name, expected_encoding in test_cases.items():
            with self.subTest(name=name):
                self.assertEqual(WEO.infer_encoding(name), expected_encoding)


if __name__ == '__main__':
    unittest.main()
