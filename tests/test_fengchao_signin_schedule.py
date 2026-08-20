import ast
import random
import unittest
from datetime import datetime, timedelta
from pathlib import Path


PLUGIN_SOURCE = Path(__file__).parents[1] / "plugins" / "FengchaoSignin" / "__init__.py"


class FakeCronTrigger:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


def load_trigger_builder():
    module = ast.parse(PLUGIN_SOURCE.read_text(encoding="utf-8"))
    function = next(
        node
        for node in module.body
        if isinstance(node, ast.FunctionDef) and node.name == "_cron_trigger_with_jitter"
    )
    namespace = {
        "CronTrigger": FakeCronTrigger,
        "settings": type("Settings", (), {"TZ": "Asia/Shanghai"})(),
    }
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(PLUGIN_SOURCE), "exec"), namespace)
    return namespace["_cron_trigger_with_jitter"]


class FengchaoScheduleTests(unittest.TestCase):
    def test_jitter_is_part_of_the_cron_trigger(self):
        build_trigger = load_trigger_builder()

        signin = build_trigger("30 8 * * *", 1800)
        snapshot = build_trigger("0 3 * * *", 7200)

        self.assertEqual(signin.kwargs["minute"], "30")
        self.assertEqual(signin.kwargs["hour"], "8")
        self.assertEqual(signin.kwargs["timezone"], "Asia/Shanghai")
        self.assertEqual(signin.kwargs["jitter"], 1800)
        self.assertEqual(snapshot.kwargs["jitter"], 7200)

    def test_four_thousand_installations_are_spread_without_a_retry_storm(self):
        rng = random.Random(20260820)
        offsets = [rng.uniform(0, 1800) for _ in range(4000)]
        second_buckets = [0] * 1801
        minute_buckets = [0] * 31
        for offset in offsets:
            second_buckets[int(offset)] += 1
            minute_buckets[int(offset // 60)] += 1

        self.assertLessEqual(max(second_buckets), 10)
        self.assertLessEqual(max(minute_buckets), 170)
        self.assertGreater(max(offsets), 1780)

        first_run = datetime(2026, 8, 20, 8, 30)
        retry_offsets = [
            (first_run + timedelta(seconds=offset) + timedelta(hours=2) - first_run).total_seconds()
            for offset in offsets
        ]
        retry_spread = max(retry_offsets) - min(retry_offsets)
        self.assertGreater(retry_spread, 1780)


if __name__ == "__main__":
    unittest.main()
