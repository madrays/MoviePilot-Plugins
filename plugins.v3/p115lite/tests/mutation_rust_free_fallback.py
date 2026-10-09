#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
变异测试：Python 3.14 无 Rust 扩展时的降级路径。

为什么必须做
------------
插件的 3 个 Rust 扩展可能缺失（3.13 宿主、或未随包分发 wheel），
``tests/test_rust_free_fallback.py`` 里的降级测试就成了**唯一守着纯 Python
路径正确性**的东西。如果这些断言写松了（比如只断言"不抛异常"），把降级
逻辑写错照样全绿，等用户真跑起来才发现目录树比对结果不对、STRM 被误判。

本脚本逐个拆掉降级逻辑里的关键判断，验证测试确实会失败。

运行
----
    cd plugins.v3/p115lite
    PYTHONPATH="$PWD/tests/_stub_host:$PWD" python3 tests/mutation_rust_free_fallback.py

脚本会临时覆写源码，并在 ``finally`` 中**无条件还原**。
"""

import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN_DIR = os.path.dirname(HERE)

TREE_TARGET = os.path.join(PLUGIN_DIR, "utils", "tree.py")
FULL_TARGET = os.path.join(PLUGIN_DIR, "helper", "strm", "full", "__init__.py")
SCANNER_TARGET = os.path.join(
    PLUGIN_DIR, "helper", "strm", "share", "pure_scanner.py"
)

BACKUPS = {
    TREE_TARGET: "/tmp/p115_mut_tree_backup.py",
    FULL_TARGET: "/tmp/p115_mut_full_backup.py",
    SCANNER_TARGET: "/tmp/p115_mut_scanner_backup.py",
}

PYTHON = os.environ.get("P115_TEST_PYTHON", sys.executable)

# (目标文件, 变异体名称, 原文, 变异后, 期望被捕获的说明)
MUTANTS = [
    # ============ 一、utils/tree.py：目录树纯 Python 后备 ============
    (
        TREE_TARGET,
        "覆盖/追加反转：append=False 变成追加（旧数据残留导致误判为多出来的文件）",
        '        mode = "a" if append else "w"',
        '        mode = "w" if append else "a"',
        "应导致 test_add_paths_overwrite_replaces_content 失败",
    ),
    (
        TREE_TARGET,
        "差集方向反转：compare_trees 返回两边共有的路径（该删的没删、不该删的被删）",
        """        other_paths = set(other_storage._iter_lines())
        for path in self._iter_lines():
            if path not in other_paths:
                yield path""",
        """        other_paths = set(other_storage._iter_lines())
        for path in self._iter_lines():
            if path in other_paths:
                yield path""",
        "应导致 test_compare_trees_returns_only_self_unique 失败",
    ),
    (
        TREE_TARGET,
        "行号基准偏移：compare_trees_lines 从 0 开始计数",
        """        for line_number, path in enumerate(self._iter_lines(), start=1):""",
        """        for line_number, path in enumerate(self._iter_lines(), start=0):""",
        "应导致 test_compare_trees_lines_matches_compare_trees 失败",
    ),
    (
        TREE_TARGET,
        "计数偏移：count 多算一条（空树或边界少一个都会失准）",
        "        return sum(1 for _ in self._iter_lines())",
        "        return sum(1 for _ in self._iter_lines()) + 1",
        "应导致 test_count_ignores_blank_lines / test_count_on_missing_file 失败",
    ),
    (
        TREE_TARGET,
        "清空失效：clear 不去写空文件（旧目录树残留，下次比对全错）",
        '        self.file_path.write_text("", encoding="utf-8")',
        "        return None",
        "应导致 test_clear_truncates_file / test_clear_and_recount_identical 失败",
    ),
    (
        TREE_TARGET,
        "Redis 行号下界失效：line_number=0 会退化成 lindex(-1)，返回最后一条而非 None",
        """        if line_number <= 0:
            return None
        path_bytes = self.client.lindex(self._list_key, line_number - 1)""",
        """        if line_number < -1:
            return None
        path_bytes = self.client.lindex(self._list_key, line_number - 1)""",
        "应导致 test_get_path_by_line_number_rejects_non_positive 失败",
    ),
    (
        TREE_TARGET,
        "未 strip 行内容：空行与带空白的行被当成有效路径",
        """                path = line.strip()
                if path:""",
        """                path = line.rstrip("\\n")
                if True:""",
        "应导致 test_count_ignores_blank_lines 失败",
    ),
    # ============ 二、helper/strm/full：Rust 加速开关回落 ============
    (
        FULL_TARGET,
        "回落失效：扩展缺失时仍返回 True（会在 Processor 初始化处炸掉全量同步）",
        """    if Processor is None:
        logger.warning(""",
        """    if False:
        logger.warning(""",
        "应导致 test_enabled_without_extension_falls_back 失败",
    ),
    # ============ 三、pure_scanner.py：分享 STRM 扫描器 ============
    (
        SCANNER_TARGET,
        "后缀过滤失效：任意文件都参与解析（非 STRM 文件被当成分享源）",
        '            if file_path.suffix.lower() == ".strm":',
        "            if True:",
        "应导致 test_ignores_non_strm_and_unparsable 失败",
    ),
    (
        SCANNER_TARGET,
        "同组合覆盖：setdefault 聚合改成直接赋值（一个组合只剩最后一个 STRM）",
        "                    mapping.setdefault(pair, []).append(strm_path)",
        "                    mapping[pair] = [strm_path]",
        "应导致 test_paths_for_many_groups_paths 失败",
    ),
    (
        SCANNER_TARGET,
        "正则贪婪：share_code 吃掉后面的参数，receive_code 抓不到",
        r'''    r"share_code=(?P<share_code>[^&\s\"']+)[^0-9a-zA-Z]*"''',
        r'''    r"share_code=(?P<share_code>.+)[^0-9a-zA-Z]*"''',
        "应导致 test_scan_collects_unique_pairs / test_paths_for_many_groups_paths 失败",
    ),
    (
        SCANNER_TARGET,
        "缓存不失效：invalidate 变成空实现（源文件已删仍返回脏路径）",
        "        self._cache.clear()",
        "        pass",
        "应导致 test_invalidate_drops_stale_cache 失败",
    ),
    (
        SCANNER_TARGET,
        "缺失组合返回非空：paths_for_many 对未知组合给出默认值",
        "            result[pair] = list(mapping.get(pair, []))",
        '            result[pair] = list(mapping.get(pair, ["unexpected"]))',
        "应导致 test_paths_for_many_unknown_pair_returns_empty 失败",
    ),
]


def run_tests():
    """
    跑降级测试，返回 (是否通过, 摘要)
    """
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [os.path.join(HERE, "_stub_host"), PLUGIN_DIR]
    )
    # 两个模块一起跑：降级路径（test_rust_free_fallback）+ 目录树存储
    # （test_tree）——部分变异体（如 Redis 行号下界）由后者守住。
    proc = subprocess.run(
        [
            PYTHON, "-m", "unittest",
            "tests.test_rust_free_fallback",
            "tests.test_tree",
            "-v",
        ],
        cwd=PLUGIN_DIR,
        capture_output=True,
        text=True,
        env=env,
    )
    output = proc.stdout + proc.stderr
    tail = "\n".join(output.strip().splitlines()[-3:])
    return proc.returncode == 0, tail


def main():
    for target, backup in BACKUPS.items():
        shutil.copy(target, backup)
    try:
        return _run()
    finally:
        # 无条件还原：本脚本直接覆写源码，中途异常若不还原，
        # 源码会永久停留在变异状态，后续测试全在污染代码上跑。
        for target, backup in BACKUPS.items():
            shutil.copy(backup, target)


def _run():
    base_ok, base_tail = run_tests()
    print(f"解释器：{PYTHON}")
    print(f"基线：{'✅ 降级测试全部通过' if base_ok else '❌ 基线即失败'}")
    if not base_ok:
        print(base_tail)
        return 1

    sources = {
        target: open(backup, encoding="utf-8").read()
        for target, backup in BACKUPS.items()
    }

    caught = escaped = skipped = 0
    escaped_names = []

    print(f"\n{'=' * 72}")
    print(f"变异测试（Rust 扩展缺失降级路径，共 {len(MUTANTS)} 个变异体）")
    print(f"{'=' * 72}")

    for idx, (target, name, old, new, expect) in enumerate(MUTANTS, 1):
        source = sources[target]
        if old not in source:
            skipped += 1
            print(f"[{idx:>2}] ⚠️  跳过：源码中未找到锚点 —— {name}")
            continue

        with open(target, "w", encoding="utf-8") as handle:
            handle.write(source.replace(old, new, 1))

        ok, tail = run_tests()
        if ok:
            escaped += 1
            escaped_names.append(name)
            print(f"[{idx:>2}] ❌ 逃逸：{name}")
            print(f"       → 变异体全绿，说明测试没守住！{expect}")
        else:
            caught += 1
            print(f"[{idx:>2}] ✅ 捕获：{name}")
            print(f"       → {tail.splitlines()[-1] if tail else 'FAILED'}")

        # 单个变异体跑完立即还原，避免影响下一个
        shutil.copy(BACKUPS[target], target)

    print(f"\n{'=' * 72}")
    print(f"结果：捕获 {caught} / 逃逸 {escaped} / 跳过 {skipped} / 合计 {len(MUTANTS)}")
    if escaped_names:
        print("\n逃逸明细（必须修测试）：")
        for name in escaped_names:
            print(f"  - {name}")
    print("已还原原始源码。")
    return 1 if escaped else 0


if __name__ == "__main__":
    sys.exit(main())
