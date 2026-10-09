"""V3 兼容兜底：宿主已移除 app.schemas.message.ChannelCapabilityManager。

V3 的 Message.buttons 仅为 Optional[List[List[dict]]]，不再提供按渠道查询
按钮能力的方法。本模块以插件本地实现补齐插件交互渲染所需的三个方法，
返回合理默认值（与原行为一致），避免对宿主内部符号的硬依赖。
"""

from typing import Any


class ChannelCapabilityManager:
    """通知渠道按钮能力（本地兜底实现）。"""

    DEFAULT_MAX_BUTTONS_PER_ROW = 5
    DEFAULT_MAX_BUTTON_ROWS = 12

    @classmethod
    def get_max_buttons_per_row(cls, channel: Any = None) -> int:
        return cls.DEFAULT_MAX_BUTTONS_PER_ROW

    @classmethod
    def get_max_button_rows(cls, channel: Any = None) -> int:
        return cls.DEFAULT_MAX_BUTTON_ROWS

    @classmethod
    def supports_buttons(cls, channel: Any = None) -> bool:
        # V3 的 Message 支持 buttons 字段，默认视为支持
        return True
