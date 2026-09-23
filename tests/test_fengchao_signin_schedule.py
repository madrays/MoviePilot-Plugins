import ast
import json
import random
import unittest
import uuid
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


def load_snapshot_push():
    module = ast.parse(PLUGIN_SOURCE.read_text(encoding="utf-8"))
    plugin = next(
        node
        for node in module.body
        if isinstance(node, ast.ClassDef) and node.name == "FengchaoSignin"
    )
    function = next(
        node
        for node in plugin.body
        if isinstance(node, ast.FunctionDef) and node.name == "__api_push_stats"
    )

    class StatsNotReady(RuntimeError):
        pass

    namespace = {"_MoviePilotStatsNotReady": StatsNotReady}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(PLUGIN_SOURCE), "exec"), namespace)
    return namespace["__api_push_stats"], StatsNotReady


def load_instance_id_resolver():
    module = ast.parse(PLUGIN_SOURCE.read_text(encoding="utf-8"))
    function = next(
        node
        for node in module.body
        if isinstance(node, ast.FunctionDef) and node.name == "_resolve_instance_id"
    )
    namespace = {"uuid": uuid}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(PLUGIN_SOURCE), "exec"), namespace)
    return namespace["_resolve_instance_id"]


class FengchaoScheduleTests(unittest.TestCase):
    def test_restart_after_key_rotation_keeps_new_persisted_instance_id(self):
        resolve_instance_id = load_instance_id_resolver()
        old_instance_id = "4c17d360-e63f-45f3-a453-3a2ed1a7382a"

        rotated_instance_id = resolve_instance_id(old_instance_id, old_instance_id, True)
        self.assertNotEqual(rotated_instance_id, old_instance_id)
        self.assertEqual(uuid.UUID(rotated_instance_id).version, 4)

        restarted_instance_id = resolve_instance_id(old_instance_id, rotated_instance_id, False)
        self.assertEqual(restarted_instance_id, rotated_instance_id)

    def test_configured_instance_id_remains_a_migration_fallback(self):
        resolve_instance_id = load_instance_id_resolver()
        configured_instance_id = "4c17d360-e63f-45f3-a453-3a2ed1a7382a"

        self.assertEqual(resolve_instance_id(configured_instance_id, "", False), configured_instance_id)

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

    def test_empty_local_statistics_never_reach_the_forum(self):
        push_snapshot, stats_not_ready = load_snapshot_push()

        class Plugin:
            _instance_id = "instance"
            plugin_version = "3.1.3"
            _current_batch_id = None

            @staticmethod
            def _get_site_statistics():
                return {"sites": []}

            @staticmethod
            def __api_request(*_args, **_kwargs):
                raise AssertionError("empty snapshots must stay local")

        with self.assertRaisesRegex(stats_not_ready, "站点统计尚未加载"):
            push_snapshot(Plugin())

    def test_local_statistics_retries_are_short_and_bounded(self):
        module = ast.parse(PLUGIN_SOURCE.read_text(encoding="utf-8"))
        assignment = next(
            node
            for node in module.body
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "LOCAL_STATS_RETRY_DELAYS_SECONDS" for target in node.targets)
        )
        delays = ast.literal_eval(assignment.value)

        self.assertEqual(delays, (30, 90, 180))
        self.assertLessEqual(sum(delays), 300)

    def test_disabled_pt_sync_is_visible_in_the_plugin_status(self):
        source = PLUGIN_SOURCE.read_text(encoding="utf-8")

        self.assertIn('if not self._mp_push_enabled:', source)
        self.assertIn('account_state = "PT 同步已关闭"', source)

    def test_pt_snapshot_uploads_site_user_id_separately_from_username(self):
        source = PLUGIN_SOURCE.read_text(encoding="utf-8")

        self.assertIn('"siteUserId": str(site.get("userid") or "")', source)
        self.assertIn('"username": str(site.get("username") or "")', source)
        self.assertIn('"joinAt": str(site.get("join_at") or "")', source)
        self.assertIn('"schemaVersion": 2', source)

    def test_task_logs_expose_schedule_result_retry_and_notification_state(self):
        source = PLUGIN_SOURCE.read_text(encoding="utf-8")

        self.assertIn("[蜂巢任务] 计划已就绪", source)
        self.assertNotIn("self._scheduler.print_jobs()", source)
        self.assertIn("[蜂巢签到] 开始", source)
        self.assertIn("[蜂巢签到] 成功", source)
        self.assertIn("[蜂巢签到] 失败", source)
        self.assertIn("[蜂巢 PT 人生] 成功", source)
        self.assertIn("下次重试=%s", source)
        self.assertIn("已提交 MoviePilot 通知链", source)
        self.assertIn("未发送（结果通知已关闭）", source)
        self.assertIn("exc_info=True", source)

    def test_network_copy_states_ipv4_and_proxy_boundaries(self):
        source = PLUGIN_SOURCE.read_text(encoding="utf-8")

        self.assertIn("当前论坛服务器仅支持 IPv4 回连", source)
        self.assertIn("纯 IPv6 地址无法接通", source)
        self.assertIn("支持显式非 443 端口", source)
        self.assertIn("目前仅支持国内出口 IP", source)
        self.assertIn("建议保持关闭", source)

    def test_plugin_catalog_publishes_the_3_1_6_release(self):
        catalog = json.loads((PLUGIN_SOURCE.parents[2] / "package.json").read_text(encoding="utf-8"))

        self.assertEqual(catalog["FengchaoSignin"]["version"], "3.1.6")
        self.assertIn("v3.1.6", catalog["FengchaoSignin"]["history"])


if __name__ == "__main__":
    unittest.main()
