# -*- coding: utf-8 -*-
"""
imf
===
International Monetary Fund (IMF) data file readers.

-------------------------------------------------------------------------------
MIT License

Copyright (c) 2024 Chris Thoung

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

import calendar
from io import BytesIO, StringIO
import itertools
from os import PathLike
from pathlib import Path
import re
from typing import Any, Dict, List, Literal, Optional, Pattern, Union
import warnings


__version__ = '0.4.0'


def detect_encoding(
    path_or_buffer: Union[str, bytes, PathLike, BytesIO],
    *,
    min_lines: int = 1,
    max_lines: int = 0,
) -> Dict[str, Any]:
    """Return the detected file encoding of `path_or_buffer`. **Requires `chardet`**.

    Parameters
    ----------
    path_or_buffer : pathlike or bytes buffer
        File (pathlike to open as bytes buffer) or filelike (bytes buffer) to
        read. **Cannot** be a str buffer.
    min_lines : int, default 1
        Minimum number of lines to read from `path_or_buffer`.
    max_lines : int, default 0
        Maximum number of lines to read from `path_or_buffer`.
        Special cases:
          0: Read as many lines as needed to confidently detect the file
             encoding
         -1: Read the entire file/buffer

    Returns
    -------
    : dict
        Result from `chardet` detection i.e. a two-item dictionary with
        contents:
         - 'encoding' : the detected/best-guess encoding (str)
         - 'confidence': the level of confidence of that guess (float)

    Notes
    -----
    This function raises a warning if confidence in the detected encoding is
    too low.

    See also
    --------
    Python chardet package:
        https://chardet.readthedocs.io/en/latest/usage.html#example-detecting-encoding-incrementally
    """
    from chardet.universaldetector import UniversalDetector

    def detect_buffer_encoding(buffer) -> Dict[str, Any]:
        """Return the `chardet` results for `buffer`."""
        detector = UniversalDetector()
        done: bool = False

        for i, line in enumerate(buffer, start=1):
            # Read next line and store detection status
            detector.feed(line)
            done = detector.done

            # Continue if reading entire file
            if max_lines == -1:
                continue

            # Break if (non-zero) maximum number of lines read
            if i >= max_lines > 0:
                break

            # Break if minimum number of lines read and detection complete
            if i >= min_lines and done:
                break

        # Close detector and check if detection is complete i.e. confidence is
        # high enough
        detector.close()

        # Print warning if detection incomplete
        if not done:
            encoding = detector.result['encoding']
            confidence = detector.result['confidence']

            msg = f'Best guess encoding: {encoding} (confidence: {confidence})'
            warnings.warn(msg)

        return detector.result

    if hasattr(path_or_buffer, 'read'):
        # TODO: Check for bytes
        return detect_buffer_encoding(path_or_buffer)
    else:
        with open(path_or_buffer, 'rb') as f:
            return detect_buffer_encoding(f)


class WEO:
    """File-like object to read IMF World Economic Outlook datasets in TSV format.

    Parameters
    ----------
    path_or_buffer :
        Input to read from
    encoding : str, default `None`
        **If `path_or_buffer` is of type `StringIO`, `encoding` must be
          `None`**.

        If non-`None`, one of:
         - a specific file encoding e.g. 'utf-16le', 'ISO-8859-1' etc
         - 'infer_' : guess the encoding from the filename in `path_or_buffer`
         - 'detect_' : guess the encoding from the contents of `path_or_buffer`

        If `None` (the default), behaviour varies according to the type of
        `path_or_buffer`:
         - str, bytes or PathLike: 'infer_'
         - StringIO: Ignore (encoding already implied by the object: `None` is
                     required)
         - BytesIO: 'detect_'

    min_lines : int, default 1 (if `encoding='detect_'`)
        Argument to `detect_encoding()`: Minimum number of lines to read from
        `path_or_buffer`.
    max_lines : int, default 0 (if `encoding='detect_'`)
        Argument to `detect_encoding()`: Maximum number of lines to read from
        `path_or_buffer`.
        Special cases:
          0: Read as many lines as needed to confidently detect the file
             encoding
         -1: Read the entire file/buffer

    See also
    --------
    IMF World Economic Outlook databases:
        https://www.imf.org/en/Publications/SPROLLs/world-economic-outlook-databases
    """

    # Regex: Extract `month` and `year` from a standard IMF WEO filename
    FILENAME_PATTERN: Pattern = re.compile(
        r'^WEO(?P<month>\S{3})(?P<year>\d{4}).+?(?:[.].*)?$'
    )

    # Mapping: Three-character month names to (1-based) numbers
    #          ('Jan', 1), ('Feb', 2), ('Mar', 3) etc
    MONTH_NUMBERS: Dict[str, int] = {
        x: i for i, x in enumerate(calendar.month_abbr) if len(x)
    }

    @staticmethod
    def infer_encoding(
        filename_or_path: Union[str, bytes, PathLike],
        *,
        regex_or_pattern: Optional[Union[str, Pattern]] = None,
    ) -> str:
        """Return the file encoding inferred from the filename in `filename_or_path`.

        Parameters
        ----------
        filename_or_path :
            Name or path to assess. This function operates on the `stem` of
            `Path(filename_or_path)`, ignoring the path and any file extension.
        regex_or_pattern : default, `None`
            Regular expression to use to extract the month and year information
            from `filename_or_path`. If `None`, default to the regex in the
            current class's `FILENAME_PATTERN` attribute.

        Returns
        -------
        : str
            The inferred coding e.g. 'utf-16le' or 'ISO-8859-1'

        Notes
        -----
        Under the default regex, this function assumes that the filename
        conforms to the standard one for IMF WEO downloads
        e.g. 'WEOApr2022all', 'WEOOct2022all', 'WEOApr2023all',
        'WEOOct2023all', 'WEOApr2024all' etc.

        The default regex extracts the month (converting it to an integer) as
        well as the year (also converting to an integer). These fields
        correspond to the date of the relevant database release.

        For example, for the filename 'WEOApr2024all', the fields are:
         - year: int = 2024 (extracted from '2024')
         - month: int = 4 (translated from 'Apr')

        Any alternative regex needs to extract the following as named fields
        (using `groupdict()`):
         - year: str = the year of the database release (the function converts
                       this to int)
         - month: str = the three-character month of the database release,
                        usually 'Apr' or 'Oct' (the function maps this to an
                        int, with Jan = 1)
        """
        # Use a `Path` object to extract the filename; for example:
        #  - /path/to/somefile.xls -> somefile
        #  - somefile.xls -> somefile
        name = Path(filename_or_path).stem

        # Set regex for month-year search
        if regex_or_pattern is None:
            pattern = __class__.FILENAME_PATTERN
        elif not isinstance(regex_or_pattern, Pattern):
            pattern = re.compile(regex_or_pattern)
        else:
            pattern = regex_or_pattern

        # Search the filename for the month and year
        match_ = pattern.search(name)
        if not match_:
            msg = f'Unable to infer file encoding from name: {name}'
            raise ValueError(msg)

        groupdict = match_.groupdict()

        month = __class__.MONTH_NUMBERS[groupdict['month']]
        year = int(groupdict['year'])

        # Infer the file encoding from the month-year combination

        # April publications:
        #  - 2022 onwards: 'utf-16le'
        #  - otherwise: 'ISO-8859-1'
        if month == 4:
            if year >= 2022:
                return 'utf-16le'
            else:
                return 'ISO-8859-1'

        # October publications:
        #  - 2020 (special case): 'utf-16le'
        #  - otherwise: 'ISO-8859-1'
        if month == 10:
            if year == 2020:
                return 'utf-16le'
            else:
                return 'ISO-8859-1'

        # September 2011 (one-off)
        if month == 9 and year == 2011:
            return 'ISO-8859-1'

        # If here, raise an exception from being unable to infer an encoding
        msg = f'Unable to infer file encoding from: {filename_or_path}'
        raise ValueError(msg)
