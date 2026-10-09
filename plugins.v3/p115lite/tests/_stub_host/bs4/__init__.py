"""
``bs4``（BeautifulSoup）宿主桩（stub）

**为什么需要这个桩**

``bs4`` 由 MoviePilot 宿主提供（见 MP V3 的 ``pyproject.toml``），
插件不在自身 ``requirements.txt`` 里声明它。真实运行环境能导入，
但自包含测试套件没有宿主，于是子进程以包整体加载 ``p115lite`` 时，
``helper/search/tg_search/__init__.py`` 顶层的
``from bs4 import BeautifulSoup`` 会失败。

**为什么不直接装 bs4**

这是"宿主桩"而非"依赖补全"：测试套件刻意保持零第三方依赖，
以暴露插件声明与实际使用之间的差异。装 bs4 会掩盖问题。

**实现取向**

与 ``oss2`` 桩里 ``determine_part_size`` 的处理一致 ——
凡是可在无第三方依赖下忠实复现的语义，就用标准库真实实现，
而不是一律抛 ``NotImplementedError``。这里：
``html.parser`` 是标准库模块，``stdlib`` 自带完整的 HTML 解析能力，
因此本桩构建出**真实的 DOM 树**，``select`` / ``select_one`` /
``get_text`` / 属性访问全部是真实语义。这样即便将来有测试
直接构造 HTML 断言 TG 解析结果，也不会因为桩失真而误判。

支持的 CSS 选择器子集（插件实际用到的全部形态）：

* ``.class``            —— 类选择器
* ``tag``               —— 标签名
* ``tag.class`` / ``.a.b`` —— 复合选择器
* 后代选择器（空格分隔）

**不支持** ``>``、``+``、``~``、``:pseudo``、``[attr]`` 等；
遇到未识别片段时按"永不匹配"处理，宁可漏配也不误配。
"""

from html.parser import HTMLParser
from typing import Any, Dict, Iterator, List, Optional

__all__ = [
    "BeautifulSoup",
    "Tag",
    "NavigableString",
]

# ``html.parser`` 解析时这些标签自闭合，不需要结束标签
_VOID_ELEMENTS = frozenset(
    {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }
)


class NavigableString(str):
    """文本节点：直接继承 ``str``，因此 ``str 操作``语义完整"""

    def get_text(self, separator: str = "", strip: bool = False) -> str:
        text = str(self)
        return text.strip() if strip else text


class Tag:
    """
    元素节点

    刻意贴近 bs4 的真实接口：``select`` / ``select_one`` / ``get_text`` /
    ``find`` / ``get`` / ``attrs`` / ``name`` / ``contents``。
    """

    def __init__(
        self,
        name: str,
        attrs: Optional[Dict[str, Any]] = None,
        parent: Optional["Tag"] = None,
    ) -> None:
        self.name = name
        # 属性名统一小写，与 html.parser 行为一致，避免大小写导致漏配
        self.attrs: Dict[str, Any] = {
            str(k).lower(): v for k, v in (attrs or {}).items()
        }
        # 多值属性（class/style 等）在 bs4 中是 list，保持一致
        for key, value in list(self.attrs.items()):
            if key in ("class", "rel", "headers") and isinstance(value, str):
                self.attrs[key] = value.split()
            elif value is None:
                # <div attr> 形式的空属性，bs4 里是空字符串
                self.attrs[key] = ""
        self.parent = parent
        self.contents: List[Any] = []

    # ------------------------------------------------------------------ 属性

    def get(self, key: str, default: Any = None) -> Any:
        """读取属性，缺失时返回 ``default``（与 bs4 一致）"""
        return self.attrs.get(str(key).lower(), default)

    def __getitem__(self, key: str) -> Any:
        return self.attrs[str(key).lower()]

    def __contains__(self, key: str) -> bool:
        return str(key).lower() in self.attrs

    @property
    def classes(self) -> List[str]:
        value = self.attrs.get("class")
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return value.split()
        return []

    # -------------------------------------------------------------- 树遍历

    def __iter__(self) -> Iterator["Tag"]:
        """与 bs4 一致：迭代所有后代，不含自身"""
        for child in self.contents:
            if isinstance(child, Tag):
                yield child
                yield from child

    def descendants(self) -> Iterator["Tag"]:
        yield from self

    def find_all(self, name: Optional[str] = None) -> List["Tag"]:
        """按标签名查找后代（``name=None`` 表示任意标签）"""
        return [t for t in self if name is None or t.name == name]

    def find(self, name: Optional[str] = None) -> Optional["Tag"]:
        for tag in self:
            if name is None or tag.name == name:
                return tag
        return None

    # ------------------------------------------------------------ 文本提取

    def get_text(self, separator: str = "", strip: bool = False) -> str:
        """
        提取子孙节点文本，语义与 bs4 对齐

        * ``strip=True`` 时对**每个**文本片段单独 strip，
          并丢弃空片段（这正是 bs4 的行为，插件依赖它清理空白）；
        * 否则原样拼接，多余空白保留。
        """
        parts: List[str] = []
        for node in self.contents:
            if isinstance(node, Tag):
                parts.append(node.get_text(separator, strip))
            else:
                parts.append(str(node))
        if strip:
            parts = [p.strip() for p in parts if p and p.strip()]
        return separator.join(parts)

    @property
    def text(self) -> str:
        return self.get_text("", strip=False)

    @property
    def stripped_strings(self) -> Iterator[str]:
        for part in self.get_text("\x00", strip=True).split("\x00"):
            if part:
                yield part

    # ------------------------------------------------------------ CSS 选择

    def _match(self, compound: str) -> bool:
        """
        判断单个复合选择器（如 ``div.js-message_text``）是否命中本节点

        无法解析的片段返回 ``False`` —— 宁漏勿误。
        """
        if not compound:
            return False
        if compound.startswith("*"):
            return True
        if "[" in compound or ":" in compound:
            return False  # 属性/伪类选择器未实现

        pieces = [p for p in compound.split(".")]
        tag_part = pieces[0]
        class_parts = pieces[1:]

        if tag_part and tag_part != self.name:
            return False
        if not tag_part and not class_parts:
            return False

        own_classes = set(self.classes)
        return all(cls in own_classes for cls in class_parts if cls)

    def _select_descendants(self, compounds: List[str]) -> List["Tag"]:
        """
        按后代选择器逐级收敛

        第一段在自身内部任意深度匹配，后续每段只在"已命中节点"的
        子树里继续匹配，从而保证 CSS 后代语义（.a .b 要求 b 在 a 内部）。
        """
        if not compounds:
            return []

        head, rest = compounds[0], compounds[1:]
        hits = [tag for tag in self if tag._match(head)]

        for compound in rest:
            next_hits: List["Tag"] = []
            for hit in hits:
                next_hits.extend(tag for tag in hit if tag._match(compound))
            hits = next_hits
            if not hits:
                break
        return hits

    def select(self, selector: str) -> List["Tag"]:
        """
        支持后代选择器的 ``select``

        bs4 允许逗号分隔多组选择器，这里同样支持，取并集后按文档顺序返回。
        """
        results: List["Tag"] = []
        for group in str(selector).split(","):
            compounds = group.split()
            for tag in self._select_descendants(compounds):
                if tag not in results:
                    results.append(tag)
        # 按文档顺序稳定输出
        order = {id(t): i for i, t in enumerate(self)}
        return sorted(results, key=lambda t: order.get(id(t), -1))

    def select_one(self, selector: str) -> Optional["Tag"]:
        hits = self.select(selector)
        return hits[0] if hits else None

    # ------------------------------------------------------------ 序列化

    def decode(self) -> str:
        """
        序列化为 HTML

        ``<br>`` 输出为 ``<br/>`` —— 与 bs4（html.parser）一致。
        插件用 ``re.split("<br.*?>", str(text_element), 1)`` 切分标题与正文，
        依赖的正是这个自闭合形式。
        """
        attrs: List[str] = []
        for key, value in self.attrs.items():
            if isinstance(value, list):
                value = " ".join(value)
            attrs.append(f' {key}="{value}"')
        attr_text = "".join(attrs)

        if self.name in _VOID_ELEMENTS:
            return f"<{self.name}{attr_text}/>"

        inner = "".join(
            node.decode() if isinstance(node, Tag) else str(node)
            for node in self.contents
        )
        return f"<{self.name}{attr_text}>{inner}</{self.name}>"

    def __str__(self) -> str:
        return self.decode()

    def __repr__(self) -> str:
        return f"<stub Tag name={self.name!r} attrs={self.attrs!r}>"


class _SoupBuilder(HTMLParser):
    """把 ``html.parser`` 的事件流组装成 :class:`Tag` 树"""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Tag("[document]")
        self._stack: List[Tag] = [self.root]

    def handle_starttag(self, tag: str, attrs: Any) -> None:
        node = Tag(tag, dict(attrs), parent=self._stack[-1])
        self._stack[-1].contents.append(node)
        if tag not in _VOID_ELEMENTS:
            self._stack.append(node)

    def handle_startendtag(self, tag: str, attrs: Any) -> None:
        node = Tag(tag, dict(attrs), parent=self._stack[-1])
        self._stack[-1].contents.append(node)

    def handle_endtag(self, tag: str) -> None:
        # 容错：未闭合标签不抛错，弹出到最近的同名祖先
        for index in range(len(self._stack) - 1, 0, -1):
            if self._stack[index].name == tag:
                del self._stack[index:]
                return

    def handle_data(self, data: str) -> None:
        if data:
            self._stack[-1].contents.append(NavigableString(data))


class BeautifulSoup(Tag):
    """
    BeautifulSoup 文档根节点

    ``BeautifulSoup(html, "html.parser")`` —— 第二个参数是解析器名，
    本桩忽略它（因为只有标准库这一个解析器）。解析得到的根节点
    同时具备 :class:`Tag` 的全部查询接口。
    """

    def __init__(self, markup: Any = "", features: Any = None, **kwargs: Any) -> None:
        super().__init__("[document]")
        self.parser_name = features
        builder = _SoupBuilder()
        builder.feed(markup if isinstance(markup, str) else str(markup))
        builder.close()
        # 接管根节点的子节点，使 soup 本身即可查询
        self.contents = builder.root.contents
        for child in self.contents:
            if isinstance(child, Tag):
                child.parent = self

    def __repr__(self) -> str:
        return f"<stub BeautifulSoup len(contents)={len(self.contents)}>"
