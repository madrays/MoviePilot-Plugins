# -*- coding: utf-8 -*-
"""
边界 / 安全测试：路径判断与删除操作。

为什么必须做这个
----------------
本插件是**唯一会真删用户媒体文件**的插件之一，且删除不可逆。已有测试集中在
URL 工具、时间工具、限流器等纯函数上，而**真正执行删除的两个模块零覆盖**：

- ``utils/path.py`` 的 ``PathRemoveUtils``（rmtree 删目录、unlink 删文件）
- ``PathUtils.has_prefix`` —— 它看着像"字符串工具"，实际是**删除前的安全闸门**：
  ``helper/mediasyncdel/__init__.py:99`` 用它判定"转移记录的目标路径是否在
  待删除目录下"，不满足才跳过删除。一旦前缀判断被绕过，删的就是用户数据。

本文件覆盖三类风险：
1. **误删**：不该删的目录/文件被删
2. **漏删**：该删的没删（功能静默失效）
3. **边界绕过**：``..`` / 符号链接 / 大小写 / 尾斜杠 等使前缀判断失真
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import tests  # noqa: F401  触发桩路径注入

from utils.path import PathRemoveUtils, PathUtils


class _TmpBase(unittest.TestCase):
    """临时目录夹具。"""

    def setUp(self):
        self.base = Path(tempfile.mkdtemp(prefix="p115-boundary-"))

    def tearDown(self):
        import shutil

        shutil.rmtree(self.base, ignore_errors=True)

    # ------------------------------------------------------------------
    def make_media_tree(self, *parts, files=("movie.strm",)) -> Path:
        """构造 ``base/parts...`` 目录并在其中放若干文件，返回目录路径。"""
        d = self.base.joinpath(*parts)
        d.mkdir(parents=True, exist_ok=True)
        for name in files:
            (d / name).write_text("x", encoding="utf-8")
        return d

    def rel(self) -> list:
        """当前临时目录下的全部条目（相对路径，排序）。"""
        return sorted(
            str(p.relative_to(self.base)) for p in self.base.rglob("*")
        )

    def rel_files(self) -> list:
        """
        当前临时目录下的全部**文件**（相对路径，排序），不含目录。

        路径分隔符统一为 ``/``：``Path`` 在 Windows 下产出反斜杠
        （CI windows-latest 实测），若断言写死 ``/`` 会误报失败。
        """
        return sorted(
            str(p.relative_to(self.base)).replace("\\", "/")
            for p in self.base.rglob("*")
            if p.is_file()
        )


# ======================================================================
# 1. has_prefix —— 删除前的安全闸门
# ======================================================================
class TestHasPrefixSafetyGate(_TmpBase):
    """
    ``has_prefix`` 是"路径归属"判定，用于放行/拦截删除。

    它是 ``PathUtils`` 里的静态方法，看着无害，但 `mediasyncdel` 用它做删除
    前校验（``if not has_prefix(dest_path, path): continue``）。判断失真 =
    删错东西或漏删。

    实现要点：用 ``Path.parts`` **按路径分量**比较，而非字符串 ``startswith``
    —— 后者会把 ``/media/电影2`` 误认为在 ``/media/电影`` 下。
    """

    def test_descendant_recognized(self):
        self.assertTrue(PathUtils.has_prefix("/media/电影/x.strm", "/media/电影"))

    def test_self_recognized(self):
        self.assertTrue(PathUtils.has_prefix("/media/电影", "/media/电影"))

    def test_deep_descendant_recognized(self):
        self.assertTrue(
            PathUtils.has_prefix("/media/电影/2026/片名/x.strm", "/media/电影")
        )

    def test_sibling_with_common_prefix_refused(self):
        """
        **核心安全用例**：``/media/电影2`` 不得被 ``/media/电影`` 认领。

        若实现退化成 ``str.startswith``，这里会返回 True —— 于是删 ``/media/电影``
        的同步操作会连带把 ``/media/电影2`` 这个毫不相干的库也算进去。
        """
        self.assertFalse(
            PathUtils.has_prefix("/media/电影2/x.strm", "/media/电影"),
            "兄弟目录被误认 → 越界删除",
        )

    def test_sibling_suffix_refused(self):
        """``/mnt/dl-old`` 不得被 ``/mnt/dl`` 认领。"""
        self.assertFalse(PathUtils.has_prefix("/mnt/dl-old/x", "/mnt/dl"))

    def test_prefix_longer_than_path_refused(self):
        """前缀比路径还长时不可能是其子路径。"""
        self.assertFalse(PathUtils.has_prefix("/media", "/media/电影/2026"))

    def test_unrelated_path_refused(self):
        self.assertFalse(PathUtils.has_prefix("/other/x.strm", "/media/电影"))

    def test_empty_inputs_refused(self):
        """空值一律返回 False（宁可不删，不可误删）。"""
        self.assertFalse(PathUtils.has_prefix("", "/media/电影"))
        self.assertFalse(PathUtils.has_prefix("/media/电影/x", ""))
        self.assertFalse(PathUtils.has_prefix("", ""))

    def test_trailing_slash_normalized(self):
        """配置里的路径常带尾斜杠，必须等价。"""
        self.assertTrue(PathUtils.has_prefix("/media/电影/x", "/media/电影/"))

    def test_dotdot_not_bypassing(self):
        """
        **核心安全用例**：未归一的 ``..`` 不得让路径"逃出"前缀。

        ``/media/电影/../音乐/x`` 真实位置在 ``/media/音乐``，**不属于**
        ``/media/电影``。若直接按分量比较（不做归一化），前三个分量
        ``('', 'media', '电影')`` 会匹配上 → 返回 True → 误判为可删。

        期望：实现应对路径做归一化（normpath）后再比较。
        """
        self.assertFalse(
            PathUtils.has_prefix("/media/电影/../音乐/x", "/media/电影"),
            "未归一的 .. 绕过了前缀检查 → 可能越界删除",
        )

    def test_dotdot_staying_inside_allowed(self):
        """``..`` 绕一圈仍在前缀内时，应判为属于（归一化后判定）。"""
        self.assertTrue(
            PathUtils.has_prefix("/media/电影/2026/../片名/x", "/media/电影"),
            "归一化后仍在前缀内，应认领",
        )

    def test_relative_prefix_not_matching_absolute(self):
        """相对前缀不得匹配绝对路径（避免配置写错时误放行）。"""
        self.assertFalse(PathUtils.has_prefix("/media/电影/x", "media/电影"))

    def test_backslash_not_confused(self):
        """
        Windows 风格反斜杠不应影响判定（插件在 Windows 上运行）。

        期望：反斜杠与正斜杠等价。
        """
        self.assertTrue(
            PathUtils.has_prefix("\\media\\电影\\x.strm", "\\media\\电影"),
            "反斜杠路径未被正确解析",
        )

    def test_case_sensitive_on_posix(self):
        """
        POSIX 下大小写敏感（避免把 ``/Media`` 误认成 ``/media``）。

        这条是"不要过度归一化"的护栏：若实现把所有路径 lower() 掉，
        在 Linux 上就会把两个真实不同的目录混为一谈。
        """
        if os.name == "nt":
            self.skipTest("Windows 文件系统大小写不敏感，跳过")
        self.assertFalse(PathUtils.has_prefix("/MEDIA/电影/x", "/media/电影"))


class TestHasPrefixConsumers(_TmpBase):
    """``has_prefix`` 的上层封装：整理路径 / 排除目录 / 媒体路径匹配。"""

    def test_run_transfer_path_matches_any_line(self):
        paths = "/media/下载\n/media/整理"
        self.assertTrue(PathUtils.get_run_transfer_path(paths, "/media/整理/x"))
        self.assertTrue(PathUtils.get_run_transfer_path(paths, "/media/下载/y"))

    def test_run_transfer_path_outside_refused(self):
        """**安全**：不在列表内时必须返回 False（决定是否触发整理逻辑）。"""
        paths = "/media/下载\n/media/整理"
        self.assertFalse(PathUtils.get_run_transfer_path(paths, "/media/其他/x"))
        self.assertFalse(PathUtils.get_run_transfer_path(paths, "/media/整理2/x"))

    def test_run_transfer_path_skips_blank_lines(self):
        """空行不得被当成"空前缀"从而匹配一切。"""
        paths = "\n\n/media/整理\n\n"
        self.assertFalse(
            PathUtils.get_run_transfer_path(paths, "/media/其他/x"),
            "空行被当成空前缀 → 匹配了所有路径",
        )
        self.assertTrue(PathUtils.get_run_transfer_path(paths, "/media/整理/x"))

    def test_run_transfer_path_empty_config_refused(self):
        self.assertFalse(PathUtils.get_run_transfer_path("", "/media/整理/x"))

    def test_scrape_exclude_path_matches(self):
        self.assertTrue(
            PathUtils.get_scrape_metadata_exclude_path("/media/排除", "/media/排除/x")
        )

    def test_scrape_exclude_path_outside_refused(self):
        """**安全**：不在排除列表内的目录应允许刮削（False = 不排除）。"""
        self.assertFalse(
            PathUtils.get_scrape_metadata_exclude_path("/media/排除", "/media/其他")
        )

    def test_media_path_mapping_matched(self):
        """媒体服务器路径#网盘路径 的映射匹配。"""
        paths = "媒体服务器路径#/media/电影"
        ok, server, pan = PathUtils.get_media_path(paths, "/media/电影/x")
        self.assertTrue(ok)
        self.assertEqual(server, "媒体服务器路径")
        self.assertEqual(pan, "/media/电影")

    def test_media_path_mapping_sibling_refused(self):
        """**安全**：兄弟前缀目录不得被映射成功。"""
        paths = "媒体服务器路径#/media/电影"
        ok, _server, _pan = PathUtils.get_media_path(paths, "/media/电影2/x")
        self.assertFalse(ok, "兄弟目录被误匹配为媒体路径")

    def test_media_path_mapping_empty_refused(self):
        ok, server, pan = PathUtils.get_media_path("", "/media/电影/x")
        self.assertFalse(ok)
        self.assertIsNone(server)

    def test_p115_media_path_uses_first_field(self):
        """三段式映射 ``媒体服务器#MoviePilot#115`` 只按首段匹配。"""
        paths = "/server/strm#/mp/电影#/115/电影"
        ok, parts = PathUtils.get_p115_media_path("/server/strm/电影/x", paths)
        self.assertTrue(ok)
        self.assertEqual(parts[0], "/server/strm")

    def test_p115_media_path_outside_refused(self):
        paths = "/server/strm#/mp/电影#/115/电影"
        ok, parts = PathUtils.get_p115_media_path("/other/x", paths)
        self.assertFalse(ok)
        self.assertIsNone(parts)

    def test_p115_strm_path_generates_relative(self):
        """
        全量目录：应由匹配到的网盘路径换算出本地路径。

        注意：实现用 ``Path`` 拼接本地路径，**Windows 下会产反斜杠**
        （实测 CI windows-latest：`\\local\\strm\\2026\\片名#...`）。这是
        平台正常行为，断言须做分隔符归一化，否则在 Windows 上误报失败。
        """
        paths = "/local/strm#/115/电影"
        ok, final = PathUtils.get_p115_strm_path(paths, "/115/电影/2026/片名")
        self.assertTrue(ok)
        local_part, _, remote_part = final.partition("#")
        self.assertEqual(
            local_part.replace("\\", "/"),
            "/local/strm/2026/片名",
            "本地路径应由网盘路径换算出相对部分",
        )
        # '#' 之后的网盘路径部分不受本地分隔符影响
        self.assertEqual(remote_part, "/115/电影/2026/片名")

    def test_p115_strm_path_outside_refused(self):
        paths = "/local/strm#/115/电影"
        ok, final = PathUtils.get_p115_strm_path(paths, "/115/其他/x")
        self.assertFalse(ok)
        self.assertIsNone(final)


# ======================================================================
# 2. remove_parent_dir —— 删目录边界
# ======================================================================
class TestRemoveParentDirBoundary(_TmpBase):
    """
    ``remove_parent_dir`` 在文件删除后回收空目录。

    它是**真正执行 rmtree 的地方**，而此前零测试覆盖。三类必须锁定的行为：

    1. 只删到"还有内容"为止，不能删非空目录之外的东西
    2. 向上最多 3 层（防止一路删到文件系统根）
    3. ``mode`` 三种取值（``all`` / list / ``mixed``）的判定基准不同
    """

    def test_all_mode_keeps_dir_with_other_files(self):
        """
        ``mode='all'`` 下目录里还有别的文件时不得删除该目录。

        注意与 ``test_list_mode_ignores_other_extensions`` 的区别：
        后者用的 ``mode=['strm']`` **刻意**只看 strm，会连 sidecar 一起
        清掉（回收空壳目录的设计语义）；本用例锁定的是 ``all`` 模式
        这条更保守的路径。
        """
        d = self.make_media_tree("lib", "电影", "片名",
                                 files=("movie.strm", "movie.mkv"))
        (d / "movie.strm").unlink()

        PathRemoveUtils.remove_parent_dir(
            file_path=d / "movie.strm", mode="all", func_type="[t]"
        )

        self.assertTrue(d.exists(), "仍有 mkv 的目录被删（误删用户文件）")
        self.assertEqual(self.rel_files(), ["lib/电影/片名/movie.mkv"])

    def test_all_mode_requires_truly_empty(self):
        """``mode='all'`` 下只有目录真正为空才删。"""
        d = self.make_media_tree("lib", "电影", files=("a.strm", "b.txt"))
        (d / "a.strm").unlink()

        PathRemoveUtils.remove_parent_dir(
            file_path=d / "a.strm", mode="all", func_type="[t]"
        )

        self.assertTrue(d.exists(), "目录不空（还有 b.txt），不得删除")

    def test_list_mode_ignores_other_extensions(self):
        """
        ``mode=['strm']`` 只看 strm 来决定目录去留。

        这是**刻意的语义**：目标是回收"STRM 全没了"的空壳目录，
        其余刮削产物（nfo/图片）随目录一起清掉。测试锁定这一语义，
        避免将来被无意改成"目录非空就不删"（那样会残留大量空壳）。
        """
        d = self.make_media_tree("lib", "电影", "片名", files=("x.strm", "x.nfo"))
        (d / "x.strm").unlink()

        PathRemoveUtils.remove_parent_dir(
            file_path=d / "x.strm", mode=["strm"], func_type="[t]"
        )

        self.assertFalse(
            d.exists(), "strm 已清空，目录应被回收（含 nfo 一并清理）"
        )

    def test_mixed_mode_first_layer_all(self):
        """
        ``mixed``：第一层按"完全空"判断，含 nfo 时保留。

        注意：这里的断言能捕获的是"第一层被改成按 strm 判定"之外的改写。
        若只把 ``(mode == "mixed" and i == 1)`` 那句删掉，属于**等价变异**
        ——第一层的进入条件是 ``not any(iterdir)``（该层必然为空），此时
        "按 all 判定"与"按 strm 判定"结论都是空目录 → 删，行为无差异。
        """
        d = self.make_media_tree("lib", "电影", "片名", files=("x.strm", "x.nfo"))
        (d / "x.strm").unlink()

        PathRemoveUtils.remove_parent_dir(
            file_path=d / "x.strm", mode="mixed", func_type="[t]"
        )

        self.assertTrue(d.exists(), "mixed 第一层要求完全空，有 nfo 应保留")
        self.assertTrue((d / "x.nfo").exists(), "第一层不得连带清掉 sidecar")
        # 上层（电影/、lib/）此时只含"非 strm"内容，必须一路保留
        self.assertTrue((self.base / "lib").exists())
        self.assertTrue((self.base / "lib" / "电影").exists())

    def test_mixed_mode_upper_layer_by_strm(self):
        """``mixed``：上层按 strm 判断，可穿透只含 sidecar 的上级目录。"""
        d = self.make_media_tree("lib", "电影", "片名", files=("x.strm",))
        # 上级目录只留一个非 strm 的 sidecar
        (Path(self.base) / "lib" / "电影" / "cover.jpg").write_text("c")
        (d / "x.strm").unlink()

        PathRemoveUtils.remove_parent_dir(
            file_path=d / "x.strm", mode="mixed", func_type="[t]"
        )

        self.assertFalse(d.exists(), "本层已空应删除")
        self.assertFalse(
            (Path(self.base) / "lib" / "电影").exists(),
            "mixed 上层按 strm 判断，仅含 sidecar 时应穿透删除",
        )

    def test_stops_at_max_parent_levels(self):
        """
        **核心边界**：最多向上删 3 层，不得一路删到根。

        没有这个限制时，一个深层路径的空目录回收会连带删除大量上层空目录，
        极端情况下触及挂载点/家目录。测试锁定该保护确实生效。
        """
        deep = self.make_media_tree("a", "b", "c", "d", "e", files=("y.strm",))
        (deep / "y.strm").unlink()

        PathRemoveUtils.remove_parent_dir(
            file_path=deep / "y.strm", mode="all", func_type="[t]"
        )

        # 删掉 3 层（e/d/c），留下 a 与 a/b
        self.assertTrue((self.base / "a").exists(), "上层目录不应被删光")
        self.assertTrue(
            (self.base / "a" / "b").exists(),
            "超过 3 层的目录不得被删除（防一路删到根）",
        )

    def test_never_deletes_filesystem_root(self):
        """
        **核心边界**：往深了删时不得触及文件系统根，也不得碰临时根。

        注：``if str(parent_path.parent) != str(file_path.root)`` 这道保护
        只在"待删目录位于根的直接子目录"时才触发，深度场景**不经过**它
        （拆掉它深度用例照样全绿 —— 实测确认过）。该分支由
        ``test_does_not_delete_direct_child_of_root`` 专门覆盖。
        """
        deep = self.make_media_tree(*[f"L{i}" for i in range(8)], files=("z.strm",))
        (deep / "z.strm").unlink()

        PathRemoveUtils.remove_parent_dir(
            file_path=deep / "z.strm", mode="all", func_type="[t]"
        )

        self.assertTrue(
            Path(self.base.anchor).exists(),
            "文件系统根（POSIX 为 /，Windows 为盘符）必须完好",
        )
        self.assertTrue(self.base.exists(), "临时根不应被删")
        # 临时根的直接子目录不在 3 层删除半径内，必须保留
        self.assertTrue(
            (self.base / "L0").exists(),
            "临时根的直接子目录不应被删",
        )

    def test_root_guard_only_protects_root_layer(self):
        """
        锁定现状：``!= root`` 这道保护只刹车在**根**那一层。

        实测行为（见下断言）——媒体库直接挂在根下、结构较浅时，向上回收会
        继续删掉「根下第 1 层」里的目录：

        ==================== ============================ ==========
        基准文件位置          实际被回收                    是否触及根
        ==================== ============================ ==========
        ``/media/x/电影/a.strm`` ``电影``、``/media/x``     否
        ``/media/电影/a.strm``   ``电影``                   否
        ==================== ============================ ==========

        ``/media`` 本身**始终安全**（它的 parent 就是 ``/``，被这道保护挡住），
        但 ``/media`` 下的第 1 层目录会被回收。

        本用例**只锁定现状、不判定对错**：收紧它（例如禁止触碰挂载点的直接
        子目录）会改变现网行为（可能残留空目录），属于产品决策，需要单独评估。
        这里的作用是把这个边界写进测试，避免它被无意识地改动。
        """
        if os.name == "nt":
            self.skipTest("Windows 下根为盘符、无 /media，构造方式不同")
        holder = Path("/media") / f"p115-rootguard-{os.getpid()}"
        import shutil

        shutil.rmtree(holder, ignore_errors=True)
        try:
            holder.mkdir(parents=True)
        except (PermissionError, OSError):
            self.skipTest("无权限在 /media 下创建目录")

        try:
            movie_dir = holder / "电影"
            movie_dir.mkdir()
            (movie_dir / "x.strm").write_text("x", encoding="utf-8")
            (movie_dir / "x.strm").unlink()

            PathRemoveUtils.remove_parent_dir(
                file_path=movie_dir / "x.strm", mode="all", func_type="[t]"
            )

            self.assertFalse(movie_dir.exists(), "「电影」已空，应被回收")
            # 现状：/media 的第 1 层目录也在回收半径内
            self.assertFalse(
                holder.exists(),
                "现状记录：根的直接子目录也在回收半径内（如需收紧请单独评估）",
            )
            # 但 /media 本身必须安全 —— 这才是 != root 保护真正守住的东西
            self.assertTrue(
                Path("/media").exists(),
                "挂载点自身被删（严重越界）",
            )
        finally:
            shutil.rmtree(holder, ignore_errors=True)

    def test_missing_file_does_not_crash(self):
        """
        文件已不存在时不得抛异常，也不得删掉不该删的东西。

        只断言"不抛异常"是无效断言——把整个方法体删掉也照样通过。必须同时
        锁定副作用边界：文件已删时目录**依然是空的**，实现可以回收它；
        但目录里若还有别的文件，实现不得因为"文件不存在"就误判为空目录。
        """
        d = self.make_media_tree("lib", "电影", files=("gone.strm",))
        target = d / "gone.strm"
        target.unlink()

        # 1) 不应抛异常
        PathRemoveUtils.remove_parent_dir(
            file_path=target, mode="all", func_type="[t]"
        )
        # 2) 目录确实空了，可以回收
        self.assertFalse(d.exists(), "空目录应被回收（走的是正常路径，不是异常）")

        # 3) 目录里还有内容时，文件不存在不得导致误删
        d2 = self.make_media_tree("lib2", "电影", files=("gone.strm", "keep.mkv"))
        target2 = d2 / "gone.strm"
        target2.unlink()

        PathRemoveUtils.remove_parent_dir(
            file_path=target2, mode="all", func_type="[t]"
        )
        self.assertTrue(
            (d2 / "keep.mkv").exists(),
            "目录非空，不得因为基准文件不存在就清空目录",
        )

    def test_symlink_dir_not_traversed(self):
        """
        符号链接指向外部时，不得沿着链接删掉外部内容。

        若实现用 ``Path.iterdir()`` 判断时跟随链接，或 rmtree 越界，
        会让删除波及媒体库之外的目录。
        """
        outside = Path(tempfile.mkdtemp(prefix="p115-outside-"))
        try:
            (outside / "重要.mkv").write_text("keep", encoding="utf-8")
            link_parent = self.base / "lib"
            link_parent.mkdir(parents=True)
            os.symlink(outside, link_parent / "link")

            d = self.make_media_tree("lib", "电影", files=("a.strm",))
            (d / "a.strm").unlink()

            PathRemoveUtils.remove_parent_dir(
                file_path=d / "a.strm", mode="all", func_type="[t]"
            )

            self.assertTrue(
                (outside / "重要.mkv").exists(),
                "符号链接目标被删（越界删除）",
            )
        finally:
            import shutil

            shutil.rmtree(outside, ignore_errors=True)


# ======================================================================
# 3. clean_related_files —— 删同名相关文件
# ======================================================================
class TestCleanRelatedFilesBoundary(_TmpBase):
    """
    ``clean_related_files`` 删除"同目录下文件名包含基准名"的其它文件。

    风险面：匹配条件宽松（子串包含），稍有不慎会删到无关文件。必须锁定
    "只删同目录、同前缀、非同 strm"的边界。
    """

    def test_deletes_related_same_stem(self):
        """同名不同后缀的关联文件应被删除（nfo/封面等）。"""
        d = self.make_media_tree("lib", files=("电影.strm", "电影.nfo", "电影.jpg"))

        PathRemoveUtils.clean_related_files(file_path=d / "电影.strm", func_type="[t]")

        self.assertFalse((d / "电影.nfo").exists())
        self.assertFalse((d / "电影.jpg").exists())

    def test_protects_strm_files(self):
        """**.strm 一律受保护**：即使名字包含基准名也不得删。

        strm 是媒体库的索引文件本体，删掉等于媒体库条目消失 —— 这是本方法
        唯一的硬性保护，必须有测试锁定。
        """
        d = self.make_media_tree(
            "lib", files=("电影.strm", "电影.1080p.strm", "电影.nfo")
        )

        PathRemoveUtils.clean_related_files(file_path=d / "电影.strm", func_type="[t]")

        self.assertTrue((d / "电影.strm").exists(), "基准 strm 不得删除")
        self.assertTrue(
            (d / "电影.1080p.strm").exists(),
            "其它 .strm 受保护，不得删除",
        )
        self.assertFalse((d / "电影.nfo").exists(), "nfo 应被清理")

    def test_keeps_base_file_itself(self):
        """基准文件自身永远不删（即使后缀不是 strm）。"""
        d = self.make_media_tree("lib", files=("电影.mkv", "电影.nfo"))

        PathRemoveUtils.clean_related_files(file_path=d / "电影.mkv", func_type="[t]")

        self.assertTrue((d / "电影.mkv").exists(), "基准文件自身不得删除")
        self.assertFalse((d / "电影.nfo").exists())

    def test_unrelated_files_kept(self):
        """文件名不含基准名的不相关文件必须保留。"""
        d = self.make_media_tree(
            "lib", files=("电影.strm", "电影.nfo", "其它影片.mkv", "readme.txt")
        )

        PathRemoveUtils.clean_related_files(file_path=d / "电影.strm", func_type="[t]")

        self.assertTrue((d / "其它影片.mkv").exists(), "无关文件被误删")
        self.assertTrue((d / "readme.txt").exists(), "无关文件被误删")

    def test_only_same_directory(self):
        """只处理同目录，子目录内的同名文件不得被删。"""
        d = self.make_media_tree("lib", files=("电影.strm", "电影.nfo"))
        sub = d / "子目录"
        sub.mkdir()
        (sub / "电影.nfo").write_text("keep", encoding="utf-8")

        PathRemoveUtils.clean_related_files(file_path=d / "电影.strm", func_type="[t]")

        self.assertFalse((d / "电影.nfo").exists())
        self.assertTrue(
            (sub / "电影.nfo").exists(), "子目录内的文件不应被删（只处理同目录）"
        )

    def test_prefix_match_deletes_superset(self):
        """
        匹配为**子串包含**：``电影`` 会命中 ``电影花絮.nfo``。

        锁定这一宽松语义 —— 它是有意为之（清理同影片的附属文件），
        但也意味着使用方必须保证基准名足够具体。
        """
        d = self.make_media_tree("lib", files=("电影.strm", "电影花絮.nfo"))

        PathRemoveUtils.clean_related_files(file_path=d / "电影.strm", func_type="[t]")

        self.assertFalse(
            (d / "电影花絮.nfo").exists(), "子串匹配语义：含基准名的附属文件会被清理"
        )

    def test_empty_dir_does_not_crash(self):
        """目录里只有基准文件时不得抛异常。"""
        d = self.make_media_tree("lib", files=("only.strm",))

        PathRemoveUtils.clean_related_files(file_path=d / "only.strm", func_type="[t]")

        self.assertTrue((d / "only.strm").exists())


if __name__ == "__main__":
    unittest.main()
