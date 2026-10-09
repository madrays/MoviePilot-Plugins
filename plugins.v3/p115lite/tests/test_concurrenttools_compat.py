"""
python-concurrenttools 兼容别名测试模块

覆盖 utils/concurrenttools_compat.py 的"有条件兼容别名"逻辑：

- 环境只有新名（python-concurrenttools 0.1.9：thread_conmap / async_conmap）
  时，把新名别名回 p115client 期望的旧名（threadpool_map / taskgroup_map）；
- 环境已有旧名（0.1.8）时不做任何改动；
- 新旧名都缺失时不写入不存在的符号；
- 重复调用幂等；concurrenttools 不可导入时静默返回空列表。

运行方式:
    cd plugins.v3/p115lite
    PYTHONPATH=. python -m unittest tests.test_concurrenttools_compat -v
"""

import sys
from types import ModuleType
from typing import Any, Dict
from unittest import TestCase
from unittest.mock import patch

from utils.concurrenttools_compat import (
    LEGACY_CONCURRENTTOOLS_ALIASES,
    ensure_legacy_concurrenttools_aliases,
)


def _fake_concurrenttools(**attrs: Any) -> ModuleType:
    """
    构造一个只带指定属性的假 concurrenttools 模块

    :param attrs: 属性名 -> 属性值
    :return ModuleType: 假模块
    """

    module = ModuleType("concurrenttools")
    for name, value in attrs.items():
        setattr(module, name, value)
    return module


class TestEnsureLegacyConcurrenttoolsAliases(TestCase):
    """ensure_legacy_concurrenttools_aliases 的别名挂载与边界行为"""

    def _run_with(self, module: Any) -> Any:
        """
        在替换后的 concurrenttools 模块下调用被测函数

        :param module: 假模块或 None（None 表示 import 失败）
        :return Any: 被测函数返回值
        """

        with patch.dict(sys.modules, {"concurrenttools": module}):
            return ensure_legacy_concurrenttools_aliases()

    def test_aliases_new_names_back_to_legacy(self) -> None:
        """0.1.9 环境：旧名缺失、新名存在时挂上别名，且指向同一对象"""

        thread_conmap = object()
        async_conmap = object()
        module = _fake_concurrenttools(
            thread_conmap=thread_conmap,
            async_conmap=async_conmap,
        )

        applied = self._run_with(module)

        self.assertEqual(
            applied,
            ["threadpool_map", "taskgroup_map"],
            "应报告两个由新名挂载的旧名",
        )
        self.assertIs(module.threadpool_map, thread_conmap)
        self.assertIs(module.taskgroup_map, async_conmap)

    def test_no_change_when_legacy_names_present(self) -> None:
        """0.1.8 环境：旧名已在，不新增也不覆盖任何属性"""

        threadpool_map = object()
        taskgroup_map = object()
        module = _fake_concurrenttools(
            threadpool_map=threadpool_map,
            taskgroup_map=taskgroup_map,
        )

        applied = self._run_with(module)

        self.assertEqual(applied, [], "旧名已存在时不应挂别名")
        self.assertIs(module.threadpool_map, threadpool_map)
        self.assertIs(module.taskgroup_map, taskgroup_map)
        self.assertFalse(hasattr(module, "thread_conmap"))
        self.assertFalse(hasattr(module, "async_conmap"))

    def test_skips_missing_new_name(self) -> None:
        """新旧名都缺失：只挂能挂的那条，不写入不存在的符号"""

        async_conmap = object()
        module = _fake_concurrenttools(async_conmap=async_conmap)

        applied = self._run_with(module)

        self.assertEqual(applied, ["taskgroup_map"], "threadpool_map 无对应新名，应跳过")
        self.assertFalse(hasattr(module, "threadpool_map"))
        self.assertIs(module.taskgroup_map, async_conmap)

    def test_idempotent(self) -> None:
        """重复调用幂等：第二次不再重复挂载"""

        module = _fake_concurrenttools(
            thread_conmap=object(),
            async_conmap=object(),
        )

        first = self._run_with(module)
        second = self._run_with(module)

        self.assertEqual(first, ["threadpool_map", "taskgroup_map"])
        self.assertEqual(second, [], "重复调用不应再次挂载")

    def test_silent_when_module_unavailable(self) -> None:
        """concurrenttools 不可导入时静默返回空列表，不抛异常"""

        self.assertEqual(self._run_with(None), [])

    def test_alias_table_matches_p115client_expectation(self) -> None:
        """别名对照表与 p115client 0.0.9.6.5.1 的 import 站保持一致"""

        self.assertEqual(
            dict(LEGACY_CONCURRENTTOOLS_ALIASES),
            {"threadpool_map": "thread_conmap", "taskgroup_map": "async_conmap"},
        )
