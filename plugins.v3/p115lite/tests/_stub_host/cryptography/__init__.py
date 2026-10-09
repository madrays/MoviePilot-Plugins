"""
``cryptography`` 宿主桩

**为什么需要这个桩**

``cryptography`` 由 MoviePilot V3 宿主提供（官方 ``pyproject.toml`` 声明
``cryptography~=50.0.0``），插件用 ``hazmat.primitives.hashes`` 计算文件
SHA1 校验值，但不在自己的 ``requirements.txt`` 里声明。

自包含测试套件没有宿主，子进程以包整体加载插件时该导入会失败。
本桩只覆盖插件实际用到的 ``hashes`` 子模块。
"""
