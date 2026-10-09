"""
``starlette`` 宿主桩（stub）

**为什么需要这个桩**

``starlette`` 由 MoviePilot 宿主提供（``fastapi`` 的底层依赖，
见 MP V3 的 ``pyproject.toml`` / ``uv.lock``），插件并不把它声明为自身依赖。
真实运行环境（MP V3 容器）能导入，但自包含测试套件没有宿主，
于是子进程以包整体加载 ``p115lite`` 时，
``mcp/manager.py`` 顶层的 ``from starlette.responses import ...`` 会失败。

本桩只提供导入期需要的最小符号，**不实现任何 ASGI 行为**：
被测代码只在 ``handle_sse`` / ``handle_messages`` 里构造响应对象，
测试断言的是 Rust 降级逻辑，不会真的跑 HTTP 服务。
"""

__all__ = ["responses"]
