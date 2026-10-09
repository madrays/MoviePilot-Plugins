"""
``pytz`` 宿主桩

**为什么需要这个桩**

``pytz`` 由 MoviePilot V3 宿主提供（其依赖链中包含它），插件用
``pytz.timezone(settings.TZ)`` 构造带时区的时间对象，但不在自己的
``requirements.txt`` 里声明。

**实现方式**

Python 3.9+ 标准库自带 ``zoneinfo``，与 ``pytz`` 在"按 IANA 时区名取
tzinfo 对象"这一用途上等价。本桩基于 ``zoneinfo`` 给出**真实可用**的实现，
而非空壳——被测代码真的构造时区对象时，得到的结果与线上一致。

注意：``pytz`` 的 ``localize()`` 归一化语义与 ``zoneinfo`` 不同，
本桩不提供该方法。若插件后续用到 ``localize``，需要显式改用 DST 敏感写法，
到时这里会明确报 ``AttributeError``，不会被静默掩盖。
"""

from datetime import tzinfo
from typing import Optional

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

__all__ = [
    "timezone",
    "utc",
    "AmbiguousTimeError",
    "NonExistentTimeError",
]


class AmbiguousTimeError(Exception):
    """夏令时切换导致的歧义时间异常（保留类型名，与真实库对齐）"""


class NonExistentTimeError(Exception):
    """夏令时切换导致的不存在时间异常（保留类型名，与真实库对齐）"""


class _UTC(tzinfo):
    """``pytz.utc`` 的等价实现，固定零偏移"""

    zone = "UTC"

    def utcoffset(self, dt: Optional[object]) -> object:
        from datetime import timedelta

        return timedelta(0)

    def dst(self, dt: Optional[object]) -> object:
        from datetime import timedelta

        return timedelta(0)

    def tzname(self, dt: Optional[object]) -> str:
        return "UTC"

    def __repr__(self) -> str:
        return "<stub pytz.utc>"


#: 常用 UTC 单例，与 ``pytz.utc`` 用法一致
utc = _UTC()


def timezone(zone: str, is_dst: Optional[bool] = None) -> tzinfo:
    """
    按 IANA 时区名返回 tzinfo 对象

    与 ``pytz.timezone`` 的签名兼容（``is_dst`` 参数保留但交由
    ``zoneinfo`` 自行处理 DST）。常见取值如 ``"Asia/Shanghai"``、
    ``"UTC"`` 均可正常解析。

    :param zone (str): IANA 时区名
    :param is_dst (bool, optional): 兼容参数，当前实现忽略
    :return tzinfo: 时区对象
    :raises UnknownTimeZoneError: 时区名无法识别时抛出
    """
    if zone is None or not str(zone).strip():
        raise UnknownTimeZoneError(f"无效的时区名: {zone!r}")
    name = str(zone).strip()
    if name.upper() == "UTC":
        return utc
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError, KeyError) as exc:
        raise UnknownTimeZoneError(f"未知时区: {name!r}") from exc


class UnknownTimeZoneError(KeyError):
    """时区名无法识别时抛出，与真实库的异常同名同基类"""

    def __str__(self) -> str:
        return self.args[0] if self.args else "unknown timezone"
