"""Example: Testing Blob Storage triggered Azure Functions."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
import json

# Third-party
from azure.functions import Out

# Project/Local
from azure_functions_test import FunctionTestContext, mock_blob
from azure_functions_test.protocols import InputStreamProtocol


# =============================================================================
# EXAMPLE: Simple Blob Processing
# =============================================================================
def process_uploaded_file(blob: InputStreamProtocol, output: Out[str]) -> None:
    """Process newly uploaded blob file.

    Args:
        blob: Input stream for blob data.
        output: Output binding for processed results.
    """
    content = blob.read()

    result = {
        "name": blob.name,
        "length": blob.length,
        "uri": blob.uri,
        "content_size": len(content),
    }

    output.set(json.dumps(result))


def test_process_uploaded_file() -> None:
    """Test processing of uploaded blob file."""
    # Arrange
    blob_content = b"Hello, Blob Storage!"
    blob = mock_blob(
        blob_content,
        name="uploads/test.txt",
        uri="https://account.blob.core.windows.net/container/test.txt",
    )
    ctx = FunctionTestContext()

    # Act
    process_uploaded_file(blob, ctx.out("processedBlob"))

    # Assert
    result = json.loads(ctx.outputs["processedBlob"])
    assert result["name"] == "uploads/test.txt"
    assert result["length"] == len(blob_content)
    assert result["content_size"] == len(blob_content)


# =============================================================================
# EXAMPLE: Processing Different Content Types
# =============================================================================
def process_json_blob(blob: InputStreamProtocol, output: Out[str]) -> None:
    """Process JSON blob file.

    Args:
        blob: Input stream with JSON data.
        output: Output binding for processing results.
    """
    content = blob.read()
    data = json.loads(content)

    # Process JSON data
    result = {
        "blob_name": blob.name,
        "data_keys": list(data.keys()),
        "processed": True,
    }

    output.set(json.dumps(result))


def test_process_json_blob() -> None:
    """Test processing JSON blob file."""
    # Arrange
    json_data = {"user_id": 123, "name": "Alice", "email": "alice@example.com"}
    blob_content = json.dumps(json_data).encode("utf-8")
    blob = mock_blob(blob_content, name="data/user.json")
    ctx = FunctionTestContext()

    # Act
    process_json_blob(blob, ctx.out("jsonResult"))

    # Assert
    result = json.loads(ctx.outputs["jsonResult"])
    assert result["blob_name"] == "data/user.json"
    assert "user_id" in result["data_keys"]
    assert result["processed"] is True


# =============================================================================
# EXAMPLE: Chunked Reading for Large Files
# =============================================================================
def process_large_file_in_chunks(blob: InputStreamProtocol, output: Out[str]) -> None:
    """Process large blob file in chunks.

    Args:
        blob: Input stream for large file.
        output: Output binding for processing results.
    """
    chunk_size = 1024
    total_chunks = 0
    total_bytes = 0

    while True:
        chunk = blob.read(chunk_size)
        if not chunk:
            break
        total_chunks += 1
        total_bytes += len(chunk)

    result = {
        "name": blob.name,
        "total_chunks": total_chunks,
        "total_bytes": total_bytes,
        "chunk_size": chunk_size,
    }

    output.set(json.dumps(result))


def test_process_large_file_in_chunks() -> None:
    """Test chunked processing of large blob file."""
    # Arrange
    # Create 3KB file
    large_content = b"x" * 3072
    blob = mock_blob(large_content, name="data/large.bin")
    ctx = FunctionTestContext()

    # Act
    process_large_file_in_chunks(blob, ctx.out("chunkResult"))

    # Assert
    result = json.loads(ctx.outputs["chunkResult"])
    assert result["total_chunks"] == 3  # 3KB / 1KB chunks
    assert result["total_bytes"] == 3072


# =============================================================================
# EXAMPLE: Empty Blob Handling
# =============================================================================
def process_blob_with_validation(
    blob: InputStreamProtocol, error: Out[str], result: Out[str]
) -> None:
    """Process blob with empty file validation.

    Args:
        blob: Input stream for blob.
        error: Output binding for errors.
        result: Output binding for successful results.
    """
    content = blob.read()

    if not content:
        error.set(json.dumps({"error": "Empty file", "blob_name": blob.name}))
        return

    result_data = {
        "blob_name": blob.name,
        "size": len(content),
        "status": "processed",
    }

    result.set(json.dumps(result_data))


def test_process_empty_blob() -> None:
    """Test handling of empty blob file."""
    # Arrange
    blob = mock_blob(b"", name="empty.txt")
    ctx = FunctionTestContext()

    # Act
    process_blob_with_validation(blob, ctx.out("error"), ctx.out("result"))

    # Assert
    error_data = json.loads(ctx.outputs["error"])
    assert error_data["error"] == "Empty file"
    assert error_data["blob_name"] == "empty.txt"


def test_process_non_empty_blob() -> None:
    """Test handling of non-empty blob file."""
    # Arrange
    blob = mock_blob(b"content", name="file.txt")
    ctx = FunctionTestContext()

    # Act
    process_blob_with_validation(blob, ctx.out("error"), ctx.out("result"))

    # Assert
    result_data = json.loads(ctx.outputs["result"])
    assert result_data["status"] == "processed"
    assert result_data["size"] == 7


# =============================================================================
# EXAMPLE: Binary Data Processing
# =============================================================================
def process_binary_blob(blob: InputStreamProtocol, output: Out[str]) -> None:
    """Process binary blob data.

    Args:
        blob: Input stream with binary data.
        output: Output binding for processing results.
    """
    content = blob.read()

    # Analyze binary data
    result = {
        "blob_name": blob.name,
        "size": len(content),
        "first_byte": content[0] if content else None,
        "is_binary": not all(32 <= b < 127 or b in (9, 10, 13) for b in content),
    }

    output.set(json.dumps(result))


def test_process_binary_blob() -> None:
    """Test processing binary blob data."""
    # Arrange
    binary_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    blob = mock_blob(binary_data, name="images/photo.png")
    ctx = FunctionTestContext()

    # Act
    process_binary_blob(blob, ctx.out("binaryResult"))

    # Assert
    result = json.loads(ctx.outputs["binaryResult"])
    assert result["blob_name"] == "images/photo.png"
    assert result["first_byte"] == 0x89
    assert result["is_binary"] is True


# =============================================================================
# EXAMPLE: Blob Metadata
# =============================================================================
def test_blob_metadata() -> None:
    """Test blob metadata properties."""
    # Arrange
    blob = mock_blob(
        b"test content",
        name="container/folder/file.txt",
        uri="https://account.blob.core.windows.net/container/folder/file.txt",
    )

    # Assert
    assert blob.name == "container/folder/file.txt"
    assert blob.uri == "https://account.blob.core.windows.net/container/folder/file.txt"
    assert blob.length == 12


if __name__ == "__main__":
    # Run all test examples
    test_process_uploaded_file()
    test_process_json_blob()
    test_process_large_file_in_chunks()
    test_process_empty_blob()
    test_process_non_empty_blob()
    test_process_binary_blob()
    test_blob_metadata()
    print("✓ All blob input stream examples passed!")
