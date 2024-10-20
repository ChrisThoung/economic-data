# -*- coding: utf-8 -*-
"""
test_imf
========
Tests for IMF file readers.
"""

from pathlib import Path
import unittest
import warnings

import pandas as pd

from imf import WEO, detect_encoding


EXPECTED_PROPERTIES = {
    'WEOSep2011all': ('ISO-8859-1', (8465, 47)),  # Special case: No other IMF release in September
    'WEOApr2019all': ('ISO-8859-1', (8732, 55)),
    'WEOOct2019all': ('ISO-8859-1', (8731, 55)),
    'WEOApr2020all': ('ISO-8859-1', (1554, 52)),
    'WEOOct2020all': ('utf-16le',   (8776, 57)),  # Special case: One-off difference, October 2020
    'WEOApr2021all': ('ISO-8859-1', (8777, 57)),
    'WEOOct2021all': ('ISO-8859-1', (8823, 57)),
    'WEOApr2022all': ('utf-16le',   (8625, 59)),  # April forecasts switch file encoding from now on
    'WEOOct2022all': ('ISO-8859-1', (8626, 58)),
    'WEOApr2023all': ('utf-16le',   (8625, 60)),
    'WEOOct2023all': ('ISO-8859-1', (8626, 59)),
    'WEOApr2024all': ('utf-16le',   (8625, 61)),
}  # fmt: skip


class TestTSV(unittest.TestCase):
    def test_read(self):
        # Check that file reads return the expected encodings and table sizes
        for path in Path('test_data').glob('*.xls'):
            # Warn and continue if no expected properties found
            name = path.stem
            if name not in EXPECTED_PROPERTIES:
                warnings.warn(
                    f'No test information available for "{name}"; skipping...'
                )
                continue

            expected_encoding, expected_shape = EXPECTED_PROPERTIES[name]

            with self.subTest(path=path):
                with WEO(path) as f:
                    self.assertEqual(f.encoding, expected_encoding)
                    self.assertEqual(
                        pd.read_csv(f, delimiter='\t').shape, expected_shape
                    )

    def test_detect_infer_encoding(self):
        # Check that the results of `detect_encoding()` and `infer_encoding()`
        # match for a given set of input files
        for path in Path('test_data').glob('*.xls'):
            with self.subTest(path=path):
                self.assertEqual(
                    WEO.infer_encoding(path), detect_encoding(path)['encoding']
                )

    def test_infer_encoding(self):
        # Check that `infer_encoding()` identifies the correct encoding
        for name, (expected_encoding, _) in EXPECTED_PROPERTIES.items():
            with self.subTest(name=name):
                self.assertEqual(WEO.infer_encoding(name), expected_encoding)


if __name__ == '__main__':
    unittest.main()
