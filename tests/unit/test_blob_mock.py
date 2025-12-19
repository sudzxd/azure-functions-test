"""Unit tests for Blob (InputStream) mock."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Project/Local
from azure_functions_test import mock_blob


# =============================================================================
# TESTS: Initialization & Defaults
# =============================================================================
def test_mock_blob_uses_defaults_when_no_args() -> None:
    """mock_blob() should use default values when called with no args."""
    blob = mock_blob()

    assert blob.name == "test-blob.txt"
    assert blob.uri == "https://test.blob.core.windows.net/container/test-blob.txt"
    assert blob.length == 0
    assert blob.read() == b""


def test_mock_blob_uses_empty_content_by_default() -> None:
    """mock_blob() should use empty bytes content by default."""
    blob = mock_blob()

    assert blob.read() == b""


# =============================================================================
# TESTS: Content - String
# =============================================================================
def test_mock_blob_string_content_encoded_to_utf8() -> None:
    """String content should be UTF-8 encoded to bytes."""
    blob = mock_blob("Hello, World!")

    content = blob.read()
    assert isinstance(content, bytes)
    assert content == b"Hello, World!"


def test_mock_blob_string_content_with_unicode() -> None:
    """String with Unicode characters should be encoded correctly."""
    blob = mock_blob("Hello, 世界! 🌍")

    content = blob.read()
    assert content.decode("utf-8") == "Hello, 世界! 🌍"


def test_mock_blob_empty_string_content() -> None:
    """Empty string should encode to empty bytes."""
    blob = mock_blob("")

    assert blob.read() == b""


# =============================================================================
# TESTS: Content - Bytes
# =============================================================================
def test_mock_blob_bytes_content_used_as_is() -> None:
    """Bytes content should be used as-is without modification."""
    blob = mock_blob(b"\x89PNG\r\n\x1a\n")

    content = blob.read()
    assert content == b"\x89PNG\r\n\x1a\n"


def test_mock_blob_binary_content() -> None:
    """Binary content should be handled correctly."""
    binary_data = b"\x00\x01\x02\x03\x04\x05"
    blob = mock_blob(binary_data)

    content = blob.read()
    assert content == binary_data


# =============================================================================
# TESTS: Content - None
# =============================================================================
def test_mock_blob_none_content_becomes_empty_bytes() -> None:
    """None content should become empty bytes."""
    blob = mock_blob(None)

    assert blob.read() == b""


# =============================================================================
# TESTS: Metadata
# =============================================================================
def test_mock_blob_custom_name() -> None:
    """Custom name should override the default."""
    blob = mock_blob("test", name="document.pdf")

    assert blob.name == "document.pdf"


def test_mock_blob_custom_uri() -> None:
    """Custom URI should override the default."""
    uri = "https://myaccount.blob.core.windows.net/container/file.txt"
    blob = mock_blob("test", uri=uri)

    assert blob.uri == uri


def test_mock_blob_all_metadata() -> None:
    """All metadata should work together."""
    uri = "https://myaccount.blob.core.windows.net/photos/photo.jpg"
    blob = mock_blob(b"image data", name="photo.jpg", uri=uri)

    assert blob.name == "photo.jpg"
    assert blob.uri == uri


# =============================================================================
# TESTS: Length Property
# =============================================================================
def test_mock_blob_length_auto_calculated() -> None:
    """Length should be auto-calculated from content."""
    blob = mock_blob("Hello, World!")

    assert blob.length == 13


def test_mock_blob_length_empty_content() -> None:
    """Length should be 0 for empty content."""
    blob = mock_blob("")

    assert blob.length == 0


def test_mock_blob_length_binary_content() -> None:
    """Length should be calculated for binary content."""
    blob = mock_blob(b"\x00\x01\x02\x03\x04")

    assert blob.length == 5


# =============================================================================
# TESTS: Read Method - Full Read
# =============================================================================
def test_mock_blob_read_full_content() -> None:
    """read() should return full content by default."""
    blob = mock_blob("Hello, World!")

    content = blob.read()
    assert content == b"Hello, World!"


def test_mock_blob_read_with_negative_one() -> None:
    """read(-1) should return full content."""
    blob = mock_blob("Test content")

    content = blob.read(-1)
    assert content == b"Test content"


# =============================================================================
# TESTS: Read Method - Partial Read
# =============================================================================
def test_mock_blob_read_partial_content() -> None:
    """read(size) should return specified number of bytes."""
    blob = mock_blob("Hello, World!")

    content = blob.read(5)
    assert content == b"Hello"


def test_mock_blob_read_multiple_chunks() -> None:
    """Multiple read() calls should return consecutive chunks."""
    blob = mock_blob("Hello, World!")

    chunk1 = blob.read(5)
    chunk2 = blob.read(2)
    chunk3 = blob.read(6)

    assert chunk1 == b"Hello"
    assert chunk2 == b", "
    assert chunk3 == b"World!"


def test_mock_blob_read_beyond_content() -> None:
    """read() should handle reading beyond content length."""
    blob = mock_blob("Hello")

    chunk1 = blob.read(3)
    chunk2 = blob.read(10)  # More than remaining

    assert chunk1 == b"Hel"
    assert chunk2 == b"lo"  # Only remaining bytes


def test_mock_blob_read_after_full_read() -> None:
    """read() after full read should return empty bytes."""
    blob = mock_blob("Hello, World!")

    _ = blob.read()  # Read all
    remaining = blob.read()

    assert remaining == b""


# =============================================================================
# TESTS: Read Method - Edge Cases
# =============================================================================
def test_mock_blob_read_zero_bytes() -> None:
    """read(0) should return empty bytes."""
    blob = mock_blob("Hello, World!")

    content = blob.read(0)
    assert content == b""


def test_mock_blob_read_empty_blob() -> None:
    """read() on empty blob should return empty bytes."""
    blob = mock_blob("")

    content = blob.read()
    assert content == b""


def test_mock_blob_read_empty_blob_with_size() -> None:
    """read(size) on empty blob should return empty bytes."""
    blob = mock_blob("")

    content = blob.read(10)
    assert content == b""


# =============================================================================
# TESTS: Multiple Instances
# =============================================================================
def test_mock_blob_multiple_instances_independent() -> None:
    """Multiple blob instances should be independent."""
    blob1 = mock_blob("Content 1", name="file1.txt")
    blob2 = mock_blob("Content 2", name="file2.txt")

    assert blob1.read() == b"Content 1"
    assert blob2.read() == b"Content 2"
    assert blob1.name == "file1.txt"
    assert blob2.name == "file2.txt"


# =============================================================================
# TESTS: Integration with Real Use Cases
# =============================================================================
def test_mock_blob_text_file_simulation() -> None:
    """Should support testing text file processing."""
    blob = mock_blob("Line 1\nLine 2\nLine 3", name="data.txt")

    content = blob.read().decode("utf-8")
    lines = content.split("\n")

    assert len(lines) == 3
    assert lines[0] == "Line 1"
    assert blob.name == "data.txt"


def test_mock_blob_image_file_simulation() -> None:
    """Should support testing binary file processing."""
    # Simulate PNG header
    png_header = b"\x89PNG\r\n\x1a\n"
    blob = mock_blob(png_header, name="image.png")

    content = blob.read()
    assert content.startswith(b"\x89PNG")
    assert blob.name == "image.png"


def test_mock_blob_streaming_read_simulation() -> None:
    """Should support testing streaming/chunked reads."""
    content = "A" * 1000  # 1KB of data
    blob = mock_blob(content, name="large-file.txt")

    # Read in 256-byte chunks
    chunk1 = blob.read(256)
    chunk2 = blob.read(256)
    chunk3 = blob.read(256)
    chunk4 = blob.read(256)

    assert len(chunk1) == 256
    assert len(chunk2) == 256
    assert len(chunk3) == 256
    assert len(chunk4) == 232  # Remaining bytes


def test_mock_blob_with_all_parameters() -> None:
    """All parameters should work together."""
    uri = "https://myaccount.blob.core.windows.net/container/document.pdf"
    blob = mock_blob(
        b"PDF content here",
        name="document.pdf",
        uri=uri,
    )

    assert blob.read() == b"PDF content here"
    assert blob.name == "document.pdf"
    assert blob.uri == uri
    assert blob.length == 16
