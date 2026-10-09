"""
FastAPI 宿主桩（stub）

**为什么需要这个桩**

``fastapi`` 由 MoviePilot 宿主提供，插件并不把它声明为自身依赖
（见 ``requirements.txt`` —— 那里没有 fastapi）。插件代码在模块顶层
``from fastapi import Request`` 这类导入，是因为运行时宿主一定能提供。

但自包含测试套件（``tests/_stub_host``）没有宿主，于是：

* 测试**父进程**里，用例只导入 ``helper.strm.full`` 这类子模块，
  不触发插件包 ``__init__.py``，所以看不出问题；
* ``test_rust_free_fallback.TestRustModeFallback`` 必须在**子进程**中以
  ``p115lite`` 包整体加载（该模块用了 4 层相对导入），
  这会执行 ``__init__.py`` —— 于是 ``import fastapi`` 失败，
  CI 报 ``ModuleNotFoundError: No module named 'fastapi'``。

本桩只提供插件实际用到的最小符号集，让被测模块能完成导入。
**它不模拟任何 HTTP 行为**：测试断言的是 Rust 降级逻辑，
不会真的发起请求或构造响应。
"""

from typing import Any, Optional

__all__ = [
    "Body",
    "Depends",
    "Query",
    "Request",
    "Response",
    "status",
]


class Request:
    """
    HTTP 请求桩

    仅作为类型占位：被测代码只在函数签名里标注 ``Request``，
    或在拿到实例后按需取属性，不会真正调用框架。
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs
        # 宿主代码常见访问点，给出宽松默认值避免 AttributeError
        self.headers: dict = kwargs.get("headers") or {}
        self.query_params: dict = kwargs.get("query_params") or {}
        self.cookies: dict = kwargs.get("cookies") or {}
        self.client: Optional[Any] = kwargs.get("client")
        self.url: Optional[Any] = kwargs.get("url")

    async def body(self) -> bytes:
        """返回请求体（桩固定为空）"""
        return b""

    async def json(self) -> Any:
        """解析 JSON 请求体（桩固定为 None）"""
        return None


class Response:
    """
    HTTP 响应桩

    保留 ``status_code`` / ``media_type`` / ``content`` 三个构造参数，
    与真实签名对齐，便于被测代码无感使用。
    """

    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: Optional[dict] = None,
        media_type: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.status_code = status_code
        self.media_type = media_type
        self.headers = headers or {}
        self.body = content
        self._kwargs = kwargs

    def __repr__(self) -> str:
        return f"<stub Response status_code={self.status_code}>"


def Body(default: Any = None, **kwargs: Any) -> Any:
    """请求体参数占位，原样返回默认值"""
    return default


def Query(default: Any = None, **kwargs: Any) -> Any:
    """查询参数占位，原样返回默认值"""
    return default


def Depends(dependency: Any = None, **kwargs: Any) -> Any:
    """
    依赖注入占位

    原样返回 ``dependency``：插件在导入期不会解依赖，
    只有真实框架接管路由时才会调用它。
    """
    return dependency


class _Status:
    """
    HTTP 状态码常量集合

    只补齐插件实际引用到的值；其余通过 ``__getattr__`` 兜底为 0，
    避免个别常量缺失导致导入期报错。
    """

    HTTP_200_OK = 200
    HTTP_201_CREATED = 201
    HTTP_204_NO_CONTENT = 204
    HTTP_301_MOVED_PERMANENTLY = 301
    HTTP_302_FOUND = 302
    HTTP_304_NOT_MODIFIED = 304
    HTTP_400_BAD_REQUEST = 400
    HTTP_401_UNAUTHORIZED = 401
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404
    HTTP_405_METHOD_NOT_ALLOWED = 405
    HTTP_409_CONFLICT = 409
    HTTP_422_UNPROCESSABLE_ENTITY = 422
    HTTP_429_TOO_MANY_REQUESTS = 429
    HTTP_500_INTERNAL_SERVER_ERROR = 500
    HTTP_502_BAD_GATEWAY = 502
    HTTP_503_SERVICE_UNAVAILABLE = 503
    HTTP_504_GATEWAY_TIMEOUT = 504

    def __getattr__(self, name: str) -> int:
        # 未显式声明的状态码常量统一兜底，保证导入期不中断
        if name.startswith("HTTP_"):
            return 0
        raise AttributeError(name)


status = _Status()
