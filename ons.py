# -*- coding: utf-8 -*-
"""
ons
===
ONS file readers.
"""

import io


class CSV(object):
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

    code = 'CDID'
    fields = ['Title', 'PreUnit', 'Unit', 'Release Date', 'Next release', 'Important Notes']

    def __init__(self, path_or_buffer):
        if hasattr(path_or_buffer, 'read'):
            self._buffer = self._iter(path_or_buffer)
        else:
            self._buffer = self._iter(open(path_or_buffer))

    def _iter(self, buffer):
        # Read file header (mix of metadata and column titles), breaking on
        # first line of data
        metadata = []

        for line in buffer:
            label = line.split(',', maxsplit=1)[0].replace('"', '')

            if label == self.code:
                header = line
            elif label in self.fields:
                metadata.append(line)
            else:
                break

        # Assemble metadata into a string
        self._metadata = ''.join([header] + metadata)

        # Assemble iterator from column titles and data
        def data():
            yield header
            yield line
            yield from buffer
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
            return ''.join(list(self._buffer))
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
