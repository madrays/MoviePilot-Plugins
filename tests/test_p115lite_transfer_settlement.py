import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "plugins.v3" / "p115lite" / "schemas" / "transfer.py"


class _TransferInfo:
    def __init__(self, success: bool, message: str = ""):
        self.success = success
        self.message = message


def _load_schema_module():
    sdk_media = types.ModuleType("app.sdk.media")
    sdk_media.MediaInfo = type("MediaInfo", (), {})
    sdk_media.MetaBase = type("MetaBase", (), {})
    schemas = types.ModuleType("app.schemas")
    schemas.FileItem = type("FileItem", (), {})
    schemas.TransferInfo = _TransferInfo
    modules = {
        "app": types.ModuleType("app"),
        "app.sdk": types.ModuleType("app.sdk"),
        "app.sdk.media": sdk_media,
        "app.schemas": schemas,
    }
    with patch.dict(sys.modules, modules):
        spec = importlib.util.spec_from_file_location(
            "p115lite_transfer_schema_contract", SCHEMA
        )
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        return module


class P115LiteTransferSettlementTest(unittest.TestCase):
    def test_host_settlement_callback_runs_exactly_once(self) -> None:
        module = _load_schema_module()
        calls = []

        def callback(host_task, transferinfo):
            calls.append((host_task, transferinfo))
            return False, "同名文件，不覆盖"

        task = module.TransferTask(
            fileitem=types.SimpleNamespace(path="/待整理/a.mkv"),
            target_path=Path("/已整理/a.mkv"),
            mediainfo=object(),
            meta=object(),
            transfer_type="move",
            host_task=object(),
            settlement_callback=callback,
        )
        info = _TransferInfo(False, "同名文件，不覆盖")

        self.assertEqual(task.settle(info), (False, "同名文件，不覆盖"))
        self.assertEqual(task.settle(info), (False, "同名文件，不覆盖"))
        self.assertEqual(len(calls), 1)
        self.assertTrue(task.completion_event.is_set())


if __name__ == "__main__":
    unittest.main()
