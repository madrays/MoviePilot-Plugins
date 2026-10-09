"""
分享 STRM 扫描器的纯 Python 实现（无 Rust 扩展时的降级路径）

为什么需要
----------
原实现依赖 Rust 扩展 ``share_strm_scan``；当宿主未提供该扩展（3.13 宿主，或未随
插件分发 wheel）时，为了让分享 STRM 清理仍然可用，这里提供一份接口一致、
纯 Python 的 ``ShareStrmScanCache`` 替代品。

接口对齐 Rust 版：
    ``scan(path)``            → 扫描根目录，返回去重后的分享码/提取码组合
    ``paths_for_many(path, pairs)`` → 返回 {组合: [STRM 文件路径...]}
    ``invalidate()``          → 丢弃缓存

解析目标：插件自身生成的 STRM 内容，形如
    {moviepilot}/api/v1/plugin/P115Lite/redirect_url?share_code=XXX&receive_code=YYY&id=ZZZ
同时也兼容 115 分享短链（``115.com/s/<code>`` + 可选 ``code=<提取码>``）。
"""

from pathlib import Path
from re import compile as re_compile
from typing import Dict, Iterable, List, NamedTuple, Optional, Tuple, Union
from urllib.parse import unquote

from app.sdk.logging import logger

__all__ = ["Pair", "PureShareStrmScanCache"]


class Pair(NamedTuple):
    """
    分享码与提取码组合

    用 NamedTuple 以保证与 Rust 版一致的两种用法都成立：
    - 可解包：``share_code, receive_code = pair``
    - 可作字典键：``{pair: [...]}``
    """

    share_code: str
    receive_code: str


# 插件 redirect_url 默认格式：...?share_code=XXX&receive_code=YYY&...
_REDIRECT_PATTERN = re_compile(
    r"share_code=(?P<share_code>[^&\s\"']+)[^0-9a-zA-Z]*"
    r"receive_code=(?P<receive_code>[^&\s\"']*)"
)
# 115 分享短链：https://115.com/s/<share_code>  提取码可能在 code= / password= 参数里
_SHARE_LINK_PATTERN = re_compile(r"115\.com/s/(?P<share_code>[0-9a-zA-Z]+)")
_RECEIVE_CODE_PATTERN = re_compile(
    r"(?:code|password|receive_code)=(?P<receive_code>[0-9a-zA-Z]+)"
)


class PureShareStrmScanCache:
    """
    纯 Python 分享 STRM 扫描器

    扫描根目录（可传多个）下的 ``.strm`` 文件，解析出其中引用的分享组合，
    并维护「组合 → STRM 路径列表」的映射供调用方按失效组合批量定位文件。
    """

    def __init__(self) -> None:
        self._cache: Dict[str, Dict[Pair, List[str]]] = {}

    @staticmethod
    def _normalize_root(path: Union[str, Path]) -> List[Path]:
        """
        规范化扫描根目录

        兼容单个路径与路径列表/元组；不存在或非目录时返回空列表。

        :param path (Union[str, Path]): 根目录或根目录集合
        :return List[Path]: 有效的根目录列表
        """
        candidates = path if isinstance(path, (list, tuple, set)) else [path]
        roots: List[Path] = []
        for item in candidates:
            try:
                resolved = Path(item).expanduser().resolve()
            except Exception:
                continue
            if resolved.is_dir():
                roots.append(resolved)
        return roots

    @staticmethod
    def _iter_strm_files(root: Path) -> Iterable[Path]:
        """
        遍历根目录下所有 .strm 文件（大小写不敏感）

        :param root (Path): 扫描根目录
        :return Iterable[Path]: STRM 文件路径的生成器
        """
        for file_path in root.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.suffix.lower() == ".strm":
                yield file_path

    @staticmethod
    def _extract_pairs(text: str) -> List[Pair]:
        """
        从 STRM 文本内容中解析分享组合

        :param text (str): STRM 文件全文
        :return List[Pair]: 解析出的分享组合（同文件多个时全部返回）
        """
        pairs: List[Pair] = []
        for match in _REDIRECT_PATTERN.finditer(text):
            pairs.append(
                Pair(
                    unquote(match.group("share_code")),
                    unquote(match.group("receive_code") or ""),
                )
            )
        if pairs:
            return pairs

        link_match = _SHARE_LINK_PATTERN.search(text)
        if link_match:
            code_match = _RECEIVE_CODE_PATTERN.search(text)
            pairs.append(
                Pair(
                    link_match.group("share_code"),
                    code_match.group("receive_code") if code_match else "",
                )
            )
        return pairs

    def _scan_root(self, path: Union[str, Path]) -> Dict[Pair, List[str]]:
        """
        扫描根目录并构建「分享组合 → STRM 路径」映射

        :param path (Union[str, Path]): 根目录
        :return Dict[Pair, List[str]]: 映射表
        """
        mapping: Dict[Pair, List[str]] = {}
        for root in self._normalize_root(path):
            for file_path in self._iter_strm_files(root):
                try:
                    text = file_path.read_text(encoding="utf-8", errors="ignore")
                except Exception as error:
                    logger.debug(f"【分享STRM清理】读取失败已跳过: {file_path} {error}")
                    continue
                strm_path = file_path.as_posix()
                for pair in self._extract_pairs(text):
                    mapping.setdefault(pair, []).append(strm_path)
        return mapping

    @staticmethod
    def _as_pair(item) -> Optional[Pair]:
        """
        把调用方传入的各种组合形态统一成 Pair

        :param item: Pair / 二元组 / 二元列表
        :return Optional[Pair]: 规范化后的 Pair，无法解析时返回 None
        """
        if isinstance(item, Pair):
            return item
        try:
            share_code, receive_code = item
        except (TypeError, ValueError):
            return None
        return Pair(str(share_code), str(receive_code or ""))

    def scan(self, path: Union[str, Path]) -> List[Pair]:
        """
        扫描目录，返回其中出现的分享组合（已去重）

        :param path (Union[str, Path]): 扫描根目录
        :return List[Pair]: 分享组合列表
        """
        mapping = self._scan_root(path)
        self._cache[str(path)] = mapping
        return list(mapping.keys())

    def paths_for_many(
        self, path: Union[str, Path], pairs: Iterable
    ) -> Dict[Pair, List[str]]:
        """
        批量返回指定分享组合对应的 STRM 文件路径

        :param path (Union[str, Path]): 扫描根目录（与 scan 相同）
        :param pairs (Iterable): 分享组合集合
        :return Dict[Pair, List[str]]: {组合: [STRM 路径...]}
        """
        mapping = self._cache.get(str(path))
        if mapping is None:
            mapping = self._scan_root(path)
            self._cache[str(path)] = mapping

        result: Dict[Pair, List[str]] = {}
        for item in pairs or []:
            pair = self._as_pair(item)
            if pair is None:
                continue
            result[pair] = list(mapping.get(pair, []))
        return result

    def invalidate(self) -> None:
        """
        丢弃已缓存的扫描结果
        """
        self._cache.clear()
