"""
``fastapi.responses`` 宿主桩

插件只用到 ``JSONResponse`` 与 ``RedirectResponse`` 两个类，
这里给出与真实签名兼容的最小实现，供导入期使用。
测试断言的是 Rust 降级逻辑，不会真的走 HTTP 响应流程。
"""

from typing import Any, Optional

__all__ = [
    "JSONResponse",
    "RedirectResponse",
    "Response",
]


class Response:
    """响应基类桩，保留 status_code 语义"""

    media_type: Optional[str] = None

    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: Optional[dict] = None,
        media_type: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.status_code = status_code
        self.headers = headers or {}
        self.body = content
        if media_type is not None:
            self.media_type = media_type
        self._kwargs = kwargs

    def __repr__(self) -> str:
        return f"<stub {type(self).__name__} status_code={self.status_code}>"


class JSONResponse(Response):
    """JSON 响应桩，记录原始 content，不做序列化"""

    media_type = "application/json"

    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: Optional[dict] = None,
        media_type: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            **kwargs,
        )
        self.content = content


class RedirectResponse(Response):
    """重定向响应桩，仅记录目标地址"""

    def __init__(
        self,
        url: str = "",
        status_code: int = 307,
        headers: Optional[dict] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            content=None,
            status_code=status_code,
            headers=headers,
            **kwargs,
        )
        self.url = url
