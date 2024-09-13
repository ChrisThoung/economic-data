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

from io import BytesIO
from os import PathLike
from typing import Any, Dict, Union
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
