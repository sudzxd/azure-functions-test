"""Blob input stream mock implementation.

This module provides a duck-typed mock for Azure Blob Storage input streams
with Pydantic validation and full type safety.
"""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Third-party
from pydantic import Field
from pydantic.dataclasses import dataclass

# Project/Local
from .._internal import get_logger
from ..protocols import InputStreamProtocol

# =============================================================================
# LOGGER
# =============================================================================
logger = get_logger(__name__)


# =============================================================================
# CORE CLASSES
# =============================================================================
@dataclass
class BlobMock:
    """Duck-typed mock for Azure Blob Storage input streams.

    This class implements the InputStreamProtocol interface using Pydantic
    dataclass for validation and type safety. It provides a simple in-memory
    blob representation with metadata.

    Attributes:
        name: The blob name. Defaults to "test-blob.txt".
        content: The blob content as bytes. Defaults to empty bytes.
        uri: The blob's primary location URI. Defaults to test URI.
        _position: Internal read position tracker. Not exposed publicly.

    Examples:
        Create a blob with text content:

        >>> blob = BlobMock(name="data.txt", content=b"Hello, World!")
        >>> blob.read()
        b'Hello, World!'
        >>> blob.length
        13

        Create a blob with custom URI:

        >>> blob = BlobMock(
        ...     name="photo.jpg",
        ...     uri="https://mystorageaccount.blob.core.windows.net/photos/photo.jpg",
        ...     content=b"\\x89PNG..."
        ... )
        >>> blob.name
        'photo.jpg'
    """

    name: str | None = Field(default="test-blob.txt")
    content: bytes = Field(default=b"")
    uri: str | None = Field(
        default="https://test.blob.core.windows.net/container/test-blob.txt"
    )
    _position: int = Field(default=0, init=False, repr=False)

    @property
    def length(self) -> int | None:
        """The size of the blob in bytes.

        Returns:
            Size of the blob content.

        Examples:
            >>> blob = BlobMock(content=b"Hello")
            >>> blob.length
            5
        """
        return len(self.content)

    def read(self, size: int = -1) -> bytes:
        """Read blob content.

        Args:
            size: Number of bytes to read. -1 reads entire blob from current position.

        Returns:
            Blob content as bytes.

        Examples:
            >>> blob = BlobMock(content=b"Hello, World!")
            >>> blob.read()
            b'Hello, World!'

            >>> blob = BlobMock(content=b"Hello, World!")
            >>> blob.read(5)
            b'Hello'
        """
        if size == -1:
            data = self.content[self._position :]
            self._position = len(self.content)
        else:
            data = self.content[self._position : self._position + size]
            self._position += len(data)
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation showing blob name, length, and memory address.

        Examples:
            >>> blob = BlobMock(name="data.txt", content=b"test")
            >>> repr(blob)
            "<BlobMock name='data.txt' length=4 at 0x...>"
        """
        return f"<BlobMock name={self.name!r} length={self.length} at {hex(id(self))}>"


# =============================================================================
# PUBLIC API
# =============================================================================
def mock_blob(
    content: str | bytes | None = None,
    *,
    name: str | None = None,
    uri: str | None = None,
) -> InputStreamProtocol:
    """Create a mock Blob InputStream for testing.

    Provides a test double for Azure Blob Storage input bindings with
    automatic content encoding and metadata. Returns an object that
    implements InputStreamProtocol.

    Args:
        content: Blob content. Strings are UTF-8 encoded. Bytes are used as-is.
        name: Blob name. Defaults to "test-blob.txt".
        uri: Blob URI. Defaults to test URI.

    Returns:
        A BlobMock instance implementing InputStreamProtocol.

    Examples:
        Create a blob with text content:

        >>> blob = mock_blob("Hello, World!", name="greeting.txt")
        >>> blob.read().decode()
        'Hello, World!'
        >>> blob.name
        'greeting.txt'

        Create a blob with bytes content:

        >>> blob = mock_blob(b"\\x89PNG\\r\\n\\x1a\\n", name="image.png")
        >>> blob.read()
        b'\\x89PNG\\r\\n\\x1a\\n'

        Create a blob with custom URI:

        >>> blob = mock_blob(
        ...     "data",
        ...     name="data.txt",
        ...     uri="https://myaccount.blob.core.windows.net/container/data.txt"
        ... )
        >>> blob.uri
        'https://myaccount.blob.core.windows.net/container/data.txt'

        Read blob in chunks:

        >>> blob = mock_blob("Hello, World!")
        >>> blob.read(5)
        b'Hello'
        >>> blob.read(7)
        b', World'
    """
    logger.debug(
        "Creating BlobMock with name=%s, length=%s",
        name or "test-blob.txt",
        len(content) if content else 0,
    )

    # Encode string content to bytes
    if isinstance(content, str):
        encoded_content = content.encode("utf-8")
    elif content is None:
        encoded_content = b""
    else:
        encoded_content = content

    # Build and return the mock
    return BlobMock(
        name=name if name is not None else "test-blob.txt",
        content=encoded_content,
        uri=uri
        if uri is not None
        else "https://test.blob.core.windows.net/container/test-blob.txt",
    )
