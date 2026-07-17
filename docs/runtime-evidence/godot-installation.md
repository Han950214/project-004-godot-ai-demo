# Godot 4.7.1 便携部署证据

当前受限沙箱无法在线构建 Authenticode 证书链，因此本阶段签名复核记为 `not_available_in_sandbox`，并沿用 Phase 2A 已记录的 `Valid` 结果。Phase 2A 只记录 Release ZIP 哈希，未记录解压后 EXE 哈希，所以不能证明二进制自 Phase 2A 起未变化；本阶段为 GUI 与 console EXE 建立当前本地 SHA-256 基线，见 `crash-isolation/README.md`。未联网补证书链，也未使用管理员权限。

验证日期：2026-07-16（Asia/Shanghai）

| 项目 | 结果 |
| --- | --- |
| Release | `4.7.1-stable`，非预发布 |
| 版本类型 | Windows x86_64 标准版 / GDScript，非 .NET |
| PE 架构 | `Machine=0x8664` / x86_64 |
| 官方发布页 | `https://github.com/godotengine/godot-builds/releases/tag/4.7.1-stable` |
| 下载 URL | `https://github.com/godotengine/godot-builds/releases/download/4.7.1-stable/Godot_v4.7.1-stable_win64.exe.zip` |
| ZIP 文件名 | `Godot_v4.7.1-stable_win64.exe.zip` |
| 下载大小 | `84,198,557` 字节 |
| 官方 SHA-256 | `c7a289051eaefb460b0106b60e9cd5bee0ef55fd102dcb2bed1eb356cf3d90a1` |
| 本地 SHA-256 | `c7a289051eaefb460b0106b60e9cd5bee0ef55fd102dcb2bed1eb356cf3d90a1` |
| Authenticode | `Valid` / `Signature verified.` |
| 签名者 | `CN=Prehensile Tales B.V., O=Prehensile Tales B.V., L=Uitgeest, S=Noord Holland, C=NL` |
| 签名时间 | `2026-07-14 21:39`（`certutil` 输出未包含时区） |
| 时间戳机构 | `CN=Certum Timestamp 2026, O=Asseco Data Systems S.A., C=PL` |
| 安装目录 | `E:\Workspace\tools\Godot\4.7.1` |
| 主程序 | `E:\Workspace\tools\Godot\4.7.1\Godot_v4.7.1-stable_win64.exe` |
| Console 程序 | `E:\Workspace\tools\Godot\4.7.1\Godot_v4.7.1-stable_win64_console.exe` |

使用 Godot 官方 `_sc_` 标记启用 self-contained 模式，编辑器数据、设置与缓存写入同目录的 `editor_data/`。未使用安装器、UAC、PATH、注册表、Windows 服务、计划任务、导出模板或 .NET 版本；下载 ZIP 已从临时目录清理，Godot 二进制不进入 Git。
