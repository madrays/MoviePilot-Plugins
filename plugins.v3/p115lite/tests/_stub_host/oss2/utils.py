"""
``oss2.utils`` 宿主桩

插件用到两个工具：

* ``SizedFileAdapter`` —— 分片上传的定长文件适配器（自 ``oss2`` 顶层复用）
* ``b64encode_as_string`` —— Base64 编码，插件用于构造回调参数

``b64encode_as_string`` 是纯计算函数，这里给出与真实实现一致的结果。
"""

import base64

from . import SizedFileAdapter

__all__ = [
    "SizedFileAdapter",
    "b64encode_as_string",
]


def b64encode_as_string(data: object) -> str:
    """
    Base64 编码为字符串

    与真实 SDK 行为一致：接受 ``bytes`` 或 ``str``，返回 ``str``。
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    if isinstance(data, (bytes, bytearray)):
        return base64.b64encode(bytes(data)).decode("utf-8")
    return base64.b64encode(str(data).encode("utf-8")).decode("utf-8")
