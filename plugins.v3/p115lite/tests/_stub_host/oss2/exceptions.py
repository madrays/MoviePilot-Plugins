"""
``oss2.exceptions`` 宿主桩

插件捕获 ``OssError``（基类）与 ``ServerError``（服务端错误）做重试判断。
桩沿用真实继承关系：``ServerError`` 是 ``OssError`` 的子类，
保证 ``except OssError`` 能捕获两者，重试逻辑语义不变。
"""

from typing import Optional

__all__ = [
    "OssError",
    "ServerError",
]


class OssError(Exception):
    """OSS 异常基类桩，保留 status / code / message 属性"""

    def __init__(
        self,
        message: str = "",
        status: Optional[int] = None,
        code: str = "",
        request_id: str = "",
        **kwargs: object,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status = status
        self.code = code
        self.request_id = request_id
        self._kwargs = kwargs


class ServerError(OssError):
    """
    服务端错误桩

    真实实现带 ``status``（HTTP 状态码），插件据其判断是否可重试
    （如 500/502/503）。
    """

    def __init__(
        self,
        status: int = 500,
        code: str = "",
        message: str = "",
        request_id: str = "",
        **kwargs: object,
    ) -> None:
        super().__init__(
            message=message,
            status=status,
            code=code,
            request_id=request_id,
            **kwargs,
        )
