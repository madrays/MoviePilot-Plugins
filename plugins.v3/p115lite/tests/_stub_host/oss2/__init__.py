"""
``oss2``（阿里云 OSS SDK）宿主桩

**为什么需要这个桩**

``oss2`` 是 MoviePilot V3 宿主的正式依赖（官方 ``pyproject.toml`` 声明
``oss2~=2.19.1``），插件用它在 ``core/u115_open.py`` 里做分片上传，
但不在自己的 ``requirements.txt`` 里声明。

自包含测试套件没有宿主，子进程以包整体加载 ``p115lite`` 时，
``from oss2 import ...`` 会失败。本桩提供导入期所需的最小符号集，
**不实现真实网络传输**：测试断言的是 Rust 降级逻辑，
不会真的调用 OSS 上传。
"""

__all__ = [
    "Bucket",
    "SizedFileAdapter",
    "StsAuth",
    "determine_part_size",
]

#: 分片大小下限（与真实 SDK 一致的量级，供上传逻辑做整除判断）
_DEFAULT_PART_SIZE = 100 * 1024
_MAX_PART_SIZE = 5 * 1024 * 1024 * 1024


class StsAuth:
    """
    STS 临时凭证鉴权桩

    保留 ``access_key_id`` / ``access_key_secret`` / ``security_token``
    三个构造参数，与真实签名对齐，便于被测代码无感使用。
    """

    def __init__(
        self,
        access_key_id: str = "",
        access_key_secret: str = "",
        security_token: str = "",
        auth_version: str = "v1",
        **kwargs: object,
    ) -> None:
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.security_token = security_token
        self.auth_version = auth_version
        self._kwargs = kwargs

    def __repr__(self) -> str:
        return f"<stub StsAuth access_key_id={self.access_key_id!r}>"


class Bucket:
    """
    OSS Bucket 桩

    真实实现承载全部网络操作；桩只记录构造参数，
    调用其方法会抛出明确的 NotImplementedError，
    避免测试在"以为上传成功"的假象下通过。
    """

    def __init__(
        self,
        auth: object = None,
        endpoint: str = "",
        bucket_name: str = "",
        connect_timeout: int = 60,
        **kwargs: object,
    ) -> None:
        self.auth = auth
        self.endpoint = endpoint
        self.bucket_name = bucket_name
        self.connect_timeout = connect_timeout
        self._kwargs = kwargs

    def _unsupported(self, name: str):
        raise NotImplementedError(
            f"oss2 测试桩不实现 {name}；如需真实上传能力请在测试中 mock 本对象"
        )

    def put_object(self, *args: object, **kwargs: object):
        return self._unsupported("put_object")

    def init_multipart_upload(self, *args: object, **kwargs: object):
        return self._unsupported("init_multipart_upload")

    def upload_part(self, *args: object, **kwargs: object):
        return self._unsupported("upload_part")

    def complete_multipart_upload(self, *args: object, **kwargs: object):
        return self._unsupported("complete_multipart_upload")

    def __repr__(self) -> str:
        return f"<stub Bucket bucket={self.bucket_name!r} endpoint={self.endpoint!r}>"


class SizedFileAdapter:
    """
    定长文件适配器桩

    真实实现把文件对象包装成"只读前 N 字节"的可读流，供分片上传使用。
    桩保留同名属性以便插件读取，``read`` 返回空字节。
    """

    def __init__(self, fileobj: object = None, size: int = 0, offset: int = 0) -> None:
        self.fileobj = fileobj
        self.size = size
        self.offset = offset
        self._left = size

    def read(self, amt: int = -1) -> bytes:
        """桩不产生真实数据，直接返回空"""
        return b""

    def __len__(self) -> int:
        return self.size

    def __repr__(self) -> str:
        return f"<stub SizedFileAdapter size={self.size}>"


def determine_part_size(
    total_size: int,
    preferred_size: int = _DEFAULT_PART_SIZE,
    min_part_size: int = _DEFAULT_PART_SIZE,
    max_part_size: int = _MAX_PART_SIZE,
) -> int:
    """
    计算分片大小

    按真实 SDK 的语义实现：把总分片数控制在 10000 以内，
    并在允许区间内尽量贴近 ``preferred_size``。
    这是纯计算逻辑，无需宿主即可给出与线上一致的结果。
    """
    if total_size <= 0:
        return min_part_size
    part_size = preferred_size
    while part_size * 10000 < total_size:
        part_size *= 2
    return max(min_part_size, min(part_size, max_part_size))
