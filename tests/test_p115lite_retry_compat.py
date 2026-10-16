import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "plugins.v3" / "p115lite" / "utils" / "transfer_compat.py"


class _Logger:
    def __init__(self) -> None:
        self.info_messages = []
        self.warning_messages = []
        self.debug_messages = []
        self.error_messages = []

    def info(self, message, *args, **kwargs) -> None:
        self.info_messages.append(str(message))

    def warning(self, message, *args, **kwargs) -> None:
        self.warning_messages.append(str(message))

    def debug(self, message, *args, **kwargs) -> None:
        self.debug_messages.append(str(message))

    def error(self, message, *args, **kwargs) -> None:
        self.error_messages.append(str(message))


def _load_module(logger: _Logger):
    sdk_logging = types.ModuleType("app.sdk.logging")
    sdk_logging.logger = logger
    modules = {
        "app": types.ModuleType("app"),
        "app.sdk": types.ModuleType("app.sdk"),
        "app.sdk.logging": sdk_logging,
    }
    spec = importlib.util.spec_from_file_location(
        "p115lite_retry_compat_contract",
        MODULE,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(module)
    return module


class P115LiteRetryCompatTest(unittest.TestCase):
    def test_abandons_host_admission_before_plugin_takeover(self) -> None:
        logger = _Logger()
        module = _load_module(logger)
        calls = []

        class Repository:
            def abandon_unstarted(self, *, task_id, lease_token):
                calls.append((task_id, lease_token))
                return True

        chain = types.SimpleNamespace(_transfer_admissions=Repository())
        task = types.SimpleNamespace(
            admission_task_id="task-1",
            lease_token="lease-1",
        )
        self.assertTrue(
            module.abandon_taken_over_admission(
                chain,
                task,
                reason="115Lite takeover",
            )
        )
        self.assertEqual(calls, [("task-1", "lease-1")])

    def test_refuses_takeover_when_admission_cannot_be_abandoned(self) -> None:
        logger = _Logger()
        module = _load_module(logger)
        task = types.SimpleNamespace(
            admission_task_id="task-2",
            lease_token="lease-2",
        )
        self.assertFalse(
            module.abandon_taken_over_admission(
                object(),
                task,
                reason="missing repository",
            )
        )

    def test_prefers_v3_durable_retry_api(self) -> None:
        logger = _Logger()
        module = _load_module(logger)
        history = types.SimpleNamespace(id=17)

        class Chain:
            def __init__(self) -> None:
                self.calls = []

            def _request_durable_transfer_retry(self, value, *, requested_by):
                self.calls.append((value, requested_by))
                return True, "已进入重试等待"

        chain = Chain()
        self.assertTrue(module.trigger_ai_transfer_retry(chain, history))
        self.assertEqual(chain.calls, [(history, "p115lite_ai_retry")])
        self.assertTrue(any("durable AI 重试" in item for item in logger.info_messages))

    def test_falls_back_to_legacy_scheduler(self) -> None:
        logger = _Logger()
        module = _load_module(logger)
        calls = []

        class Scheduler:
            def schedule_retry(self, history_id, *, group_key):
                calls.append((history_id, group_key))
                return object()

        chain = types.SimpleNamespace(retry_scheduler=Scheduler())
        config = types.ModuleType("app.sdk.config")
        config.global_vars = types.SimpleNamespace(loop=object())
        with (
            patch.dict(sys.modules, {"app.sdk.config": config}),
            patch("asyncio.run_coroutine_threadsafe") as submit,
        ):
            self.assertTrue(
                module.trigger_ai_transfer_retry(
                    chain,
                    types.SimpleNamespace(id=23),
                    group_key="group",
                )
            )
        self.assertEqual(calls, [(23, "group")])
        submit.assert_called_once()

    def test_missing_retry_api_warns_only_once(self) -> None:
        logger = _Logger()
        module = _load_module(logger)
        history = types.SimpleNamespace(id=42)

        self.assertFalse(module.trigger_ai_transfer_retry(object(), history))
        self.assertFalse(module.trigger_ai_transfer_retry(object(), history))
        self.assertEqual(len(logger.warning_messages), 1)
        self.assertIn("未提供可用的 AI 整理重试接口", logger.warning_messages[0])


if __name__ == "__main__":
    unittest.main()
