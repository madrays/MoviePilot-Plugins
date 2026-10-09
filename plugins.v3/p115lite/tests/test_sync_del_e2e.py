# -*- coding: utf-8 -*-
"""
端到端测试：同步删除的**真实调用链**。

与单元测试的分工
----------------
``test_path_remove_boundary.py`` 单测 ``has_prefix`` / ``PathRemoveUtils``
本身；本文件走**完整链路**，验证这些函数被真正接进删除流程后行为正确：

    ``MediaSyncDelHelper.remove_by_path(path, del_source=True)``
        → ``TransferHBOper.get_transfer_his_by_path_title`` 查历史
        → ``PathUtils.has_prefix(dest, path)``       ← 安全闸门
        → ``transferhis.delete(id)``                ← 删历史
        → ``Path(src).unlink()``                    ← **真删本地文件**
        → ``PathRemoveUtils.remove_parent_dir(...)`` ← 真删空目录
        → ``handle_torrent(...)``                   ← 种子判定

单测绿不代表链路对：闸门函数写对了但被接反、或删除顺序导致数据不一致，
只有端到端跑真实文件系统才看得出来。这是"删除不可逆"类插件必须做的验证。

为什么单独建文件
----------------
``test_mediasyncdel.py`` 只测了一个纯字符串短路逻辑（ISO 后缀），
``remove_by_path`` 这条真正会删用户文件的路径**此前零覆盖**。
"""

import importlib
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock, patch


def _load_mediasyncdel_module():
    """
    按 MoviePilot 插件包路径加载同步删除模块。

    与 ``test_mediasyncdel.py`` 保持一致的加载方式：把插件根注册成
    ``app.plugins.p115lite`` 包，使模块内的相对导入可用。
    """
    plugin_root = Path(__file__).resolve().parent.parent
    package_name = "app.plugins.p115lite"
    package = ModuleType(package_name)
    package.__path__ = [str(plugin_root)]
    sys.modules[package_name] = package
    module_name = "app.plugins.p115lite.helper.mediasyncdel"
    sys.modules.pop(module_name, None)
    return importlib.import_module(module_name)


class _FakeTransferHBOper:
    """
    ``TransferHBOper`` 替身：按"目标路径在前缀之下"筛选历史记录。

    真实实现走 jieba 分词 + 数据库模糊匹配；端到端测试关心的是**闸门与
    删除动作**，因此这里直接把待测历史记录原样返回，让
    ``PathUtils.has_prefix`` 成为唯一的筛选条件 —— 闸门失效时才会删到
    不该删的文件，这正是本文件要验证的。
    """

    def __init__(self, records):
        self._records = list(records)
        #: 记录删除调用，便于断言"未授权的记录没被删"
        self.deleted_ids = []

    def get_transfer_his_by_path_title(self, path):
        return list(self._records)

    def delete(self, history_id):
        self.deleted_ids.append(history_id)
        before = len(self._records)
        self._records = [r for r in self._records if r.id != history_id]
        return len(self._records) != before


class _HelperHarness(unittest.TestCase):
    """构造一个绕过 ``__init__`` 的 helper，只挂端到端所需的桩。"""

    def setUp(self):
        self.base = Path(tempfile.mkdtemp(prefix="p115-e2e-"))
        self.module = _load_mediasyncdel_module()

    def tearDown(self):
        import shutil

        shutil.rmtree(self.base, ignore_errors=True)

    def make_helper(self, records):
        """
        返回 (helper, fake)。

        注意接线细节：``remove_by_path`` 里**查询用 ``self.transferhisb``、
        删除用 ``self.transferhis``**（两个不同属性）。替身必须同时挂到
        这两处，否则会出现"文件被真删了但历史记录仍留在库里"这种半成品
        状态——测试也会因为 ``deleted_ids`` 永远为空而看似"闸门拦住了"。
        """
        helper = object.__new__(self.module.MediaSyncDelHelper)
        fake = _FakeTransferHBOper(records)
        helper.transferhisb = fake
        helper.transferhis = fake
        helper.downloadhis = Mock()
        helper.plugindata = Mock()
        helper.chain = Mock()
        helper.storagechain = Mock()
        helper.mediaserver_operate = Mock()
        # handle_torrent 单独覆写：本文件只验证"何时被调用"，种子逻辑另有测试
        helper.handle_torrent = Mock(return_value=(False, True, []))
        return helper, fake

    def record(self, **kwargs):
        """构造一条整理历史记录（宽松容器，未知字段返回 None）。"""
        from app.db.models.transferhistory import TransferHistory

        return TransferHistory(**kwargs)

    def make_media_file(self, *parts) -> Path:
        p = self.base.joinpath(*parts)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x", encoding="utf-8")
        return p


class TestRemoveByPathSafetyGate(_HelperHarness):
    """``remove_by_path`` 的闸门：只有目标路径在待删路径之下才动手。"""

    def test_deletes_file_inside_prefix(self):
        """目标路径在前缀之下的记录：删历史 + 删本地源文件。"""
        src = self.make_media_file("media", "电影", "片名", "movie.strm")
        record = self.record(
            id=1,
            src=str(src),
            src_storage="local",
            dest=str(src),
            mode="link",
            type="movie",
            download_hash=None,
        )
        helper, fake = self.make_helper([record])

        with patch.object(self.module.settings, "RMT_MEDIAEXT", [".strm"]):
            helper.remove_by_path(str(self.base / "media" / "电影"), del_source=True)

        self.assertEqual(fake.deleted_ids, [1], "历史记录应被删除")
        self.assertFalse(src.exists(), "前缀内的源文件应被真实删除")

    def test_sibling_path_untouched(self):
        """
        **核心安全链路**：兄弟目录（``/media/电影2``）下的记录不得被删。

        ``/media/电影2/x.strm`` 以字符串论确实 startswith ``/media/电影``，
        但按路径分量不是其子路径。闸门一旦退化成 startswith，这里就会
        真删用户文件 —— 本用例就是那个场景的端到端复现。
        """
        victim = self.make_media_file("media", "电影2", "片名", "movie.strm")
        record = self.record(
            id=2,
            src=str(victim),
            src_storage="local",
            dest=str(victim),
            mode="link",
            type="movie",
            download_hash=None,
        )
        helper, fake = self.make_helper([record])

        with patch.object(self.module.settings, "RMT_MEDIAEXT", [".strm"]):
            helper.remove_by_path(str(self.base / "media" / "电影"), del_source=True)

        self.assertEqual(fake.deleted_ids, [], "不在前缀下的记录不得删除")
        self.assertTrue(
            victim.exists(),
            "兄弟目录文件被删（闸门退化成字符串 startswith 的后果）",
        )

    def test_dotdot_escaping_record_untouched(self):
        """
        **核心安全链路**：``dest`` 含 ``..`` 时不得越界删除。

        整理历史里的 ``dest`` 由配置与上游数据拼出，出现 ``..`` 是有可能的。
        未归一化时 ``/media/电影/../音乐/x`` 会被误判为在 ``/media/电影`` 下，
        进而删掉 ``/media/音乐`` 下的真实文件。
        """
        victim = self.make_media_file("media", "音乐", "片名", "song.strm")
        record = self.record(
            id=3,
            src=str(victim),
            src_storage="local",
            dest=str(victim.parent.parent / "电影" / ".." / "音乐" / "片名" / "song.strm"),
            mode="link",
            type="movie",
            download_hash=None,
        )
        helper, fake = self.make_helper([record])

        with patch.object(self.module.settings, "RMT_MEDIAEXT", [".strm"]):
            helper.remove_by_path(str(self.base / "media" / "电影"), del_source=True)

        self.assertEqual(fake.deleted_ids, [], ".. 逃出前缀的记录不得删除")
        self.assertTrue(
            victim.exists(),
            "``..`` 绕过前缀检查，越界删除了 /media/音乐 下的文件",
        )

    def test_empty_dest_skipped(self):
        """``dest`` 为空的记录跳过（无从判定归属，宁可不删）。"""
        src = self.make_media_file("media", "电影", "片名", "movie.strm")
        record = self.record(
            id=4,
            src=str(src),
            src_storage="local",
            dest=None,
            mode="link",
            type="movie",
            download_hash=None,
        )
        helper, fake = self.make_helper([record])

        with patch.object(self.module.settings, "RMT_MEDIAEXT", [".strm"]):
            helper.remove_by_path(str(self.base / "media" / "电影"), del_source=True)

        self.assertEqual(fake.deleted_ids, [], "dest 为空的记录不得删除")
        self.assertTrue(src.exists(), "dest 为空时不得删源文件")

    def test_del_source_false_keeps_file(self):
        """``del_source=False``（仅删记录）时不得碰本地文件。"""
        src = self.make_media_file("media", "电影", "片名", "movie.strm")
        record = self.record(
            id=5,
            src=str(src),
            src_storage="local",
            dest=str(src),
            mode="link",
            type="movie",
            download_hash=None,
        )
        helper, fake = self.make_helper([record])

        with patch.object(self.module.settings, "RMT_MEDIAEXT", [".strm"]):
            helper.remove_by_path(str(self.base / "media" / "电影"), del_source=False)

        self.assertEqual(fake.deleted_ids, [5], "仅删记录模式下历史仍应删除")
        self.assertTrue(src.exists(), "del_source=False 时不得删除本地文件")

    def test_move_mode_keeps_src(self):
        """``mode='move'`` 时源文件已不在原处，不得再删。"""
        src = self.make_media_file("media", "电影", "片名", "movie.strm")
        record = self.record(
            id=6,
            src=str(src),
            src_storage="local",
            dest=str(src),
            mode="move",
            type="movie",
            download_hash=None,
        )
        helper, fake = self.make_helper([record])

        with patch.object(self.module.settings, "RMT_MEDIAEXT", [".strm"]):
            helper.remove_by_path(str(self.base / "media" / "电影"), del_source=True)

        self.assertEqual(fake.deleted_ids, [6])
        self.assertTrue(src.exists(), "move 模式的源文件不得删除")

    def test_remote_src_storage_keeps_file(self):
        """``src_storage`` 非 local（网盘）时不得走本地删除分支。"""
        src = self.make_media_file("media", "电影", "片名", "movie.strm")
        record = self.record(
            id=7,
            src=str(src),
            src_storage="115",
            dest=str(src),
            mode="link",
            type="movie",
            download_hash=None,
        )
        helper, fake = self.make_helper([record])

        with patch.object(self.module.settings, "RMT_MEDIAEXT", [".strm"]):
            helper.remove_by_path(str(self.base / "media" / "电影"), del_source=True)

        self.assertEqual(fake.deleted_ids, [7])
        self.assertTrue(src.exists(), "非本地存储的源文件不得被本地删除")

    def test_non_media_suffix_keeps_file(self):
        """不在 ``RMT_MEDIAEXT`` 白名单内的后缀不得删除。"""
        src = self.make_media_file("media", "电影", "片名", "notes.txt")
        record = self.record(
            id=8,
            src=str(src),
            src_storage="local",
            dest=str(src),
            mode="link",
            type="movie",
            download_hash=None,
        )
        helper, fake = self.make_helper([record])

        with patch.object(self.module.settings, "RMT_MEDIAEXT", [".strm", ".mkv"]):
            helper.remove_by_path(str(self.base / "media" / "电影"), del_source=True)

        self.assertEqual(fake.deleted_ids, [8])
        self.assertTrue(src.exists(), "非媒体后缀文件不得删除（白名单外）")


class TestRemoveByPathSideEffects(_HelperHarness):
    """端到端副作用：目录回收、种子判定时机。"""

    def test_empty_parent_dir_recycled(self):
        """删掉源文件后，随之变空的父目录应被回收。"""
        src = self.make_media_file("media", "电影", "片名", "movie.strm")
        movie_dir = src.parent
        record = self.record(
            id=10,
            src=str(src),
            src_storage="local",
            dest=str(src),
            mode="link",
            type="movie",
            download_hash=None,
        )
        helper, _ = self.make_helper([record])

        with patch.object(self.module.settings, "RMT_MEDIAEXT", [".strm"]):
            helper.remove_by_path(str(self.base / "media" / "电影"), del_source=True)

        self.assertFalse(src.exists(), "源文件应被删除")
        self.assertFalse(
            movie_dir.exists(),
            "空目录应被回收（RMT_MEDIAEXT 只含 strm，目录已无 strm）",
        )

    def test_parent_dir_recycled_when_only_non_whitelist_left(self):
        """
        目录里只剩**非白名单后缀**文件时，目录会被回收（连同这些文件）。

        这是 ``mode=settings.RMT_MEDIAEXT``（list）模式的**设计语义**：
        判定基准是"还有没有白名单内的媒体文件"，而不是"目录是否为空"。
        ``remove_by_path`` 传的是 ``settings.RMT_MEDIAEXT``，所以只保留
        ``.strm`` 时，同目录的 ``.mkv`` / 图片 / nfo 会随空目录一并清掉。

        风险提示（不在本测试的判定范围，仅记录）：若 ``RMT_MEDIAEXT`` 被
        用户配置得过窄（例如只留 ``.strm``），这条路径会连带删掉本应保留的
        其它媒体文件。使用方需保证 ``RMT_MEDIAEXT`` 覆盖媒体库全部后缀。
        """
        src = self.make_media_file("media", "电影", "片名", "movie.strm")
        keep = src.parent / "extra.mkv"
        keep.write_text("keep", encoding="utf-8")
        movie_dir = src.parent
        record = self.record(
            id=11,
            src=str(src),
            src_storage="local",
            dest=str(src),
            mode="link",
            type="movie",
            download_hash=None,
        )
        helper, _ = self.make_helper([record])

        # 只把 .strm 放进白名单 → .mkv 不被视为"需保留的媒体文件"
        with patch.object(self.module.settings, "RMT_MEDIAEXT", [".strm"]):
            helper.remove_by_path(str(self.base / "media" / "电影"), del_source=True)

        self.assertFalse(src.exists(), "源文件应被删除")
        self.assertFalse(
            movie_dir.exists(),
            "目录内已无白名单后缀文件，应被回收（list 模式的既定语义）",
        )

    def test_parent_dir_kept_when_other_whitelist_media_present(self):
        """
        同目录仍有**白名单内**的其它媒体文件时，目录必须保留。

        这是上一条的对照组：把 ``.mkv`` 也放进 ``RMT_MEDIAEXT`` 后，
        目录不再满足回收条件，``.mkv`` 必须原样保留。
        """
        src = self.make_media_file("media", "电影", "片名", "movie.strm")
        keep = src.parent / "extra.mkv"
        keep.write_text("keep", encoding="utf-8")
        movie_dir = src.parent
        record = self.record(
            id=15,
            src=str(src),
            src_storage="local",
            dest=str(src),
            mode="link",
            type="movie",
            download_hash=None,
        )
        helper, _ = self.make_helper([record])

        with patch.object(self.module.settings, "RMT_MEDIAEXT", [".strm", ".mkv"]):
            helper.remove_by_path(str(self.base / "media" / "电影"), del_source=True)

        self.assertFalse(src.exists(), "源文件应被删除")
        self.assertTrue(
            keep.exists(), "白名单内的其它媒体文件被误删"
        )
        self.assertTrue(movie_dir.exists(), "目录内仍有媒体文件，不得回收")

    def test_torrent_judgement_invoked_with_record_hash(self):
        """有 ``download_hash`` 时应触发种子判定，且传对 hash 与 src。"""
        src = self.make_media_file("media", "电影", "片名", "movie.strm")
        record = self.record(
            id=12,
            src=str(src),
            src_storage="local",
            dest=str(src),
            mode="link",
            type="movie",
            download_hash="ABCDEF",
        )
        helper, _ = self.make_helper([record])

        with patch.object(self.module.settings, "RMT_MEDIAEXT", [".strm"]):
            helper.remove_by_path(str(self.base / "media" / "电影"), del_source=True)

        helper.handle_torrent.assert_called_once()
        kwargs = helper.handle_torrent.call_args.kwargs
        self.assertEqual(kwargs.get("torrent_hash"), "ABCDEF")
        self.assertEqual(kwargs.get("src"), str(src))
        self.assertEqual(kwargs.get("type"), "movie")

    def test_no_torrent_judgement_without_hash(self):
        """无 ``download_hash`` 时不得触发种子判定。"""
        src = self.make_media_file("media", "电影", "片名", "movie.strm")
        record = self.record(
            id=13,
            src=str(src),
            src_storage="local",
            dest=str(src),
            mode="link",
            type="movie",
            download_hash=None,
        )
        helper, _ = self.make_helper([record])

        with patch.object(self.module.settings, "RMT_MEDIAEXT", [".strm"]):
            helper.remove_by_path(str(self.base / "media" / "电影"), del_source=True)

        helper.handle_torrent.assert_not_called()

    def test_gate_failure_does_not_touch_torrent(self):
        """闸门拦下的记录不得触发种子判定（否则会误暂停/误删种子）。"""
        src = self.make_media_file("media", "电影2", "片名", "movie.strm")
        record = self.record(
            id=14,
            src=str(src),
            src_storage="local",
            dest=str(src),
            mode="link",
            type="movie",
            download_hash="NOTMINE",
        )
        helper, _ = self.make_helper([record])

        with patch.object(self.module.settings, "RMT_MEDIAEXT", [".strm"]):
            helper.remove_by_path(str(self.base / "media" / "电影"), del_source=True)

        helper.handle_torrent.assert_not_called()
        self.assertTrue(src.exists(), "闸门拦下的文件被删")

    def test_mixed_records_only_authorized_ones_deleted(self):
        """
        混合场景：同一批记录里，只有真正在前缀下的才被删。

        这是最接近线上的一步：一次同步删除会带回多条历史，闸门必须**逐条**
        判定，不能因为"有一条匹配"就整批放过。
        """
        inside = self.make_media_file("media", "电影", "片名", "a.strm")
        sibling = self.make_media_file("media", "电影2", "片名", "b.strm")
        unrelated = self.make_media_file("other", "c.strm")
        escape = self.make_media_file("media", "音乐", "d.strm")

        records = [
            self.record(id=21, src=str(inside), src_storage="local",
                        dest=str(inside), mode="link",
                        type="movie", download_hash=None),
            self.record(id=22, src=str(sibling), src_storage="local",
                        dest=str(sibling), mode="link",
                        type="movie", download_hash=None),
            self.record(id=23, src=str(unrelated), src_storage="local",
                        dest=str(unrelated), mode="link",
                        type="movie", download_hash=None),
            self.record(id=24, src=str(escape), src_storage="local",
                        dest=str(escape.parent.parent / "电影" / ".." / "音乐" / "d.strm"), mode="link",
                        type="movie", download_hash=None),
        ]
        helper, fake = self.make_helper(records)

        with patch.object(self.module.settings, "RMT_MEDIAEXT", [".strm"]):
            helper.remove_by_path(str(self.base / "media" / "电影"), del_source=True)

        self.assertEqual(fake.deleted_ids, [21], "只应删除授权范围内的记录")
        self.assertFalse(inside.exists(), "前缀内的文件应被删除")
        self.assertTrue(sibling.exists(), "兄弟目录文件被误删")
        self.assertTrue(unrelated.exists(), "无关目录文件被误删")
        self.assertTrue(escape.exists(), ".. 逃逸的文件被误删")


if __name__ == "__main__":
    unittest.main()
