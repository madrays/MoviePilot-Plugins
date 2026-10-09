"""
Python 3.14 无 Rust 扩展时的降级路径测试模块

背景
----
插件的三个 Rust 加速扩展（``txt_tree_storage`` / ``full_strm_sync`` /
``share_strm_scan``）以 wheel 随插件 wheels/ 分发，但 3.13 宿主、或未随包分发
wheel 时会缺失。这三个依赖始终是可选的，插件必须能在它们全部缺失时：

1. 正常导入（不能在模块顶层 import 就炸）
2. 走纯 Python 降级路径，且**语义与 Rust 路径一致**

本模块用 ``patch(..., None)`` 模拟扩展缺失，逐项校验降级后的行为。
"""

import sys
from types import ModuleType

# 注入 version mock，避免 CI 中插件目录的 version.py 被优先加载
_version_mod = ModuleType("version")
_version_mod.APP_VERSION = "test"
_version_mod.FRONTEND_VERSION = "test"
sys.modules["version"] = _version_mod

import subprocess  # noqa: E402

from pathlib import Path  # noqa: E402
from tempfile import TemporaryDirectory  # noqa: E402
from unittest import TestCase  # noqa: E402
from unittest.mock import patch  # noqa: E402

from utils.tree import TxtFileStorage  # noqa: E402


class TestTxtFileStorageWithoutRust(TestCase):
    """txt_tree_storage 缺失时，TxtFileStorage 的纯 Python 后备"""

    def _storage(self, tmpdir: str, name: str = "tree.txt"):
        with patch("utils.tree.txt_tree_storage", None):
            return TxtFileStorage(Path(tmpdir) / name)

    def test_add_paths_writes_every_path(self):
        """add_paths 应把非空路径逐行写入文件"""
        with TemporaryDirectory() as tmpdir:
            storage = self._storage(tmpdir)
            storage.add_paths(["/a/1.mkv", "/a/2.mkv", "/a/3.mkv"])

            lines = (Path(tmpdir) / "tree.txt").read_text(encoding="utf-8").splitlines()
            self.assertEqual(lines, ["/a/1.mkv", "/a/2.mkv", "/a/3.mkv"])

    def test_add_paths_skips_empty_when_appending(self):
        """追加模式下空路径不应写入"""
        with TemporaryDirectory() as tmpdir:
            storage = self._storage(tmpdir)
            storage.add_paths(["/a/1.mkv"])
            storage.add_paths(["", "/a/2.mkv", None], append=True)

            lines = (Path(tmpdir) / "tree.txt").read_text(encoding="utf-8").splitlines()
            self.assertEqual(lines, ["/a/1.mkv", "/a/2.mkv"])

    def test_add_paths_overwrite_replaces_content(self):
        """append=False 应覆盖而非追加"""
        with TemporaryDirectory() as tmpdir:
            storage = self._storage(tmpdir)
            storage.add_paths(["/old/1.mkv", "/old/2.mkv"])
            storage.add_paths(["/new/1.mkv"])

            lines = (Path(tmpdir) / "tree.txt").read_text(encoding="utf-8").splitlines()
            self.assertEqual(lines, ["/new/1.mkv"])

    def test_compare_trees_returns_only_self_unique(self):
        """compare_trees 应只返回 self 有而 other 没有的路径"""
        with TemporaryDirectory() as tmpdir:
            left = self._storage(tmpdir, "left.txt")
            right = self._storage(tmpdir, "right.txt")
            left.add_paths(["/a/1.mkv", "/a/2.mkv", "/a/3.mkv"])
            right.add_paths(["/a/2.mkv", "/a/9.mkv"])

            self.assertEqual(list(left.compare_trees(right)), ["/a/1.mkv", "/a/3.mkv"])

    def test_compare_trees_rejects_mismatched_type(self):
        """与非 TxtFileStorage 比较应抛 TypeError"""
        with TemporaryDirectory() as tmpdir:
            storage = self._storage(tmpdir)
            with self.assertRaises(TypeError):
                list(storage.compare_trees(object()))

    def test_compare_trees_lines_matches_compare_trees(self):
        """行号流与路径流必须一一对应（行号可回查到同一路径）"""
        with TemporaryDirectory() as tmpdir:
            left = self._storage(tmpdir, "left.txt")
            right = self._storage(tmpdir, "right.txt")
            left.add_paths(["/a/1.mkv", "/a/2.mkv", "/a/3.mkv", "/a/4.mkv"])
            right.add_paths(["/a/2.mkv"])

            lines = list(left.compare_trees_lines(right))
            self.assertEqual(lines, [1, 3, 4])

            # 行号回查必须得到 compare_trees 产出的同顺序路径
            paths = list(left.compare_trees(right))
            self.assertEqual(
                [left.get_path_by_line_number(n) for n in lines], paths
            )

    def test_get_path_by_line_number_boundary(self):
        """行号边界：0/负数/越界都返回 None"""
        with TemporaryDirectory() as tmpdir:
            storage = self._storage(tmpdir)
            storage.add_paths(["/a/1.mkv", "/a/2.mkv"])

            self.assertEqual(storage.get_path_by_line_number(1), "/a/1.mkv")
            self.assertEqual(storage.get_path_by_line_number(2), "/a/2.mkv")
            self.assertIsNone(storage.get_path_by_line_number(0))
            self.assertIsNone(storage.get_path_by_line_number(-1))
            self.assertIsNone(storage.get_path_by_line_number(3))

    def test_count_ignores_blank_lines(self):
        """count 只统计有效条目，空行不计入"""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tree.txt"
            path.write_text("/a/1.mkv\n\n/a/2.mkv\n\n", encoding="utf-8")
            storage = self._storage(tmpdir)
            self.assertEqual(storage.count(), 2)

    def test_count_on_missing_file(self):
        """文件不存在时 count 应为 0 而不是抛异常"""
        with TemporaryDirectory() as tmpdir:
            storage = self._storage(tmpdir, "not_exists.txt")
            self.assertEqual(storage.count(), 0)
            self.assertEqual(list(storage.compare_trees(self._storage(tmpdir, "other.txt"))), [])

    def test_clear_truncates_file(self):
        """clear 应清空文件且 count 归零"""
        with TemporaryDirectory() as tmpdir:
            storage = self._storage(tmpdir)
            storage.add_paths(["/a/1.mkv"])
            storage.clear()

            self.assertEqual(storage.count(), 0)
            self.assertEqual(
                (Path(tmpdir) / "tree.txt").read_text(encoding="utf-8"), ""
            )

    def test_roundtrip_matches_rust_semantics(self):
        """完整往返：写入→比较→按行号取路径→计数→清空"""
        with TemporaryDirectory() as tmpdir:
            pan = self._storage(tmpdir, "pan.txt")
            local = self._storage(tmpdir, "local.txt")

            pan_paths = [f"/pan/{i}.mkv" for i in range(10)]
            local_paths = [f"/pan/{i}.mkv" for i in range(0, 10, 2)]
            pan.add_paths(pan_paths)
            local.add_paths(local_paths)

            missing = list(pan.compare_trees(local))
            self.assertEqual(sorted(missing), sorted(set(pan_paths) - set(local_paths)))

            self.assertEqual(pan.count(), 10)
            self.assertEqual(local.count(), 5)

            for line_number in pan.compare_trees_lines(local):
                self.assertIsNotNone(pan.get_path_by_line_number(line_number))


class TestPurePythonMatchesRust(TestCase):
    """
    纯 Python 后备与 Rust 实现的等价性对比（宿主装了扩展时才生效）

    沙箱/宿主若装了 txt_tree_storage，就用同一份数据分别跑两条路径，
    断言结果一致——保证降级不会悄悄改变语义。
    """

    def setUp(self):
        if TxtFileStorage(Path("/tmp/_probe_tree.txt"))._rust is None:
            self.skipTest("宿主未安装 txt_tree_storage，跳过 Rust 等价性对比")

    def test_compare_and_count_identical(self):
        """两條路径的 compare_trees / count / 行号查询结果必须一致"""
        with TemporaryDirectory() as tmpdir:
            pan_paths = [f"/pan/{i}.mkv" for i in range(20)]
            local_paths = [f"/pan/{i}.mkv" for i in range(0, 20, 3)]

            rust_pan = TxtFileStorage(Path(tmpdir) / "rust_pan.txt")
            rust_local = TxtFileStorage(Path(tmpdir) / "rust_local.txt")
            rust_pan.add_paths(pan_paths)
            rust_local.add_paths(local_paths)

            with patch("utils.tree.txt_tree_storage", None):
                py_pan = TxtFileStorage(Path(tmpdir) / "py_pan.txt")
                py_local = TxtFileStorage(Path(tmpdir) / "py_local.txt")
                py_pan.add_paths(pan_paths)
                py_local.add_paths(local_paths)

            self.assertEqual(rust_pan.count(), py_pan.count())
            self.assertEqual(
                sorted(rust_pan.compare_trees(rust_local)),
                sorted(py_pan.compare_trees(py_local)),
            )
            self.assertEqual(
                sorted(rust_pan.compare_trees_lines(rust_local)),
                sorted(py_pan.compare_trees_lines(py_local)),
            )
            for line_number in rust_pan.compare_trees_lines(rust_local):
                self.assertEqual(
                    rust_pan.get_path_by_line_number(line_number),
                    py_pan.get_path_by_line_number(line_number),
                )

    def test_clear_and_recount_identical(self):
        """clear 后两条路径的 count 都应归零"""
        with TemporaryDirectory() as tmpdir:
            rust_tree = TxtFileStorage(Path(tmpdir) / "rust.txt")
            rust_tree.add_paths(["/a/1.mkv", "/a/2.mkv"])
            rust_tree.clear()

            with patch("utils.tree.txt_tree_storage", None):
                py_tree = TxtFileStorage(Path(tmpdir) / "py.txt")
                py_tree.add_paths(["/a/1.mkv", "/a/2.mkv"])
                py_tree.clear()

            self.assertEqual(rust_tree.count(), 0)
            self.assertEqual(py_tree.count(), 0)


class TestRustModeFallback(TestCase):
    """
    full_strm_sync 缺失时，Rust 加速开关必须自动回落

    helper.strm.full 用了 4 层相对导入，必须以插件包整体加载，
    因此在独立子进程里验证，避免污染同进程的模块/类引用。
    """

    _PLUGIN_PARENT = Path(__file__).resolve().parent.parent.parent
    _STUB_HOST = Path(__file__).resolve().parent.parent / "tests" / "_stub_host"

    def _run_in_subprocess(self, body: str, drop_rust: bool = True):
        """
        在子进程里以 p115lite 包方式执行断言脚本

        :param body (str): 子进程要执行的 Python 语句（可用 full 变量）
        :param drop_rust (bool): 是否屏蔽 Rust 扩展模拟缺失
        :return CompletedProcess: 子进程结果
        """
        guard = (
            "import sys;"
            "sys.modules['full_strm_sync']=None;"
            "sys.modules['txt_tree_storage']=None;"
            "sys.modules['share_strm_scan']=None;"
            if drop_rust
            else ""
        )
        script = (
            guard
            + "sys.path[:0]=[sys.argv[2], sys.argv[1]];"
            + "from p115lite.helper.strm import full;"
            + body
        )
        return subprocess.run(
            [sys.executable, "-c", script, str(self._PLUGIN_PARENT), str(self._STUB_HOST)],
            capture_output=True,
            text=True,
            timeout=180,
        )

    def test_disabled_stays_disabled(self):
        """配置未开启时无论扩展是否存在都应为 False"""
        result = self._run_in_subprocess(
            "assert full.resolve_rust_mode(False) is False;print('OK')"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK", result.stdout)

    def test_enabled_without_extension_falls_back(self):
        """开启加速但扩展缺失时应回落到 False，而不是崩溃"""
        result = self._run_in_subprocess(
            "assert full.Processor is None;"
            "assert full.resolve_rust_mode(True) is False;print('OK')"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK", result.stdout)

    def test_enabled_with_extension_keeps_enabled(self):
        """扩展可用且开启加速时应保持 True"""
        result = self._run_in_subprocess(
            "full.Processor=object();"
            "assert full.resolve_rust_mode(True) is True;print('OK')"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK", result.stdout)

    def test_full_module_imports_without_rust(self):
        """无 Rust 扩展时 helper.strm.full 本身必须能导入"""
        result = self._run_in_subprocess(
            "assert full.Processor is None;"
            "assert full.rust_core_version is None;print('OK')"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK", result.stdout)


def _load_pure_scanner():
    """
    按文件路径加载纯 Python 扫描器模块

    pure_scanner 只依赖宿主的 app.sdk.logging（绝对导入），
    因此可以脱离插件包单独加载，避免触发整个插件的初始化。
    """
    import importlib.util

    module_path = Path(__file__).resolve().parent.parent / "helper" / "strm" / "share" / "pure_scanner.py"
    spec = importlib.util.spec_from_file_location("_pure_scanner_under_test", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestPureShareStrmScanCache(TestCase):
    """纯 Python 分享 STRM 扫描器"""

    BASE = "http://mp.local/api/v1/plugin/P115Lite/redirect_url"

    def setUp(self):
        self.scanner_module = _load_pure_scanner()
        self.Pair = self.scanner_module.Pair
        self.PureShareStrmScanCache = self.scanner_module.PureShareStrmScanCache

    def _write(self, root: Path, rel: str, share_code: str, receive_code: str):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"{self.BASE}?share_code={share_code}&receive_code={receive_code}&id=123",
            encoding="utf-8",
        )
        return path

    def test_scan_collects_unique_pairs(self):
        """scan 应去重并返回所有出现过的分享组合"""
        PureShareStrmScanCache = self.PureShareStrmScanCache

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._write(root, "a/1.strm", "abc123", "xyz")
            self._write(root, "b/2.strm", "abc123", "xyz")  # 同组合不同文件
            self._write(root, "b/3.strm", "def456", "")

            scaner = PureShareStrmScanCache()
            pairs = scaner.scan(root)

            self.assertEqual(len(pairs), 2)
            self.assertIn(("abc123", "xyz"), pairs)
            self.assertIn(("def456", ""), pairs)

    def test_paths_for_many_groups_paths(self):
        """同一组合的多个 STRM 应聚合到同一 key 下"""
        Pair, PureShareStrmScanCache = self.Pair, self.PureShareStrmScanCache

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            first = self._write(root, "a/1.strm", "abc123", "xyz")
            second = self._write(root, "b/2.strm", "abc123", "xyz")
            self._write(root, "c/3.strm", "other", "key")

            scaner = PureShareStrmScanCache()
            scaner.scan(root)
            mapping = scaner.paths_for_many(root, [("abc123", "xyz")])

            self.assertEqual(
                sorted(mapping[Pair("abc123", "xyz")]),
                sorted([first.as_posix(), second.as_posix()]),
            )

    def test_paths_for_many_unknown_pair_returns_empty(self):
        """查询不存在的组合应返回空列表而非 KeyError"""
        Pair, PureShareStrmScanCache = self.Pair, self.PureShareStrmScanCache

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._write(root, "a/1.strm", "abc123", "xyz")

            scaner = PureShareStrmScanCache()
            mapping = scaner.paths_for_many(root, [Pair("nope", "nope")])

            self.assertEqual(mapping[Pair("nope", "nope")], [])

    def test_ignores_non_strm_and_unparsable(self):
        """非 .strm 文件与不含分享信息的文件都应被忽略"""
        PureShareStrmScanCache = self.PureShareStrmScanCache

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "readme.txt").write_text("share_code=abc123&receive_code=x", encoding="utf-8")
            (root / "empty.strm").write_text("no share info here", encoding="utf-8")

            scaner = PureShareStrmScanCache()
            self.assertEqual(scaner.scan(root), [])

    def test_invalidate_drops_stale_cache(self):
        """
        invalidate 必须真的丢弃旧缓存

        断言方式：先扫描取得结果，再删掉源文件；若 invalidate 只是空实现，
        paths_for_many 会命中旧缓存继续返回已删除的路径（脏数据），
        只有真正清空缓存、重新扫描才会返回空。
        """
        Pair, PureShareStrmScanCache = self.Pair, self.PureShareStrmScanCache

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            target = self._write(root, "a/1.strm", "abc123", "xyz")

            scaner = PureShareStrmScanCache()
            scaner.scan(root)
            self.assertEqual(
                len(scaner.paths_for_many(root, [("abc123", "xyz")])[Pair("abc123", "xyz")]),
                1,
            )

            # 源文件删除后必须重新扫描，而不是拿出缓存里的脏数据
            target.unlink()
            scaner.invalidate()

            mapping = scaner.paths_for_many(root, [("abc123", "xyz")])
            self.assertEqual(mapping[Pair("abc123", "xyz")], [])

    def test_pair_is_hashable_and_unpackable(self):
        """Pair 必须同时支持字典键与二元组解包（对齐 Rust 版用法）"""
        Pair = self.Pair

        pair = Pair("abc123", "xyz")
        share_code, receive_code = pair
        self.assertEqual((share_code, receive_code), ("abc123", "xyz"))
        self.assertEqual({pair: 1}[Pair("abc123", "xyz")], 1)

    def test_parses_115_share_short_link(self):
        """兼容 115 分享短链格式"""
        PureShareStrmScanCache = self.PureShareStrmScanCache

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "a").mkdir(parents=True, exist_ok=True)
            (root / "a/1.strm").write_text(
                "https://115.com/s/abc123xyz?code=9a9a", encoding="utf-8"
            )

            scaner = PureShareStrmScanCache()
            self.assertEqual(list(scaner.scan(root)), [("abc123xyz", "9a9a")])


class TestOptionalImportSurvivesMissingRust(TestCase):
    """Rust 扩展缺失时，相关模块仍应可导入"""

    def test_tree_module_imports_without_rust(self):
        """
        utils.tree 在 txt_tree_storage 缺失时可导入且不抛错

        用独立子进程验证：reload 会替换模块内的类对象，
        污染同进程里其它用例持有的旧引用，因此不能在原地 reload。
        """
        plugin_dir = Path(__file__).resolve().parent.parent
        stub_host = plugin_dir / "tests" / "_stub_host"
        script = (
            "import sys;"
            "sys.modules['txt_tree_storage'] = None;"  # import 会抛 ImportError
            "sys.path[:0] = [sys.argv[1], sys.argv[2]];"
            "import utils.tree;"
            "assert utils.tree.txt_tree_storage is None;"
            "print('OK')"
        )
        result = subprocess.run(
            [sys.executable, "-c", script, str(stub_host), str(plugin_dir)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"无 Rust 扩展时 utils.tree 导入失败：{result.stderr}",
        )
        self.assertIn("OK", result.stdout)


if __name__ == "__main__":
    from unittest import main

    main(verbosity=2)
