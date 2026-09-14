#!/usr/bin/env python3
"""校验 MoviePilot V3 市场索引与插件源码的安装身份是否一致。"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "package.v3.json"
PLUGINS_ROOT = ROOT / "plugins.v3"
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


def class_attributes(source: Path) -> dict[str, Any]:
    """读取唯一插件类的字面量身份字段，不导入也不执行插件源码。"""
    tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    candidates: list[dict[str, Any]] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        attributes: dict[str, Any] = {}
        for statement in node.body:
            if (
                isinstance(statement, ast.Assign)
                and len(statement.targets) == 1
                and isinstance(statement.targets[0], ast.Name)
                and isinstance(statement.value, ast.Constant)
            ):
                attributes[statement.targets[0].id] = statement.value.value
        if "plugin_name" in attributes:
            candidates.append(attributes)
    if len(candidates) != 1:
        raise ValueError(f"应存在唯一插件类，实际找到 {len(candidates)} 个")
    return candidates[0]


def main() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    expected_dirs: set[str] = set()

    for plugin_id, metadata in manifest.items():
        directory = plugin_id.lower()
        expected_dirs.add(directory)
        source = PLUGINS_ROOT / directory / "__init__.py"
        if not source.is_file():
            errors.append(f"{plugin_id}: 缺少 V3 源码 {source.relative_to(ROOT)}")
            continue
        if metadata.get("release"):
            errors.append(f"{plugin_id}: 不能声明 release=true，仓库未发布对应 Release 资产")
        if metadata.get("system_version") != ">=3.0.0":
            errors.append(f"{plugin_id}: system_version 必须为 >=3.0.0")
        version = metadata.get("version")
        if not isinstance(version, str) or not VERSION_RE.fullmatch(version):
            errors.append(f"{plugin_id}: V3 版本号无效：{version!r}")
            continue
        try:
            attributes = class_attributes(source)
        except (SyntaxError, ValueError) as error:
            errors.append(f"{plugin_id}: 无法读取插件身份：{error}")
            continue
        if attributes.get("plugin_name") != metadata.get("name"):
            errors.append(
                f"{plugin_id}: 插件名称不一致，源码={attributes.get('plugin_name')!r}，"
                f"市场={metadata.get('name')!r}"
            )
        if attributes.get("plugin_version") != version:
            errors.append(
                f"{plugin_id}: 插件版本不一致，源码={attributes.get('plugin_version')!r}，市场={version!r}"
            )
        expected_prefix = f"{directory}_"
        if attributes.get("plugin_config_prefix") != expected_prefix:
            errors.append(
                f"{plugin_id}: 配置前缀不一致，源码={attributes.get('plugin_config_prefix')!r}，"
                f"应为={expected_prefix!r}"
            )

    actual_dirs = {path.name for path in PLUGINS_ROOT.iterdir() if path.is_dir()}
    for directory in sorted(actual_dirs - expected_dirs):
        errors.append(f"{directory}: V3 源码目录未被 package.v3.json 发布")
    if errors:
        print("V3 插件身份校验失败：", file=sys.stderr)
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"V3 插件身份校验通过：{len(manifest)} 个插件")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
