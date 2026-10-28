# GlaDOS 签到 · 前端（Vue 联邦插件）

MoviePilot 远程组件，暴露 `./Page`、`./Config`、`./Dashboard`。

## 构建

```bash
cd frontend/gladossign
npm install
npm run build
cp -R dist ../../../plugins.v3/gladossign/dist
```

构建产物必须同步到 `plugins.v3/gladossign/dist/`，插件通过
`get_render_mode() -> ("vue", "dist/assets")` 加载。

## 宿主契约

- 宿主直接把 `api`、`pluginId`、`sourcePluginId`、`nativeSubscribe` 作为 props 传给组件
- `Config` 额外接收 `initialConfig`
- 保存配置：`emit('save', config)`
- 认证接口：`props.api.get/post(\`plugin/${pluginId}/...\`)`，后端声明 `auth: "bear"`

## 本地调试

```bash
npm run dev
# 打开 http://localhost:5002/dev-harness.html
```

`dev-harness` 用模拟 api 渲染三个组件，可验证登录、发码、签到与保存交互。
