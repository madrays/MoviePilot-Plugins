#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
变异测试：路径安全与删除边界。

为什么必须做
------------
本插件会**真删用户的媒体文件与目录**，且删除不可逆。已有 43 个边界测试
守着 ``PathUtils.has_prefix``（删前安全闸门）与 ``PathRemoveUtils``（真删），
但边界测试本身极易退化成"永远绿的装饰"——断言写松一点，把防护代码整段
删掉照样通过。

本脚本把防护逻辑逐个拆掉，若某个变异体全绿，说明对应的边界测试**没有
真正守住**，必须收紧断言。这就是"边界测试有效性"的证明方式。

变异体设计原则：每一条都对应一处**真实可能写错的防护**，不是随机改字符。

运行
----
    cd plugins.v3/p115lite
    PYTHONPATH="$PWD/tests/_stub_host:$PWD" python3 tests/mutation_path_safety.py

脚本会临时覆写 ``utils/path.py``，并在 ``finally`` 中**无条件还原**。
"""

import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN_DIR = os.path.dirname(HERE)
TARGET = os.path.join(PLUGIN_DIR, "utils", "path.py")
BACKUP = "/tmp/p115_path_safety_backup.py"

# 实际会用的解释器：默认跟随当前 python，可用环境变量覆盖
PYTHON = os.environ.get("P115_TEST_PYTHON", sys.executable)

# 端到端链路的目标文件（remove_by_path 所在的模块）
E2E_TARGET = os.path.join(PLUGIN_DIR, "helper", "mediasyncdel", "__init__.py")
E2E_BACKUP = "/tmp/p115_msd_backup.py"


# (名称, [(原文, 变异后), ...], 期望被捕获的说明)
#
# 单段替换可写成 (名称, 原文, 变异后, 说明)；多段替换用于表达"组合穿透"——
# 本插件的删除逻辑有防御纵深，只拆一道防线常被另一道兜住，测出的"全绿"是
# 假象（实测：只拆 clean_related_files 的保护，目录里还有别的文件时
# remove_parent_dir 也不会删，结果照样绿）。
MUTANTS = [
    # ================= 一、has_prefix：删除前的安全闸门 =================
    (
        "闸门①失效：分量比较退回朴素字符串 startswith（兄弟目录被误认）",
        """        full = Path(os_normpath(str(full_path).replace("\\\\", "/"))).parts
        prefix = Path(os_normpath(str(prefix_path).replace("\\\\", "/"))).parts

        if len(prefix) > len(full):
            return False

        return full[: len(prefix)] == prefix""",
        """        full = os_normpath(str(full_path).replace("\\\\", "/"))
        prefix = os_normpath(str(prefix_path).replace("\\\\", "/"))
        return full.startswith(prefix)""",
        "应导致 test_sibling_with_common_prefix_refused / test_sibling_suffix_refused 失败",
    ),
    (
        "闸门②失效：不做 normpath 归一化（.. 可越界）",
        """        full = Path(os_normpath(str(full_path).replace("\\\\", "/"))).parts
        prefix = Path(os_normpath(str(prefix_path).replace("\\\\", "/"))).parts""",
        """        full = Path(str(full_path)).parts
        prefix = Path(str(prefix_path)).parts""",
        "应导致 test_dotdot_not_bypassing 失败（.. 绕过闸门）",
    ),
    (
        "闸门③失效：不做反斜杠统一（Windows 路径判定失真）",
        """        full = Path(os_normpath(str(full_path).replace("\\\\", "/"))).parts
        prefix = Path(os_normpath(str(prefix_path).replace("\\\\", "/"))).parts""",
        """        full = Path(os_normpath(str(full_path))).parts
        prefix = Path(os_normpath(str(prefix_path))).parts""",
        "应导致 test_backslash_not_confused 失败",
    ),
    (
        "闸门④失效：前缀比路径长时也放行（len 校验被删）",
        """        if len(prefix) > len(full):
            return False

        return full[: len(prefix)] == prefix""",
        """        if len(prefix) > len(full):
            return True

        return full[: len(prefix)] == prefix""",
        "应导致 test_prefix_longer_than_path_refused 失败（无关路径被认领）",
    ),
    (
        "闸门⑤失效：空值改判为 True（空前缀放行一切 ← 最危险）",
        """        if not full_path or not prefix_path:
            return False""",
        """        if not full_path and not prefix_path:
            return True""",
        "应导致 test_empty_inputs_refused 失败（空路径被当成万能前缀）",
    ),
    (
        "闸门⑥失效：过度归一化，大小写被抹平",
        """        full = Path(os_normpath(str(full_path).replace("\\\\", "/"))).parts
        prefix = Path(os_normpath(str(prefix_path).replace("\\\\", "/"))).parts""",
        """        full = Path(os_normpath(str(full_path).replace("\\\\", "/")).lower()).parts
        prefix = Path(os_normpath(str(prefix_path).replace("\\\\", "/")).lower()).parts""",
        "应导致 test_case_sensitive_on_posix 失败（Linux 上 /Media 与 /media 混淆）",
    ),

    # ================= 二、remove_parent_dir：删目录的范围 =================
    (
        "层数上限失效：一路向上删到根（i>3 的刹车被拆）",
        """                i += 1
                if i > 3:
                    break""",
        """                i += 1""",
        "应导致 test_stops_at_max_parent_levels 失败（可能删到文件系统根）",
    ),
    (
        "mode=all 语义失效：目录非空也删（any(iterdir) 判定反转）",
        """        if mode in ("all", "mixed"):
            func_bool = any(file_path.parent.iterdir())
        else:""",
        """        if mode in ("all", "mixed"):
            func_bool = not any(file_path.parent.iterdir())
        else:""",
        "应导致 test_all_mode_keeps_dir_with_other_files 失败（误删含 mkv 的目录）",
    ),
    (
        "根保护失效：允许删除文件系统根的直接子目录（挂载点被回收）",
        """                if str(parent_path.parent) != str(file_path.root):
                    # 父目录非根目录，才删除父目录
                    if mode == "all" or (mode == "mixed" and i == 1):""",
        """                if True:
                    # 父目录非根目录，才删除父目录
                    if mode == "all" or (mode == "mixed" and i == 1):""",
        # 注意：这道保护只刹车在**根**那一层，深度场景不经过它，
        # 由 test_root_guard_only_protects_root_layer 用 /media 直接覆盖。
        "应导致 test_root_guard_only_protects_root_layer 失败（/media 被删）",
    ),
    (
        "保守返回失效：文件不存在时仍走删除流程（异常/误删）",
        """        if mode in ("all", "mixed"):
            func_bool = any(file_path.parent.iterdir())
        else:
            func_bool = SystemUtils.exits_files(
                directory=file_path.parent, extensions=mode
            )
        if not func_bool:""",
        """        if mode in ("all", "mixed"):
            func_bool = any(file_path.parent.iterdir())
        else:
            func_bool = SystemUtils.exits_files(
                directory=file_path.parent, extensions=mode
            )
        if True:""",
        "应导致 test_missing_file_does_not_crash 失败（目录非空仍进删除流程）",
    ),

    # ================= 三、clean_related_files：连带删除的边界 =================
    (
        "组合穿透：clean_related_files 的 .strm 保护 + remove_parent_dir 的目录保护同时拆除",
        [
            (
                """                and item_to_check.suffix.lower() != ".strm\"""",
                """                and item_to_check.suffix.lower() != ".never-match\"""",
            ),
            (
                """        if mode in ("all", "mixed"):
            func_bool = any(file_path.parent.iterdir())""",
                """        if mode in ("all", "mixed"):
            func_bool = False""",
            ),
        ],
        # 只拆 .strm 保护会「假绿」：被误删的 strm 让目录变空，但目录本身
        # 仍被 remove_parent_dir 的"非空才留"兜住。两道一起拆才测得出。
        "应导致 test_protects_strm_files 失败（同目录 strm 被删）",
    ),
    (
        "连带删除越界：基准文件自身也被删",
        """            if (
                item_to_check.is_file()
                and item_to_check != file_path""",
        """            if (
                item_to_check.is_file()""",
        "应导致 test_keeps_base_file_itself 失败",
    ),
    (
        "连带删除越界：子串匹配放宽成「删除同目录全部文件」",
        """                and file_stem in item_to_check.stem""",
        """                and (file_stem in item_to_check.stem or True)""",
        "应导致 test_unrelated_files_kept / test_keeps_base_file_itself 失败",
    ),
    (
        "连带删除越界：递归到子目录（只应处理同目录）",
        """        for item_to_check in directory.iterdir():""",
        """        for item_to_check in directory.rglob("*"):""",
        "应导致 test_only_same_directory 失败（子目录文件被删）",
    ),

    # ================= 四、mixed 模式上层穿透的对照 =================
    #
    # 说明：``(mode == "mixed" and i == 1)`` 这一句**不能**作为有效变异体。
    # 第一层的进入前置条件是 ``not any(file_path.parent.iterdir())``，即该层
    # 必然为空；此时"按 all 判定"与"按 strm 判定"的结论都是空目录 → 删，
    # 行为完全一致。删掉这句属于**等价变异**（实测：v3 上两者行为逐字节相同）。
    # 这里改为攻击 ``i > 1`` 那条真正决定"能否穿透 sidecar 目录"的分支。
    (
        "mixed 上层穿透失效：改为按 all 判定（含 sidecar 的上级目录残留）",
        """                    elif mode == "mixed":
                        # 混合模式：上层以 ["strm"] 判断，允许穿透含 sidecar 的上级目录
                        func_bool = SystemUtils.exits_files(
                            directory=parent_path, extensions=["strm"]
                        )""",
        """                    elif mode == "mixed":
                        # 混合模式：上层以 ["strm"] 判断，允许穿透含 sidecar 的上级目录
                        func_bool = any(parent_path.iterdir())""",
        "应导致 test_mixed_mode_upper_layer_by_strm 失败（sidecar 目录不再穿透）",
    ),
    # ================= 五、端到端链路（remove_by_path 的删除前置条件） =================
    #
    # 这些变异发生在 ``helper/mediasyncdel/__init__.py``，只有端到端测试
    # （test_sync_del_e2e.py）能捕获 —— 单测不经过这条链路。
    (
        "链路①失效：del_source 时删除前置条件全部放开（非白名单/网盘/move 都删）",
        """                    transferhis.src
                    and Path(transferhis.src).suffix in settings.RMT_MEDIAEXT
                    and transferhis.src_storage == "local"
                    and transferhis.mode != "move\"""",
        """                    transferhis.src""",
        "应导致 test_non_media_suffix_keeps_file / "
        "test_remote_src_storage_keeps_file / test_move_mode_keeps_src 失败"
        "（不该删的文件被真删）",
    ),
    (
        "组合穿透链路②+闸门：跳过空 dest 的防线拆掉，且 has_prefix 彻底短路",
        [
            (
                """            if not dest_path:
                logger.warn(
                    f"【同步删除】转移记录 {transferhis.id} 目标路径为空，跳过删除"
                )
                continue""",
                """            if False:
                continue""",
            ),
            (
                """        if not full_path or not prefix_path:
            return False

        # 本方法在多处充当"删除前"的安全闸门，判定前必须先做两步规范化，
        # 否则会被绕过：""",
                """        return True

        # 本方法在多处充当"删除前"的安全闸门，判定前必须先做两步规范化，
        # 否则会被绕过：""",
            ),
        ],
        # 本变异体刻意做了两次"缩小攻击面"的调整，都记下来：
        #
        # 1) 只拆链路②会「假绿」：`has_prefix(None, ...)` 内部 `not full_path`
        #    返回 False，第二道防线兜住（实测确认）。
        # 2) 只再去掉 `not full_path` **仍然**假绿：`Path(None)` 会变成字符串
        #    "None"，只有 1 个路径分量，下一句 `len(prefix) > len(full)` 又兜住
        #    （实测确认）—— 也就是这里有**三重防御**。
        #    因此必须把闸门整体短路，才能真正体现"链路②失效"的后果。
        "应导致 test_empty_dest_skipped 失败（dest 为空仍被删除）",
    ),
    (
        "链路③失效：del_source 判定反转（仅删记录时删文件 / 反之不删）",
        """            if del_source:""",
        """            if not del_source:""",
        "应导致 test_del_source_false_keeps_file / test_deletes_file_inside_prefix 失败",
    ),
]


def run_tests():
    """
    跑边界 + 端到端测试，返回 (是否通过, 摘要)。

    两个文件一起跑：边界测试验证**函数本身**，端到端验证**函数被接进真实
    删除链路后**行为正确。变异体应同时被两者之一捕获，任一全绿即说明
    该侧覆盖不足。
    """
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [os.path.join(HERE, "_stub_host"), PLUGIN_DIR]
    )
    proc = subprocess.run(
        [
            PYTHON, "-m", "unittest",
            "tests.test_path_remove_boundary",
            "tests.test_sync_del_e2e",
            "-v",
        ],
        cwd=PLUGIN_DIR, capture_output=True, text=True, env=env,
    )
    output = proc.stdout + proc.stderr
    tail = "\n".join(output.strip().splitlines()[-3:])
    return proc.returncode == 0, tail


def main():
    shutil.copy(TARGET, BACKUP)
    shutil.copy(E2E_TARGET, E2E_BACKUP)
    try:
        return _run()
    finally:
        # 关键：必须无条件还原（两个目标文件都要还）。
        # 本脚本直接覆写插件源码，一旦中途抛异常（解包错误、语法错误）而
        # 没走到还原那一步，源码就会**永久停留在变异状态**，后续所有测试
        # 都在被污染的源码上跑，表现为"基线即失败"，极易误判成测试坏了。
        shutil.copy(BACKUP, TARGET)
        shutil.copy(E2E_BACKUP, E2E_TARGET)


def _run():
    base_ok, base_tail = run_tests()
    print(f"解释器：{PYTHON}")
    print(f"基线：{'✅ 边界 + 端到端测试全部通过' if base_ok else '❌ 基线即失败'}")
    if not base_ok:
        print(base_tail)
        return 1

    sources = {
        TARGET: open(BACKUP, encoding="utf-8").read(),
        E2E_TARGET: open(E2E_BACKUP, encoding="utf-8").read(),
    }
    caught = escaped = skipped = 0
    escaped_names = []

    print(f"\n{'=' * 72}")
    print(f"变异测试（路径安全 / 删除边界 / 同步删除链路，共 {len(MUTANTS)} 个变异体）")
    print(f"{'=' * 72}")
    for idx, entry in enumerate(MUTANTS, 1):
        if len(entry) == 4:
            name, old, new, expect = entry
            pairs = [(old, new)]
        else:
            name, pairs, expect = entry

        # 按段定位：每个替换片段各自找到它所在的源文件。
        # 支持**跨文件组合穿透**（例：同时拆 mediasyncdel 的防线与
        # utils/path.py 的 has_prefix 保护）——这是本插件防御纵深下的常态，
        # 只拆一处会被另一处兜住，必须能表达"同时拆多处"。
        plan = []
        unmatched = None
        for old, new in pairs:
            owner = next((p for p, t in sources.items() if old in t), None)
            if owner is None:
                unmatched = old
                break
            plan.append((owner, old, new))
        if unmatched is not None:
            skipped += 1
            print(f"[{idx:2d}] ⚠️  跳过（定位失败）：{name}")
            print(f"        未匹配：{unmatched.strip().splitlines()[0][:70]}")
            continue

        # 按文件分组改写，避免跨文件互相覆盖
        pending = {}
        for owner, old, new in plan:
            pending.setdefault(owner, sources[owner])
            pending[owner] = pending[owner].replace(old, new, 1)
        for owner, text in pending.items():
            with open(owner, "w", encoding="utf-8") as handle:
                handle.write(text)

        ok, tail = run_tests()
        # 跑完立刻还原这些文件，避免影响下一个变异体
        for owner in pending:
            with open(owner, "w", encoding="utf-8") as handle:
                handle.write(sources[owner])

        if ok:
            escaped += 1
            escaped_names.append(name)
            print(f"[{idx:2d}] ❌ 逃逸：{name}\n       （{expect}）")
        else:
            caught += 1
            fails = re.search(r"FAILED \((.*?)\)", tail)
            detail = fails.group(0) if fails else "有失败"
            print(f"[{idx:2d}] ✅ 捕获：{name}\n       → {detail}")

    print(f"\n{'=' * 72}")
    print(f"结果：捕获 {caught} / 逃逸 {escaped} / 跳过 {skipped} / 合计 {caught + escaped + skipped}")
    if escaped_names:
        print("逃逸清单（对应边界测试存在盲区，必须补强）：")
        for name in escaped_names:
            print(f"  - {name}")
    print("已还原原始源码。")
    return 0 if not escaped_names else 2


if __name__ == "__main__":
    sys.exit(main())
