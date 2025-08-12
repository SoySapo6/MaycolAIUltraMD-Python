# magic.py (local replacement)
"""
This is a local replacement for the `python-magic` library.
It is intended to avoid the dependency on the `libmagic` C library,
which can be difficult to install in some environments.
This module provides a minimal, compatible interface for the `neonize` library.
"""

# Define a dummy exception class to match the original library's interface
class MagicException(Exception):
    pass

def _guess_from_buffer(buffer):
    """
    A simple, pure-Python function to guess the mimetype from a buffer's magic bytes.
    """
    if buffer.startswith(b'\xff\xd8\xff'):
        return 'image/jpeg'
    if buffer.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'image/png'
    if buffer.startswith(b'GIF87a') or buffer.startswith(b'GIF89a'):
        return 'image/gif'
    if buffer.startswith(b'RIFF') and buffer[8:12] == b'WEBP':
        return 'image/webp'
    # Add more magic bytes checks here if needed for other file types.

    # Fallback for unknown types
    return 'application/octet-stream'

class Magic:
    """A mock class that mimics the `python-magic` Magic class."""
    def __init__(self, mime=True, mime_encoding=None, keep_going=False, uncompress=False):
        # We don't use these parameters, but we accept them for compatibility.
        if not mime:
            raise NotImplementedError("This mock magic library only supports mime=True")
        pass

    def from_buffer(self, buffer):
        """Guesses the mimetype from the first few bytes of the buffer."""
        return _guess_from_buffer(buffer)

    def from_file(self, filename):
        """Guesses the mimetype from the file's content."""
        try:
            with open(filename, 'rb') as f:
                return self.from_buffer(f.read(2048)) # Read first 2k bytes
        except FileNotFoundError:
            raise MagicException(f"No such file or directory: '{filename}'")

# For compatibility, some libraries might call magic.from_buffer directly
def from_buffer(buffer, mime=True):
    if not mime:
        raise NotImplementedError("This mock magic library only supports mime=True")
    return _guess_from_buffer(buffer)

def from_file(filename, mime=True):
    if not mime:
        raise NotImplementedError("This mock magic library only supports mime=True")
    m = Magic()
    return m.from_file(filename)
