"""
``cryptography.hazmat.primitives.hashes`` 宿主桩

插件只用到两个对象：

* ``hashes.SHA1()`` —— 算法描述符
* ``hashes.Hash(algorithm)`` —— 增量哈希计算器，接口为
  ``update(bytes)`` + ``finalize()``，``finalize()`` 返回值需带 ``.hex()``

由于 SHA1 是纯计算，本桩**基于标准库 hashlib 给出与真实库语义一致的实现**，
而不是空壳：这样被测代码若真去算校验值，得到的结果与线上完全相同，
不会因桩而引入假阴性。
"""

import hashlib
from typing import Any

__all__ = [
    "Hash",
    "HashAlgorithm",
    "SHA1",
]


class HashAlgorithm:
    """哈希算法描述符基类桩"""

    #: 对应的 hashlib 算法名，由子类覆盖
    name: str = ""
    #: 摘要字节长度
    digest_size: int = 0

    def __repr__(self) -> str:
        return f"<stub {type(self).__name__}>"


class SHA1(HashAlgorithm):
    """SHA1 算法描述符桩，与真实实现常量一致"""

    name = "sha1"
    digest_size = 20


class _Digest(bytes):
    """
    ``Hash.finalize()`` 的返回值

    真实实现是 ``bytes`` 的子类，同时提供 ``.hex()``。
    这里直接继承 ``bytes``，保证 ``bytes(result)``、``len(result)``、
    ``result.hex()`` 等用法全部可用。
    """

    def __new__(cls, data: bytes = b"") -> "_Digest":
        return super().__new__(cls, data)

    def hex(self) -> str:  # type: ignore[override]
        """返回十六进制摘要（小写），与真实库一致"""
        return bytes(self).hex()


class Hash:
    """
    增量哈希计算器桩

    用法与真实库完全一致::

        h = hashes.Hash(hashes.SHA1())
        h.update(b"data")
        h.finalize().hex()

    底层委托 ``hashlib``，因此计算结果可信。
    """

    def __init__(self, algorithm: HashAlgorithm, backend: Any = None) -> None:
        if not isinstance(algorithm, HashAlgorithm) or not algorithm.name:
            raise TypeError(f"不支持的哈希算法: {algorithm!r}")
        self._algorithm = algorithm
        self._backend = backend
        self._hasher = hashlib.new(algorithm.name)

    @property
    def algorithm(self) -> HashAlgorithm:
        """返回算法描述符"""
        return self._algorithm

    def update(self, data: bytes) -> None:
        """喂入数据，可多次调用"""
        self._hasher.update(data)

    def copy(self) -> "Hash":
        """复制当前计算状态"""
        new = Hash(self._algorithm, self._backend)
        new._hasher = self._hasher.copy()
        return new

    def finalize(self) -> bytes:
        """
        结束计算并返回摘要

        返回 ``bytes`` 子类实例，同时具备 ``.hex()`` 方法。
        """
        return _Digest(self._hasher.digest())

    def __repr__(self) -> str:
        return f"<stub Hash algorithm={self._algorithm.name}>"
