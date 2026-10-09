"""
``oss2.models`` 宿主桩

插件只用到 ``PartInfo``：记录分片号与 ETag，供分片上传列表使用。
"""

from typing import Optional

__all__ = ["PartInfo"]


class PartInfo:
    """分片信息桩，保留 ``part_number`` / ``etag`` 语义"""

    def __init__(self, part_number: int = 0, etag: Optional[str] = None, **kwargs: object) -> None:
        self.part_number = part_number
        self.etag = etag
        self._kwargs = kwargs

    def __repr__(self) -> str:
        return f"<stub PartInfo part_number={self.part_number} etag={self.etag!r}>"
