"""
``watchfiles`` 宿主桩（stub）

**为什么需要这个桩**

``watchfiles`` 由 MoviePilot 宿主间接提供（其依赖 ``uvicorn[standard]``
会带入 ``watchfiles``），插件不在自己的 ``requirements.txt`` 里声明它。
真实运行环境（MP V3 容器）能导入，但自包含测试套件没有宿主，
于是子进程以包整体加载 ``p115lite`` 时，
``service/__init__.py`` 顶层的 ``from watchfiles import watch, Change`` 会失败。

本桩只提供导入期需要的最小符号，**不实现真实文件监控**：
被测代码在导入时会引用 ``watch`` / ``Change``，但测试断言的是
Rust 降级逻辑，不会真的启动目录监听。
"""

from typing import Any, AsyncIterator, Iterator, Optional

__all__ = [
    "Change",
    "DefaultFilter",
    "watch",
    "awatch",
]


class Change:
    """
    ``watchfiles`` 的文件变更类型枚举

    真实实现是一个 ``IntEnum``，这里给出功能等价的枚举，
    保证按位比较与成员访问行为一致。
    """

    added = 1
    modified = 2
    deleted = 4

    def __init__(self, value: int = 0) -> None:
        self.value = value

    def __or__(self, other: "Change") -> "Change":
        return Change(self.value | other.value)

    def __and__(self, other: "Change") -> "Change":
        return Change(self.value & other.value)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Change):
            return self.value == other.value
        if isinstance(other, int):
            return self.value == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.value)

    def __repr__(self) -> str:
        return f"<stub Change value={self.value}>"


class DefaultFilter:
    """默认文件过滤器桩，保留 ``__call__`` 接口"""

    def __call__(self, change: Any, path: str) -> bool:
        return True


def watch(
    *paths: Any,
    watch_filter: Optional[Any] = None,
    debounce: int = 1600,
    step: int = 50,
    stop_event: Optional[Any] = None,
    rust_timeout: int = 5000,
    yield_on_timeout: bool = True,
    debug: bool = False,
    raise_interrupt: bool = True,
    force_polling: Optional[bool] = None,
    poll_delay_ms: int = 300,
    recursive: bool = True,
    ignore_permission_denied: Optional[bool] = None,
    **kwargs: Any,
) -> Iterator[set]:
    """
    同步目录监控桩

    立即返回空迭代器：不阻塞、不监听。真实实现在这里会持续 yield
    变更集合，桩只保证调用方能正常拿到迭代对象并安全结束循环。
    """
    return iter(())


async def awatch(*paths: Any, **kwargs: Any) -> AsyncIterator[set]:
    """
    异步目录监控桩

    返回空异步迭代器，语义同上。被测代码 ``async for`` 时会立刻结束。
    """
    return
    yield set()  # pragma: no cover - 让函数成为异步生成器
