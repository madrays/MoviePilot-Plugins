import json
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins.v3" / "p115lite"
FRONTEND = ROOT / "frontend" / "p115lite"


class P115LiteContractTest(unittest.TestCase):
    """验证 115Lite 的身份、依赖锁与删减边界"""

    def test_manifest_identity(self) -> None:
        """市场 ID、名称和版本必须保持独立"""
        manifest = json.loads((ROOT / "package.v3.json").read_text())
        metadata = manifest["P115Lite"]
        self.assertEqual(metadata["name"], "115Lite")
        self.assertEqual(metadata["version"], "3.0.3")
        self.assertIs(metadata["release"], True)
        self.assertEqual(
            metadata["description"],
            "115Lite 自用版，感谢原作者 DDSRem、zkmydgth",
        )
        self.assertTrue(metadata["icon"].endswith("/icons/p115lite.png"))
        self.assertTrue((ROOT / "icons" / "p115lite.png").is_file())
        source = (PLUGIN / "__init__.py").read_text()
        self.assertIn('class P115Lite(_PluginBase):', source)
        self.assertIn(
            'from .storage import P115LiteStorageMixin as _P115LiteStorageMixin',
            source,
        )
        self.assertNotIn('from .storage import P115LiteStorageMixin\n', source)
        self.assertIn('plugin_config_prefix = "p115lite_"', source)

    def test_commands_are_short_and_have_no_underscores(self) -> None:
        """用户可见命令保持短小，内部 action 名可继续兼容旧实现"""
        source = (PLUGIN / "__init__.py").read_text()
        commands = [
            "/115full",
            "/115inc",
            "/115save",
            "/115share",
            "/115down",
            "/115strm",
        ]
        for command in commands:
            self.assertIn(f'"cmd": "{command}"', source)
            self.assertNotIn("_", command)
            self.assertLessEqual(len(command), 10)
        self.assertNotIn('"cmd": "/p115lite_', source)

    def test_dependency_pair_is_exact(self) -> None:
        """p115client 与 concurrenttools 必须成对精确锁定"""
        project = tomllib.loads((PLUGIN / "pyproject.toml").read_text())
        dependencies = set(project["project"]["dependencies"])
        self.assertIn("p115client==0.0.9.6.5.1", dependencies)
        self.assertIn("python-concurrenttools==0.1.8", dependencies)
        self.assertEqual(project["project"]["requires-python"], ">=3.14,<3.15")

    def test_removed_feature_modules_are_absent(self) -> None:
        """明确要求删除的模块不能重新进入发行目录"""
        removed = [
            "core/aliyunpan.py",
            "helper/ali2115",
            "helper/fuse",
            "helper/hdhive",
            "helper/monitor",
            "helper/search",
            "service/fuse",
            "service/hdhive_checkin",
            "service/p115_checkin",
            "sidebar_nav.py",
        ]
        for relative in removed:
            path = PLUGIN / relative
            if path.is_dir():
                self.assertFalse(any(path.rglob("*.py")), relative)
            else:
                self.assertFalse(path.exists(), relative)

    def test_storage_does_not_expose_upload(self) -> None:
        """合并后的 115Lite 存储不得声明上传模块接口"""
        adapter = (PLUGIN / "storage" / "adapter.py").read_text()
        self.assertNotIn('"upload_file":', adapter)
        self.assertNotIn("def upload_file(", adapter)

    def test_federation_keeps_original_surfaces_without_sidebar(self) -> None:
        """联邦前端保留 Page/Config/Dashboard，但不再暴露侧边栏入口"""
        vite = (FRONTEND / "vite.config.js").read_text()
        self.assertIn("'./Page'", vite)
        self.assertIn("'./Config'", vite)
        self.assertIn("'./Dashboard'", vite)
        self.assertNotIn("'./AppPageStart'", vite)
        self.assertTrue((PLUGIN / "dist" / "assets" / "remoteEntry.js").is_file())

    def test_removed_frontend_tabs_are_absent(self) -> None:
        """前端不再显示点名删除的功能标签"""
        pan = (FRONTEND / "src/components/sections/PanManagementSection.vue").read_text()
        other = (FRONTEND / "src/components/sections/OtherFeaturesSection.vue").read_text()
        system = (FRONTEND / "src/components/sections/SystemConfigSection.vue").read_text()
        self.assertNotIn('value="tab-pan-mount"', pan)
        self.assertNotIn('value="tab-directory-upload"', pan)
        self.assertNotIn('value="tab-tg-search"', other)
        self.assertNotIn('value="tab-same-playback"', other)
        self.assertNotIn('value="tab-hdhive-checkin"', other)
        self.assertNotIn('value="tab-p115-checkin"', other)
        self.assertNotIn('v-model="config.sidebar_nav_keys"', system)
        self.assertNotIn('v-model="config.upload_module_enhancement"', system)

    def test_lite_config_import_and_removed_controls(self) -> None:
        """精简界面不显示点名选项，并提供原版配置换算入口"""
        config = (FRONTEND / "src/components/Config.vue").read_text()
        pan = (FRONTEND / "src/components/sections/PanManagementSection.vue").read_text()
        other = (FRONTEND / "src/components/sections/OtherFeaturesSection.vue").read_text()
        backend = (PLUGIN / "api.py").read_text()
        routes = (PLUGIN / "__init__.py").read_text()

        self.assertNotIn("交由 CloudDrive2 储存整理", pan)
        self.assertNotIn("开启多版本删除", other)
        self.assertNotIn("需要使用神医助手PRO", other)
        self.assertIn("获取原版配置", config)
        self.assertIn("get_original_config_api", backend)
        self.assertIn('converted["storage_module"] = "115Lite"', backend)
        self.assertIn('"path": "/get_original_config"', routes)

    def test_transfer_patch_uses_v3_scrape_settlement_api(self) -> None:
        """整理接管使用 V3 当前接口，并兼容旧插件的名字改写调用"""
        patcher = (PLUGIN / "patch" / "transfer_chain.py").read_text()
        service = (PLUGIN / "service" / "__init__.py").read_text()

        self.assertIn('current_name = "_finish_scrape_batch_task"', patcher)
        self.assertIn('legacy_name = "_TransferChain__finish_scrape_batch_task"', patcher)
        self.assertIn("resolve_scrape_batch_finish(chain_self)", patcher)
        self.assertNotIn(
            "chain_self._TransferChain__finish_scrape_batch_task(task)",
            patcher,
        )
        self.assertNotIn("check_patch_target(transfer_chain.jobview", patcher)
        self.assertIn("cls._verify_jobview_once(chain_self)", patcher)
        self.assertIn("TransferChainPatcher.ensure_host_compatibility()", service)

    def test_takeover_abandons_host_durable_admission_before_batching(self) -> None:
        """接管前必须注销宿主恢复责任，否则回退原生整理"""
        patcher = (PLUGIN / "patch" / "transfer_chain.py").read_text()
        service = (PLUGIN / "service" / "__init__.py").read_text()
        system = (FRONTEND / "src/components/sections/SystemConfigSection.vue").read_text()

        self.assertIn("abandon_taken_over_admission(", patcher)
        self.assertNotIn("_prepare_durable_checkpoint", patcher)
        self.assertNotIn("plugin_task.completion_event.wait", patcher)
        self.assertNotIn("settlement_callback=callback", patcher)
        self.assertIn("return cls._call_original(chain_self, task, callback)", patcher)
        self.assertIn("V3 durable 责任隔离", service)
        self.assertIn("接管网盘整理", system)


if __name__ == "__main__":
    unittest.main()
