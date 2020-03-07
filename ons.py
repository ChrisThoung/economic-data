# -*- coding: utf-8 -*-
"""
ons
===
UK Office for National Statistics (ONS) data file readers.

-------------------------------------------------------------------------------
MIT License

Copyright (c) 2018-20 Chris Thoung

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__version__ = '0.3.1'


import csv
import io
import itertools


class CSV:
    """File-like object to read UK Office for National Statistics (ONS) CSV time-series datasets
    e.g. the UK Economic Accounts:
         https://www.ons.gov.uk/economy/grossdomesticproductgdp/datasets/unitedkingdomeconomicaccounts

    Separates lines of data from metadata while preserving a common header line.

    The object itself is iterable, returning the column titles (short series
    codes) and data from the file as strings, line by line. This format is
    compatible with the Python standard library `csv` readers as well as
    `pandas` `read_csv()`.

    The metadata are accessible as an attribute (`metadata`), which is a
    `StringIO` object of the lines of metadata. It is thus iterable in a
    similar manner to the data.

    Examples
    --------
    >>> from ons import CSV  # This class

    >>> import csv
    >>> with CSV('ukea.csv') as f:
    ...     metadata = f.metadata.read()  # No need to read the data before accessing the metadata
    ...     reader = csv.reader(f)  # `DictReader` works, too
    ...     for row in reader:
    ...         pass

    >>> import pandas as pd
    >>> with CSV('ukea.csv') as f:
    >>>     data = pd.read_csv(f, index_col=0)
    >>>     metadata = pd.read_csv(f.metadata, index_col=0)
    """

    __slots__ = ['_buffer', '_metadata']

    CODE = 'CDID'
    FIELDS = ['Title', 'PreUnit', 'Unit', 'Release Date', 'Next release', 'Important Notes']

    def __init__(self, path_or_buffer):
        if hasattr(path_or_buffer, 'read'):
            self._buffer = self._iter(path_or_buffer)
        else:
            self._buffer = self._iter(open(path_or_buffer))

    def _iter(self, buffer):
        # Copy `buffer` twice:
        #  - `reader_stream`: to check the header and metadata
        #  - `line_stream`: to return data (as distinct from header/metadata)
        reader_stream, line_stream = itertools.tee(buffer, 2)

        # Read header and metadata to separate lists
        header_lines = []
        metadata_lines = []

        reader = csv.reader(reader_stream)

        start = reader.line_num
        for row in reader:
            # Store line indexes for the row as a `range()` object
            end = reader.line_num
            count = end - start
            start = end

            # Check row contents
            label = row[0]

            # Header
            if label == self.CODE:
                for _ in range(count):
                    header_lines.append(next(line_stream))

            # Metadata
            elif label in self.FIELDS:
                for _ in range(count):
                    metadata_lines.append(next(line_stream))

            # Anything else: Assume data and break
            else:
                break

        # Assemble metadata into a string
        self._metadata = ''.join(itertools.chain(header_lines, metadata_lines))

        # Assemble iterator from column titles and data
        def data():
            yield from header_lines
            yield from line_stream

        return data()

    @property
    def metadata(self):
        """File metadata as a `StringIO` object."""
        return io.StringIO(self._metadata)

    def __iter__(self):
        yield from self._buffer

    def __next__(self):
        return next(self._buffer)

    def read(self, size=-1):
        if size == -1:
            return ''.join(self._buffer)
        else:
            return self.readline()

    def readline(self, *args):
        try:
            return next(self._buffer)
        except StopIteration:
            return ''

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass
