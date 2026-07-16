# Godot 运行验收 Demo

此目录是 Godot 4.7.1 Stable 的最小运行验收项目，只验证便携引擎、项目解析、主场景加载和 GDScript 执行，不代表正式游戏产品方向。

## 编辑器运行

使用已验证的普通版编辑器打开 `demo/project.godot`，然后运行主场景。窗口会显示 `Codex Godot Runtime Validation`、Godot 版本环境和绿色 `Runtime Ready` 状态；状态文字的轻微脉冲表示脚本正在执行。

## CLI 运行

在仓库根目录执行：

```powershell
& 'E:\Workspace\tools\Godot\4.7.1\Godot_v4.7.1-stable_win64_console.exe' --headless --path '.\demo' --quit-after 300
```

成功输出必须包含：

```text
CODEX_GODOT_RUNTIME_START
CODEX_GODOT_RUNTIME_READY
```

headless 模式会在验证完成后由脚本主动退出，不会留下持续运行的 Godot 进程。
