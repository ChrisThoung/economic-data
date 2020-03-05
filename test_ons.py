# -*- coding: utf-8 -*-
"""
test_ons
========
Tests for ONS file readers.
"""

import csv
import os
import unittest

import numpy as np

from pandas import DataFrame, Index
from pandas.testing import assert_frame_equal
import pandas as pd

from ons import CSV


current_dir = os.path.split(__file__)[0]

csv_filepath = os.path.join(current_dir, 'test_data', 'ons.csv')
csv_expected_metadata = '''\
"CDID","AB12","XY90"
"Title","First variable","Variable 2"
"PreUnit","£","£"
"Unit","","m"
"Release Date","13-01-2018","13-01-2018"
"Next release","16 February 2018","16 February 2018"
"Important Notes","",""
'''


def test_csv_string():
    # Test that string contents (on `read()`) match
    with open(csv_filepath) as f:
        ons = CSV(f)
        data = ons.read()
        metadata = ons.metadata.read()

    assert data == '''\
"CDID","AB12","XY90"
"1946","1.0",""
"1947","2.0","0.0"
'''
    assert metadata == csv_expected_metadata

def test_csv_reader():
    # Test that standard-library `csv.reader` works
    with CSV(csv_filepath) as f:
        assert f.metadata.read() == csv_expected_metadata

        reader = csv.reader(f)

        assert next(reader) == ['CDID', 'AB12', 'XY90']
        assert next(reader) == ['1946', '1.0', '']
        assert next(reader) == ['1947', '2.0', '0.0']

        try:
            next(reader)
            assert False, 'EOF expected'
        except StopIteration:
            assert True

        reader = csv.reader(f.metadata)

        assert next(reader) == ['CDID', 'AB12', 'XY90']
        assert next(reader) == ['Title', 'First variable', 'Variable 2']
        assert next(reader) == ['PreUnit', '£', '£']
        assert next(reader) == ['Unit', '', 'm']
        assert next(reader) == ['Release Date', '13-01-2018', '13-01-2018']
        assert next(reader) == ['Next release', '16 February 2018', '16 February 2018']
        assert next(reader) == ['Important Notes', '', '']

        try:
            next(reader)
            assert False, 'EOF expected'
        except StopIteration:
            assert True

def test_csv_dictreader():
    # Test that standard-library `csv.DictReader` works
    with CSV(csv_filepath) as f:
        reader = csv.DictReader(f)

        assert next(reader) == {'CDID': '1946', 'AB12': '1.0', 'XY90': ''}
        assert next(reader) == {'CDID': '1947', 'AB12': '2.0', 'XY90': '0.0'}

        try:
            next(reader)
            assert False, 'EOF expected'
        except StopIteration:
            assert True

        reader = csv.DictReader(f.metadata)

        assert next(reader) == {'CDID': 'Title', 'AB12': 'First variable', 'XY90': 'Variable 2'}
        assert next(reader) == {'CDID': 'PreUnit', 'AB12': '£', 'XY90': '£'}
        assert next(reader) == {'CDID': 'Unit', 'AB12': '', 'XY90': 'm'}
        assert next(reader) == {'CDID': 'Release Date', 'AB12': '13-01-2018', 'XY90': '13-01-2018'}
        assert next(reader) == {'CDID': 'Next release', 'AB12': '16 February 2018', 'XY90': '16 February 2018'}
        assert next(reader) == {'CDID': 'Important Notes', 'AB12': '', 'XY90': ''}

        try:
            next(reader)
            assert False, 'EOF expected'
        except StopIteration:
            assert True

def test_csv_pandas():
    # Test with `pandas` `read_csv()`
    with CSV(csv_filepath) as f:
        data = pd.read_csv(f, index_col=0)
        metadata = pd.read_csv(f.metadata, index_col=0)

    assert_frame_equal(data,
                       DataFrame({'AB12': [1.0, 2.0],
                                  'XY90': [np.nan, 0.0]},
                                 index=Index([1946, 1947], name='CDID')))

    assert_frame_equal(metadata,
                       DataFrame({
                           'AB12': ['First variable', '£', np.nan, '13-01-2018', '16 February 2018', np.nan],
                           'XY90': ['Variable 2', '£', 'm', '13-01-2018', '16 February 2018', np.nan]},
                                 index=Index(['Title',
                                              'PreUnit',
                                              'Unit',
                                              'Release Date',
                                              'Next release',
                                              'Important Notes'], name='CDID')))


class TestCSVMultiLine(unittest.TestCase):

    CSV_FILEPATH = os.path.join(current_dir, 'test_data', 'ons_multiline.csv')
    CSV_EXPECTED_METADATA = '''\
"CDID","AB12","XY90"
"Title","First variable","Variable 2"
"PreUnit","
£","£
"
"Unit","","m"
"Release Date","13-01-2018","13-01-2018"
"Next release","16
February
2018","16
February
2018"
"Important Notes","",""
'''

    def test_csv_string(self):
        # Test that string contents (on `read()`) match
        with open(self.CSV_FILEPATH) as f:
            ons = CSV(f)
            data = ons.read()
            metadata = ons.metadata.read()

        assert data == '''\
"CDID","AB12","XY90"
"1946","1.0",""
"1947","2.0","0.0"
'''
        assert metadata == self.CSV_EXPECTED_METADATA


if __name__ == '__main__':
    unittest.main()
