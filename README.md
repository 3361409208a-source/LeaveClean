# LeaveClean - 离职数据清理助手

> 一款帮助离职员工安全清理工作电脑上个人隐私数据的桌面工具。先扫描、后预览、再清理，防止误删。

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 功能概览

### 7 大清理模块

| 模块 | 清理内容 |
|------|---------|
| **浏览器数据** | Chrome / Edge / Firefox / QQ浏览器 / 搜狗 / 360 — 账号同步、Cookie、密码、历史、缓存、扩展、书签等 |
| **聊天与通讯** | 微信(新版+经典版) / QQ(NT版) / 企业微信 / 钉钉 / 飞书 / 腾讯会议 / Telegram / Foxmail — 图片、视频、文件、语音、聊天记录分类展示 |
| **个人文件** | 桌面 / 下载 / 文档 / 图片 / 视频 / 音乐 / 回收站 / 临时文件 / 最近文件记录 |
| **凭据与隐私** | Windows凭据 / WiFi密码 / 剪贴板 / 搜索历史 / 运行历史 / 远程桌面记录 / DNS缓存 / Git / SSH密钥 / Shell历史 |
| **AI 编程工具** | Claude Code / Cursor / Windsurf / Trae / Kiro / Copilot / Codeium / OpenClaw / Codex / Gemini CLI / Cline / Ollama 等 30+ 工具 |
| **开发环境** | Python / Node.js(NVM/PNPM/Bun) / Go / Rust / Java / .NET / Docker / Flutter / HarmonyOS / VS Code / JetBrains / AWS / Azure / K8s |
| **个人软件管理** | 50+ 常见个人软件 — 卸载软件 + 清除数据残留 + 注册表清理 + 快捷方式清理 |

### 界面特性

- **统一树形视图** — 勾选、详情、路径、大小、操作类型在同一个表格中展示
- **分类侧边栏** — 左侧 7 大分类导航，点击过滤，切换时保留勾选状态
- **数据详情预览** — 点击任一行，实时预览文件内容 / 目录结构（敏感信息自动打码）
- **单项 + 批量操作** — 每行可独立清除/卸载，也可勾选后一键批量清理
- **右键菜单** — 查看详情 / 打开目录 / 复制路径 / 清除 / 卸载
- **实时统计** — 发现项目数、预估大小、已清理数、扫描用时、模块进度
- **操作日志** — 彩色日志（成功/失败/警告），支持导出
- **二次确认** — 清理前双重确认弹窗，防止误操作
- **并行扫描** — 7 个模块线程池并行扫描，秒级完成

## 快速开始

### 运行要求

- Windows 10 / 11
- Python 3.8+（仅使用标准库 tkinter，无需 pip install）

### 启动

```bash
cd LeaveClean
python main.py
```

### 使用流程

1. 点击 **「扫描检测」** — 自动检测所有可清理数据
2. 左侧分类导航 **筛选** 感兴趣的类别
3. 点击行查看 **数据详情**，确认是什么数据
4. 点击 **☐** 勾选要清理的项目（或点分类行全选）
5. 点击 **「一键清理」** — 二次确认后执行

## 项目结构

```
LeaveClean/
├── main.py                # GUI 主界面 (tkinter)
├── cleaners/
│   ├── browser.py         # 浏览器数据清理
│   ├── chat.py            # 聊天通讯清理
│   ├── files.py           # 个人文件清理
│   ├── credentials.py     # 凭据隐私清理
│   ├── aitools.py         # AI 编程工具清理
│   ├── devenv.py          # 开发环境清理
│   └── software.py        # 个人软件管理
├── utils/
│   ├── scanner.py         # 文件扫描与大小统计
│   └── logger.py          # 操作日志记录
└── logs/                  # 自动生成的日志目录
```

## 安全说明

- **只清理个人数据**，不触碰系统文件和公司工作文件
- **先扫描后清理** — 所有操作可预览确认
- **敏感信息打码** — 预览文件内容时，password / token / key 等自动显示为 `********`
- **操作日志** — 每次清理自动记录到 `logs/` 目录
- **二次确认** — 批量清理需两次确认，防止误删

## 注意事项

- 清理浏览器数据前请先 **关闭浏览器**
- 清理聊天数据前请先 **退出微信/QQ/钉钉等**
- 卸载软件时可能弹出卸载向导，请配合完成
- **数据删除后无法恢复**，请确认后再操作

---

# LeaveClean - Resignation Data Cleanup Assistant

> A desktop tool to help employees securely clean personal data from work computers before leaving. Scan first, preview, then clean -- preventing accidental deletion.

## Features

### 7 Cleanup Modules

| Module | What it cleans |
|--------|---------------|
| **Browser Data** | Chrome / Edge / Firefox / QQ Browser / Sogou / 360 -- accounts, sync data, cookies, passwords, history, cache, extensions, bookmarks |
| **Chat & Communication** | WeChat (new + classic) / QQ (NT) / WeCom / DingTalk / Feishu / Tencent Meeting / Telegram / Foxmail -- images, videos, files, voice messages, chat history |
| **Personal Files** | Desktop / Downloads / Documents / Pictures / Videos / Music / Recycle Bin / Temp files / Recent files |
| **Credentials & Privacy** | Windows Credentials / WiFi passwords / Clipboard / Search history / Run history / RDP history / DNS cache / Git / SSH keys / Shell history |
| **AI Coding Tools** | Claude Code / Cursor / Windsurf / Trae / Kiro / Copilot / Codeium / OpenClaw / Codex / Gemini CLI / Cline / Ollama and 30+ more |
| **Dev Environments** | Python / Node.js (NVM/PNPM/Bun) / Go / Rust / Java / .NET / Docker / Flutter / HarmonyOS / VS Code / JetBrains / AWS / Azure / K8s |
| **Software Management** | 50+ personal apps -- uninstall + remove data residuals + registry cleanup + shortcut cleanup |

### UI Features

- **Unified tree view** -- checkbox, details, path, size, action type in one table
- **Category sidebar** -- 7 categories for quick filtering, checked state preserved across switches
- **Data preview** -- click any row to preview file content / directory structure (sensitive info auto-masked)
- **Single + batch operations** -- clean/uninstall per item, or batch clean all checked items
- **Context menu** -- right-click for details / open folder / copy path / clean / uninstall
- **Real-time stats** -- items found, estimated size, cleaned count, scan time, module progress
- **Colored log** -- success / error / warning with export support
- **Double confirmation** -- two confirmation dialogs before batch cleanup
- **Parallel scanning** -- 7 modules scanned concurrently via thread pool

## Quick Start

### Requirements

- Windows 10 / 11
- Python 3.8+ (standard library only, no pip install needed)

### Run

```bash
cd LeaveClean
python main.py
```

### Usage

1. Click **"Scan"** -- auto-detect all cleanable data
2. Use the **category sidebar** to filter
3. Click any row to **preview data details**
4. Click **☐** to check items (or click category row to select all)
5. Click **"Clean All"** -- double confirmation, then execute

## Project Structure

```
LeaveClean/
├── main.py                # GUI entry (tkinter)
├── cleaners/
│   ├── browser.py         # Browser data cleanup
│   ├── chat.py            # Chat app cleanup
│   ├── files.py           # Personal files cleanup
│   ├── credentials.py     # Credentials & privacy cleanup
│   ├── aitools.py         # AI coding tools cleanup
│   ├── devenv.py          # Dev environment cleanup
│   └── software.py        # Software management
├── utils/
│   ├── scanner.py         # File scanner & size calculator
│   └── logger.py          # Operation logger
└── logs/                  # Auto-generated log directory
```

## Safety

- **Only cleans personal data** -- does not touch system files or company work files
- **Scan before clean** -- all operations can be previewed
- **Sensitive info masked** -- passwords, tokens, keys shown as `********` in preview
- **Operation log** -- every cleanup is logged to `logs/`
- **Double confirmation** -- batch cleanup requires two confirmations

## License

MIT
