"""
``starlette.responses`` 宿主桩（stub）

``mcp/manager.py`` 用到两个符号：

* ``Response("Accepted", status_code=202)`` —— 纯文本响应，
  插件只读它的 ``status_code``；
* ``StreamingResponse(generator, media_type=..., headers=...)`` —— SSE 流响应，
  插件只做构造，不消费生成器。

因此这里保留与真实签名对齐的构造参数并记录到实例属性，
不做编码、不做 ASGI 调用，避免为测试引入不必要的行为耦合。
"""

from typing import Any, AsyncIterator, Iterable, Iterator, Optional, Union

__all__ = [
    "Response",
    "StreamingResponse",
]


class Response:
    """
    HTTP 响应桩

    与 Starlette 真实签名保持一致（``content`` / ``status_code`` /
    ``headers`` / ``media_type``），并额外记录 ``body``，
    便于被测代码按真实习惯读取。
    """

    media_type: Optional[str] = None
    charset = "utf-8"

    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: Optional[dict] = None,
        media_type: Optional[str] = None,
        background: Optional[Any] = None,
    ) -> None:
        self.status_code = status_code
        self.media_type = media_type or type(self).media_type
        self.headers = dict(headers or {})
        self.background = background

        if content is None:
            body = b""
        elif isinstance(content, bytes):
            body = content
        elif isinstance(content, str):
            body = content.encode(self.charset)
            self.headers.setdefault(
                "content-type", f"text/plain; charset={self.charset}"
            )
        else:
            body = str(content).encode(self.charset)
        self.body = body

    def __repr__(self) -> str:
        return f"<stub Response status_code={self.status_code}>"


class StreamingResponse(Response):
    """
    流式响应桩

    保存 ``body_iterator``（可能是同步或异步可迭代对象）而不消费它 ——
    Starlette 真实实现同样不会在构造时就遍历生成器，
    因此这里保持惰性，行为一致且不会意外推进 SSE 事件流。
    """

    media_type = None

    def __init__(
        self,
        content: Union[Iterable[Any], AsyncIterator[Any]],
        status_code: int = 200,
        headers: Optional[dict] = None,
        media_type: Optional[str] = None,
        background: Optional[Any] = None,
    ) -> None:
        self.body_iterator = content
        super().__init__(
            content=None,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )

    def __repr__(self) -> str:
        return (
            f"<stub StreamingResponse status_code={self.status_code} "
            f"media_type={self.media_type!r}>"
        )
