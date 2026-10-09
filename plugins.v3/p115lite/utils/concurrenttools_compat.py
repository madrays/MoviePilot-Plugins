"""
python-concurrenttools 兼容适配层（有条件兼容别名）。

p115client ``0.0.9.6.5.1`` 在 import 期直接执行::

    from concurrenttools import threadpool_map, taskgroup_map

而 python-concurrenttools ``0.1.9``（2026-09-29）把这两个函数改名为
``thread_conmap`` / ``async_conmap``（其余 ``conmap`` / ``run_as_thread`` /
``iter_page*`` / ``iter_offset*`` 未变）。MoviePilot 的插件依赖装在共享
venv 里，一旦该环境已经存在 0.1.9，本插件就会在 import 阶段直接
``ImportError: cannot import name 'threadpool_map'`` 而加载失败。

治本手段是 requirements.txt 里锁 ``python-concurrenttools<0.1.9``，但插件安装
无法降级宿主已装依赖，锁版本对"环境里已经是 0.1.9"的用户无能为力。本模块因此
提供**有条件兼容别名**：仅在旧名缺失、新名存在时把新函数别名为旧名，让
p115client 能 import 成功并正常工作。

别名不是治本，它把"加载即崩"降级为"能跑"：等到 p115client 升级到适配 0.1.9
的版本后，本模块与 requirements 里的上限应一并移除。
"""

from typing import List, Tuple

__all__ = [
    "LEGACY_CONCURRENTTOOLS_ALIASES",
    "ensure_legacy_concurrenttools_aliases",
]

# (旧名, 新名)：python-concurrenttools 0.1.9 的改名对照
LEGACY_CONCURRENTTOOLS_ALIASES: Tuple[Tuple[str, str], ...] = (
    ("threadpool_map", "thread_conmap"),
    ("taskgroup_map", "async_conmap"),
)


def ensure_legacy_concurrenttools_aliases() -> List[str]:
    """
    按需把 concurrenttools 的新函数名别名回 p115client 期望的旧名。

    判断规则（三者互相独立）：
    - 旧名已存在 → 跳过（0.1.8 等旧版本，不做任何改动）；
    - 旧名缺失且新名存在 → 挂别名并记入返回值；
    - 新旧名都缺失 → 跳过（不写入不存在的符号，避免把问题变成更晚才炸）。

    :return List[str]: 本次实际挂载的旧名列表；无需挂载或挂载失败时为空列表
    """

    applied: List[str] = []
    try:
        import concurrenttools
    except Exception:
        return applied

    for old_name, new_name in LEGACY_CONCURRENTTOOLS_ALIASES:
        if hasattr(concurrenttools, old_name):
            continue
        replacement = getattr(concurrenttools, new_name, None)
        if replacement is None:
            continue
        try:
            setattr(concurrenttools, old_name, replacement)
        except Exception:
            continue
        applied.append(old_name)

    return applied
