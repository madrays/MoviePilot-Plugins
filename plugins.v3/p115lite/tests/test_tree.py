"""
DirectoryTree / RedisStorage / TxtFileStorage 测试模块
"""

import sys
from types import ModuleType

# 注入 version mock，避免 CI 中插件目录的 version.py 被优先加载
_version_mod = ModuleType("version")
_version_mod.APP_VERSION = "test"
_version_mod.FRONTEND_VERSION = "test"
sys.modules["version"] = _version_mod

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import MagicMock, patch

from utils.tree import DirectoryTree, RedisStorage, TxtFileStorage


class TestDirectoryTreeBackendSwitch(TestCase):
    """测试 DirectoryTree 后端切换与初始化"""

    @patch("utils.tree.settings")
    def test_force_backend_txt_overrides_redis_setting(self, mock_settings):
        """force_backend='txt' 应强制使用 TxtFileStorage，忽略 settings"""
        mock_settings.CACHE_BACKEND_TYPE = "redis"

        with TemporaryDirectory() as tmpdir:
            tree = DirectoryTree(Path(tmpdir) / "test.txt", force_backend="txt")
            self.assertIsInstance(tree._storage, TxtFileStorage)

    @patch("utils.tree.settings")
    def test_force_backend_redis_overrides_txt_setting(self, mock_settings):
        """force_backend='redis' 应强制使用 RedisStorage，忽略 settings"""
        mock_settings.CACHE_BACKEND_TYPE = "txt"

        with TemporaryDirectory() as tmpdir:
            tree = DirectoryTree(Path(tmpdir) / "test.txt", force_backend="redis")
            self.assertIsInstance(tree._storage, RedisStorage)

    @patch("utils.tree.settings")
    def test_switch_storage_redis_to_txt(self, mock_settings):
        """从 Redis 切换到 TXT 应清空旧数据并创建新的 TxtFileStorage"""
        mock_settings.CACHE_BACKEND_TYPE = "redis"

        with TemporaryDirectory() as tmpdir:
            tree = DirectoryTree(Path(tmpdir) / "test.txt", force_backend="redis")
            tree.switch_storage("txt")
            self.assertIsInstance(tree._storage, TxtFileStorage)

    @patch("utils.tree.settings")
    def test_switch_storage_txt_to_redis(self, mock_settings):
        """从 TXT 切换到 Redis 应清空旧数据并创建新的 RedisStorage"""
        mock_settings.CACHE_BACKEND_TYPE = "txt"

        with TemporaryDirectory() as tmpdir:
            tree = DirectoryTree(Path(tmpdir) / "test.txt", force_backend="txt")
            tree.switch_storage("redis")
            self.assertIsInstance(tree._storage, RedisStorage)

    @patch("utils.tree.settings")
    def test_switch_storage_no_op_when_same(self, mock_settings):
        """切换目标与当前后端相同时，不应执行任何操作"""
        mock_settings.CACHE_BACKEND_TYPE = "redis"

        with TemporaryDirectory() as tmpdir:
            tree = DirectoryTree(Path(tmpdir) / "test.txt", force_backend="redis")
            original_storage = tree._storage
            tree.switch_storage("redis")
            self.assertIs(tree._storage, original_storage)


class TestRedisStorageAddPaths(TestCase):
    """测试 RedisStorage.add_paths 的 OOM 捕获与 TTL"""

    @patch("utils.tree.RedisHelper")
    def test_oom_raises_memory_error(self, mock_redis_helper):
        """Redis OOM 时应抛出 MemoryError，并包含配置提示"""
        mock_client = MagicMock()
        mock_pipe = MagicMock()
        mock_client.pipeline.return_value = mock_pipe
        mock_pipe.execute.side_effect = Exception(
            "OOM command not allowed when used memory > 'maxmemory'"
        )
        mock_redis_helper.return_value.client = mock_client

        storage = RedisStorage("test_tree")
        with self.assertRaises(MemoryError) as ctx:
            storage.add_paths(["/a/b/c.mkv"])

        self.assertIn("maxmemory", str(ctx.exception))
        self.assertIn("test_tree", str(ctx.exception))

    @patch("utils.tree.RedisHelper")
    def test_success_sets_ttl(self, mock_redis_helper):
        """成功写入后应调用 expire 设置 TTL"""
        mock_client = MagicMock()
        mock_pipe = MagicMock()
        mock_client.pipeline.return_value = mock_pipe
        mock_redis_helper.return_value.client = mock_client

        storage = RedisStorage("test_tree")
        storage.add_paths(["/a/b/c.mkv"])

        mock_pipe.expire.assert_any_call("dirtree:set:test_tree", 604800)
        mock_pipe.expire.assert_any_call("dirtree:list:test_tree", 604800)
        mock_pipe.execute.assert_called_once()

    @patch("utils.tree.RedisHelper")
    def test_unknown_error_not_wrapped(self, mock_redis_helper):
        """非 OOM 错误应原样抛出，不包装为 MemoryError"""
        mock_client = MagicMock()
        mock_pipe = MagicMock()
        mock_client.pipeline.return_value = mock_pipe
        mock_pipe.execute.side_effect = Exception("random connection error")
        mock_redis_helper.return_value.client = mock_client

        storage = RedisStorage("test_tree")
        with self.assertRaises(Exception) as ctx:
            storage.add_paths(["/a/b/c.mkv"])

        self.assertEqual(str(ctx.exception), "random connection error")


class TestRedisStorageLineNumberBoundary(TestCase):
    """
    RedisStorage.get_path_by_line_number 的非正数行号防护

    这里的 ``line_number <= 0`` 不是可有可无的防御：Redis 的 ``lindex`` 接受负数
    下标，-1 表示"最后一个元素"。若放行 0，会退化成 ``lindex(-1)`` 返回最后一条
    路径——调用方拿到的不是"无效行号"，而是一条**真实但错误**的路径。
    """

    def _storage(self):
        with patch("utils.tree.RedisHelper") as mock_redis_helper:
            mock_redis_helper.return_value.client = MagicMock()
            storage = RedisStorage("test_tree")
        return storage

    def test_get_path_by_line_number_rejects_non_positive(self):
        """0 与负数行号都应返回 None，且不穿透到 Redis"""
        storage = self._storage()

        self.assertIsNone(storage.get_path_by_line_number(0))
        self.assertIsNone(storage.get_path_by_line_number(-1))
        self.assertIsNone(storage.get_path_by_line_number(-100))
        storage.client.lindex.assert_not_called()

    def test_get_path_by_line_number_valid(self):
        """正数行号正常查询，下标换算为 line_number - 1"""
        storage = self._storage()
        storage.client.lindex.return_value = b"/a/1.mkv"

        self.assertEqual(storage.get_path_by_line_number(1), "/a/1.mkv")
        storage.client.lindex.assert_called_once_with("dirtree:list:test_tree", 0)


if __name__ == "__main__":
    from unittest import main

    main(verbosity=2)
