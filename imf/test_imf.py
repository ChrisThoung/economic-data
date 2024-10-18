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
