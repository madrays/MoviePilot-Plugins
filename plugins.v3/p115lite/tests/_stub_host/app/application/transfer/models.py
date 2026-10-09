"""
``app.application.transfer.models`` 包替身。

真实 V3 已将 ``TransferTask`` 从 ``app.schemas`` 迁入此路径
（见 app/application/transfer/models.py 的注释：为避免 import 环，
整理链的进程内工作项已移出 ``app.schemas``）。

本桩复用 ``app.schemas.models`` 中的同一实现，使插件修复后的新导入路径
``from app.application.transfer.models import TransferTask`` 在本地测试环境可用。
"""

from app.schemas.models import TransferTask  # noqa: F401

__all__ = ["TransferTask"]
