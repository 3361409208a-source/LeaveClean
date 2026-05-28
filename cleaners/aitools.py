"""AI编程工具与助手数据清理"""
import os
import shutil
import subprocess
from utils.scanner import check_path_exists, get_dir_size_fast, format_size, count_files_fast


class AIToolsCleaner:
    DISPLAY_NAME = "AI编程工具"

    def __init__(self):
        home = os.path.expanduser("~")
        local = os.environ.get("LOCALAPPDATA", "")
        roaming = os.environ.get("APPDATA", "")

        # AI工具: 名称 -> {描述, 数据路径列表, 详情说明}
        self.tools = {
            "Claude Code": {
                "desc": "Anthropic CLI编程助手",
                "paths": [
                    (os.path.join(home, ".claude"), "配置/项目记忆/对话历史/MCP配置"),
                    (os.path.join(home, ".claude.json"), "全局设置文件"),
                    (os.path.join(local, "claude-cli-nodejs"), "Node运行时缓存"),
                ],
            },
            "Cline (VS Code)": {
                "desc": "VS Code AI助手插件",
                "paths": [
                    (os.path.join(home, ".cline"), "对话历史/API密钥/配置"),
                ],
            },
            "GitHub Copilot": {
                "desc": "GitHub AI代码补全",
                "paths": [
                    (os.path.join(home, ".copilot"), "认证令牌/配置/缓存"),
                ],
            },
            "Codeium": {
                "desc": "AI代码补全工具",
                "paths": [
                    (os.path.join(home, ".codeium"), "API密钥/认证/语言服务器缓存"),
                ],
            },
            "OpenClaw": {
                "desc": "开源AI编程助手",
                "paths": [
                    (os.path.join(home, ".openclaw"), "配置/对话历史"),
                    (os.path.join(home, ".openclaw-dev"), "开发版数据"),
                ],
            },
            "OpenClaw Bot (clawdbot)": {
                "desc": "ClawdBot CLI工具",
                "paths": [
                    (os.path.join(home, ".clawdbot"), "配置/对话记录"),
                ],
            },
            "Codex (OpenAI)": {
                "desc": "OpenAI Codex CLI",
                "paths": [
                    (os.path.join(home, ".codex"), "配置/API密钥/对话历史"),
                    (os.path.join(home, ".codex_cursor"), "Cursor集成的Codex数据"),
                ],
            },
            "Google Gemini CLI": {
                "desc": "Google AI编程助手",
                "paths": [
                    (os.path.join(home, ".gemini"), "API密钥/配置/对话缓存"),
                ],
            },
            "Cursor": {
                "desc": "AI代码编辑器",
                "paths": [
                    (os.path.join(home, ".cursor"), "扩展/配置/AI对话历史"),
                    (os.path.join(home, ".cursor_free_data"), "免费版数据"),
                    (os.path.join(home, ".cursor_info"), "设备信息/许可"),
                    (os.path.join(roaming, "Cursor"), "应用数据/缓存/账号令牌"),
                ],
            },
            "Windsurf": {
                "desc": "Codeium出品AI编辑器",
                "paths": [
                    (os.path.join(home, ".windsurf"), "配置/扩展/AI对话"),
                    (os.path.join(roaming, "Windsurf"), "应用数据/账号/缓存"),
                    (os.path.join(roaming, "WindsurfTools"), "工具链数据"),
                ],
            },
            "Trae / Trae CN": {
                "desc": "字节跳动AI编辑器",
                "paths": [
                    (os.path.join(home, ".trae"), "配置/扩展"),
                    (os.path.join(home, ".trae-aicc"), "AI功能缓存"),
                    (os.path.join(home, ".trae-cn"), "CN版配置"),
                    (os.path.join(roaming, "Trae"), "应用数据"),
                    (os.path.join(roaming, "Trae CN"), "CN版应用数据"),
                    (os.path.join(roaming, "TRAE SOLO"), "独立版数据"),
                    (os.path.join(local, "Programs", "Trae"), "安装目录"),
                    (os.path.join(local, "Programs", "Trae CN"), "CN版安装目录"),
                ],
            },
            "Kiro (Amazon)": {
                "desc": "Amazon AI编辑器",
                "paths": [
                    (os.path.join(home, ".kiro"), "配置/扩展/AI对话"),
                    (os.path.join(roaming, "Kiro"), "应用数据/账号"),
                    (os.path.join(roaming, "kiro-account-manager"), "账号管理器"),
                    (os.path.join(local, "Programs", "kiro-account-manager"), "账号管理安装"),
                ],
            },
            "Junie (JetBrains AI)": {
                "desc": "JetBrains AI助手",
                "paths": [
                    (os.path.join(home, ".junie"), "配置/对话历史"),
                ],
            },
            "Augment": {
                "desc": "AI编程助手",
                "paths": [
                    (os.path.join(home, ".augment"), "配置/API密钥"),
                ],
            },
            "Fitten Code": {
                "desc": "AI代码补全",
                "paths": [
                    (os.path.join(home, ".fitten"), "配置/模型缓存"),
                ],
            },
            "通义灵码 (Lingma)": {
                "desc": "阿里AI编程助手",
                "paths": [
                    (os.path.join(home, ".lingma"), "配置/对话/缓存"),
                ],
            },
            "CodeBuddy": {
                "desc": "腾讯AI编程助手",
                "paths": [
                    (os.path.join(home, ".codebuddy"), "配置/对话历史"),
                    (os.path.join(local, "CodeBuddyExtension"), "扩展缓存"),
                ],
            },
            "CodeYu": {
                "desc": "AI编程工具",
                "paths": [
                    (os.path.join(home, ".codeyu"), "配置/数据"),
                    (os.path.join(home, ".codeyu-dev"), "开发版数据"),
                ],
            },
            "SecureCoder": {
                "desc": "安全编码AI助手",
                "paths": [
                    (os.path.join(home, ".securecoder"), "配置/分析缓存"),
                ],
            },
            "Antigravity IDE": {
                "desc": "反重力AI编辑器",
                "paths": [
                    (os.path.join(home, ".antigravity"), "配置"),
                    (os.path.join(home, ".antigravity-ide"), "IDE配置"),
                    (os.path.join(home, ".antigravitycli"), "CLI配置"),
                    (os.path.join(home, ".antigravity_tools"), "工具数据"),
                    (os.path.join(roaming, "Antigravity"), "应用数据"),
                    (os.path.join(roaming, "Antigravity IDE"), "IDE应用数据"),
                    (os.path.join(local, "antigravity"), "本地缓存"),
                    (os.path.join(local, "Programs", "Antigravity"), "安装目录"),
                    (os.path.join(local, "Programs", "Antigravity IDE"), "IDE安装目录"),
                ],
            },
            "Devin": {
                "desc": "AI软件工程师",
                "paths": [
                    (os.path.join(local, "devin"), "应用数据"),
                    (os.path.join(roaming, "devin"), "配置"),
                ],
            },
            "Cagent": {
                "desc": "AI Agent CLI",
                "paths": [
                    (os.path.join(home, ".cagent"), "配置/对话"),
                ],
            },
            "Ollama": {
                "desc": "本地大模型运行器",
                "paths": [
                    (os.path.join(home, ".ollama"), "模型文件/配置 (可能很大!)"),
                ],
            },
            "ChatBox AI": {
                "desc": "桌面AI对话客户端",
                "paths": [
                    (os.path.join(roaming, "xyz.chatboxapp.app"), "对话历史/API密钥/配置"),
                ],
            },
            "腾讯元宝": {
                "desc": "腾讯AI助手",
                "paths": [
                    (os.path.join(roaming, "com.tencent.yuanbao"), "对话/配置"),
                ],
            },
            "GStack": {
                "desc": "AI开发框架",
                "paths": [
                    (os.path.join(home, ".gstack"), "配置/缓存"),
                ],
            },
            "MCP Auth": {
                "desc": "MCP协议认证数据",
                "paths": [
                    (os.path.join(home, ".mcp-auth"), "服务器令牌/OAuth凭据"),
                ],
            },
            "Mem0": {
                "desc": "AI记忆层",
                "paths": [
                    (os.path.join(home, ".mem0"), "向量数据库/记忆数据"),
                ],
            },
            "ModelScope": {
                "desc": "魔搭模型缓存",
                "paths": [
                    (os.path.join(home, ".modelscope"), "模型下载缓存 (可能很大!)"),
                ],
            },
            "AI Completion": {
                "desc": "AI补全配置",
                "paths": [
                    (os.path.join(home, ".ai_completion"), "配置/缓存"),
                ],
            },
            "ZCode": {
                "desc": "AI编程工具",
                "paths": [
                    (os.path.join(home, ".zcode"), "配置"),
                ],
            },
        }

    def scan(self) -> list:
        results = []
        for name, info in self.tools.items():
            for path, detail in info["paths"]:
                if check_path_exists(path):
                    if os.path.isdir(path):
                        size = format_size(get_dir_size_fast(path))
                        fcount = count_files_fast(path)
                        desc = f"{name} - {detail} (~{fcount}文件)"
                    else:
                        try:
                            size = format_size(os.path.getsize(path))
                        except OSError:
                            size = "未知"
                        desc = f"{name} - {detail}"
                    results.append((desc, path, size, True))
        return results

    def clean(self, paths: list, logger) -> int:
        cleaned = 0
        for path in paths:
            try:
                if os.path.isfile(path):
                    os.remove(path)
                    logger.success(f"已删除: {path}")
                    cleaned += 1
                elif os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                    logger.success(f"已删除目录: {path}")
                    cleaned += 1
            except PermissionError:
                logger.error(f"权限不足: {path}")
            except Exception as e:
                logger.error(f"删除失败 {path}: {e}")
        return cleaned
