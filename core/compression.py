# core/compression.py
import gzip
import zlib
from typing import Union

import brotli


class CompressionManager:
    @staticmethod
    def compress(data: Union[str, bytes], method: str = "gzip") -> bytes:
        if isinstance(data, str):
            data = data.encode("utf-8")

        if method == "gzip":
            return gzip.compress(data)
        elif method == "zlib":
            return zlib.compress(data)
        elif method == "brotli":
            return brotli.compress(data)
        else:
            raise ValueError(f"Unsupported compression method: {method}")

    @staticmethod
    def decompress(data: bytes, method: str = "gzip") -> str:
        if method == "gzip":
            decompressed = gzip.decompress(data)
        elif method == "zlib":
            decompressed = zlib.decompress(data)
        elif method == "brotli":
            decompressed = brotli.decompress(data)
        else:
            raise ValueError(f"Unsupported decompression method: {method}")

        return decompressed.decode("utf-8")


# Usage in API responses
async def compress_response(data: dict) -> bytes:
    json_data = json.dumps(data)
    return CompressionManager.compress(json_data, "brotli")


from typing import Union


class CompressionManager:
    @staticmethod
    def compress(data: Union[str, bytes], method: str = "gzip") -> bytes:
        if isinstance(data, str):
            data = data.encode("utf-8")

        if method == "gzip":
            return gzip.compress(data)
        elif method == "zlib":
            return zlib.compress(data)
        elif method == "brotli":
            return brotli.compress(data)
        else:
            raise ValueError(f"Unsupported compression method: {method}")

    @staticmethod
    def decompress(data: bytes, method: str = "gzip") -> str:
        if method == "gzip":
            decompressed = gzip.decompress(data)
        elif method == "zlib":
            decompressed = zlib.decompress(data)
        elif method == "brotli":
            decompressed = brotli.decompress(data)
        else:
            raise ValueError(f"Unsupported decompression method: {method}")

        return decompressed.decode("utf-8")


# Usage in API responses
async def compress_response(data: dict) -> bytes:
    json_data = json.dumps(data)
    return CompressionManager.compress(json_data, "brotli")
