"""导出目录树迭代器的错误转换回归测试"""

import ast
from pathlib import Path
from typing import Any, Generator, Iterator
from unittest import TestCase


def _load_guard():
    """
    仅加载守卫函数与其依赖的告警文案，避免导入网盘客户端及 MoviePilot 运行时

    :return tuple: (守卫函数, 异常替身)
    """
    source = Path(__file__).resolve().parents[1] / "helper/strm/increment.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    hint = next(
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and getattr(node.targets[0], "id", "") == "_EXPORT_CLIENT_STATE_HINT"
    )
    func = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "_iter_export_dir_lines"
    )

    class ItertreeClientStateError(Exception):
        """测试用的异常替身。"""

    namespace = {
        "Any": Any,
        "Generator": Generator,
        "Iterator": Iterator,
        "ItertreeClientStateError": ItertreeClientStateError,
    }
    module = ast.Module(body=[hint, func], type_ignores=[])
    exec(compile(module, str(source), "exec"), namespace)
    return namespace[func.name], ItertreeClientStateError


class TestExportDirLineGuard(TestCase):
    """验证导出目录树迭代异常被转换为可读的领域错误"""

    def setUp(self):
        """加载被测守卫与异常替身"""
        self.guard, self.error = _load_guard()

    def test_passthrough_lines(self):
        """正常迭代器逐行透传，内容不变"""
        result = list(self.guard(iter(["电影", "电影/阿凡达.mkv"]), "/影视库/电影"))
        self.assertEqual(result, ["电影", "电影/阿凡达.mkv"])

    def test_lazy_type_error_converted(self):
        """库内惰性 TypeError（not iterable）转换为领域错误并给出处置指向"""
        def boom():
            """模拟 p115client 触发 yield from 非可迭代对象"""
            raise TypeError("'P115ClientWithTimeout' object is not iterable")
            yield  # pragma: no cover

        with self.assertRaises(self.error) as ctx:
            list(self.guard(boom(), "/影视库/电影"))
        message = str(ctx.exception)
        self.assertIn("P115ClientWithTimeout", message)
        self.assertIn("115 Cookie", message)
        self.assertIn("/影视库/电影", message)
    def test_non_iterable_argument(self):
        """传入不可迭代对象时同样转换为领域错误"""
        with self.assertRaises(self.error) as ctx:
            list(self.guard(object(), "/影视库/电影"))
        self.assertIn("不可迭代", str(ctx.exception))

    def test_key_error_converted(self):
        """库内 KeyError（如 authorization）转换为领域错误"""
        def boom():
            """模拟 115 返回结构缺字段"""
            raise KeyError("authorization")
            yield  # pragma: no cover

        with self.assertRaises(self.error) as ctx:
            list(self.guard(boom(), "/影视库/动漫"))
        self.assertIn("KeyError", str(ctx.exception))

    def test_error_after_partial_items(self):
        """先产出部分行再抛错时，已产出的行仍然可见"""
        def partial():
            """先产出一行，再触发库内异常"""
            yield "电影"
            raise TypeError("'P115ClientWithTimeout' object is not iterable")

        collected = []
        with self.assertRaises(self.error):
            for line in self.guard(partial(), "/影视库/电影"):
                collected.append(line)
        self.assertEqual(collected, ["电影"])
