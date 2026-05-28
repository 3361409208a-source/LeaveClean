"""开发环境与运行时清理/卸载"""
import os
import shutil
import subprocess
import winreg
from utils.scanner import check_path_exists, get_dir_size_fast, format_size, count_files_fast


class DevEnvCleaner:
    DISPLAY_NAME = "开发环境"

    def __init__(self):
        home = os.path.expanduser("~")
        local = os.environ.get("LOCALAPPDATA", "")
        roaming = os.environ.get("APPDATA", "")
        programs = os.path.join(local, "Programs")

        self.environments = {
            # ===== Python =====
            "Python": {
                "paths": [
                    (os.path.join(programs, "Python"), "Python安装目录(所有版本)"),
                    (os.path.join(home, ".python_history"), "REPL交互历史"),
                    (os.path.join(roaming, "pip"), "pip配置与缓存"),
                    (os.path.join(local, "pip"), "pip本地缓存"),
                    (os.path.join(local, "pypa"), "PyPA工具缓存"),
                    (os.path.join(home, ".ipython"), "IPython配置/历史"),
                    (os.path.join(home, ".jupyter"), "Jupyter配置/密钥"),
                    (os.path.join(home, ".matplotlib"), "Matplotlib缓存"),
                    (os.path.join(roaming, "jupyter"), "Jupyter运行时数据"),
                    (os.path.join(home, ".cache", "uv"), "uv包管理器缓存"),
                    (os.path.join(local, "uv"), "uv本地数据"),
                    (os.path.join(roaming, "uv"), "uv配置"),
                ],
            },
            "Anaconda/Conda": {
                "paths": [
                    (os.path.join(local, "conda"), "Conda安装/环境数据"),
                    (os.path.join(roaming, "conda-anaconda-tos"), "Anaconda服务条款"),
                    (os.path.join(home, ".condarc"), "Conda配置文件"),
                ],
            },
            # ===== Node.js =====
            "Node.js": {
                "paths": [
                    (r"D:\Program Files", "Node.js安装目录(D盘)"),
                    (r"D:\nodejs", "Node.js全局模块(D盘)"),
                    (os.path.join(home, ".npmrc"), "npm配置(含registry/token)"),
                    (os.path.join(local, "npm-cache"), "npm缓存"),
                    (os.path.join(roaming, "npm"), "npm全局包"),
                    (os.path.join(home, ".node_repl_history"), "Node REPL历史"),
                    (os.path.join(home, ".nuxtrc"), "Nuxt配置"),
                    (os.path.join(home, ".expo"), "Expo(React Native)配置"),
                ],
            },
            "NVM (Node版本管理)": {
                "paths": [
                    (os.path.join(roaming, "nvm"), "NVM安装/所有Node版本"),
                ],
            },
            "PNPM": {
                "paths": [
                    (os.path.join(local, "pnpm"), "pnpm全局包/CLI"),
                    (os.path.join(local, "pnpm-cache"), "pnpm缓存(可能很大)"),
                    (os.path.join(local, "pnpm-state"), "pnpm状态"),
                ],
            },
            "Bun": {
                "paths": [
                    (os.path.join(home, ".bun"), "Bun运行时/缓存/全局包"),
                ],
            },
            "Yarn": {
                "paths": [
                    (os.path.join(local, "Yarn"), "Yarn缓存/全局包"),
                ],
            },
            # ===== Go =====
            "Go": {
                "paths": [
                    (r"C:\Program Files\Go", "Go安装目录"),
                    (os.path.join(home, "go"), "GOPATH(模块/二进制)"),
                    (os.path.join(local, "go-build"), "Go构建缓存"),
                    (os.path.join(local, "goimports"), "goimports缓存"),
                    (os.path.join(local, "gopls"), "gopls语言服务器缓存"),
                ],
            },
            # ===== Rust =====
            "Rust": {
                "paths": [
                    (os.path.join(home, ".cargo"), "Cargo包管理器/工具链/源码缓存"),
                    (os.path.join(home, ".rustup"), "Rustup工具链管理/所有版本"),
                ],
            },
            # ===== Java =====
            "Java/JDK": {
                "paths": [
                    (r"C:\Program Files\Java", "JDK安装目录"),
                    (os.path.join(home, ".jdks"), "JetBrains下载的JDK"),
                    (os.path.join(home, ".gradle"), "Gradle缓存/构建数据"),
                    (os.path.join(home, ".m2"), "Maven本地仓库"),
                ],
            },
            # ===== .NET =====
            ".NET": {
                "paths": [
                    (os.path.join(home, ".dotnet"), ".NET SDK/运行时/工具"),
                    (os.path.join(home, ".nuget"), "NuGet包缓存"),
                    (os.path.join(home, ".omnisharp"), "OmniSharp语言服务器"),
                    (os.path.join(home, ".templateengine"), ".NET模板缓存"),
                ],
            },
            # ===== 前端/移动端 =====
            "Android SDK": {
                "paths": [
                    (os.path.join(home, ".android"), "Android SDK/AVD/调试密钥"),
                ],
            },
            "Flutter/Dart": {
                "paths": [
                    (os.path.join(home, ".flutter"), "Flutter SDK配置"),
                    (os.path.join(home, ".dart"), "Dart SDK配置"),
                    (os.path.join(local, "flutter_webview_windows"), "Flutter WebView缓存"),
                ],
            },
            "HarmonyOS": {
                "paths": [
                    (os.path.join(home, ".hvigor"), "鸿蒙构建工具缓存"),
                    (os.path.join(home, ".ohos"), "鸿蒙SDK配置"),
                    (os.path.join(home, ".ohpm"), "鸿蒙包管理器"),
                ],
            },
            # ===== 编辑器/IDE =====
            "VS Code": {
                "paths": [
                    (os.path.join(home, ".vscode"), "扩展/配置"),
                    (os.path.join(home, ".vscode-oss"), "VSCodium数据"),
                    (os.path.join(home, ".vscode-oss-dev"), "OSS开发版"),
                    (os.path.join(home, ".vscode-shared"), "共享配置"),
                    (os.path.join(home, ".vsc-cache"), "VS Code缓存"),
                    (os.path.join(roaming, "Code"), "VS Code用户数据/设置/扩展状态"),
                    (os.path.join(local, "Programs", "Microsoft VS Code"), "安装目录"),
                ],
            },
            "JetBrains全家桶": {
                "paths": [
                    (os.path.join(roaming, "JetBrains"), "所有IDE配置/历史/缓存"),
                    (os.path.join(local, "JetBrains"), "所有IDE缓存/索引"),
                ],
            },
            # ===== Docker/容器 =====
            "Docker": {
                "paths": [
                    (os.path.join(home, ".docker"), "Docker配置/认证/镜像元数据"),
                    (os.path.join(roaming, "Docker"), "Docker Desktop数据"),
                    (os.path.join(roaming, "Docker Desktop"), "Docker Desktop配置"),
                    (os.path.join(local, "Docker"), "Docker本地缓存"),
                ],
            },
            # ===== 云平台 =====
            "AWS CLI": {
                "paths": [
                    (os.path.join(home, ".aws"), "AWS凭据/配置/SSO缓存"),
                ],
            },
            "Azure CLI": {
                "paths": [
                    (os.path.join(home, ".azure"), "Azure认证令牌/订阅配置"),
                ],
            },
            "Kubernetes": {
                "paths": [
                    (os.path.join(home, ".kube"), "kubeconfig/集群凭据"),
                ],
            },
            # ===== Git =====
            "Git": {
                "paths": [
                    (os.path.join(home, ".gitconfig"), "Git全局配置(用户名/邮箱/别名)"),
                    (os.path.join(home, ".git-credentials"), "Git明文密码存储!"),
                    (os.path.join(roaming, "TortoiseGit"), "TortoiseGit配置"),
                ],
            },
            # ===== SSH =====
            "SSH": {
                "paths": [
                    (os.path.join(home, ".ssh"), "SSH密钥对/known_hosts/配置"),
                ],
            },
            # ===== Shell =====
            "Shell历史": {
                "paths": [
                    (os.path.join(home, ".bash_history"), "Bash命令历史"),
                    (os.path.join(home, ".zshrc"), "Zsh配置"),
                    (os.path.join(home, ".lesshst"), "Less浏览历史"),
                    (os.path.join(home, ".viminfo"), "Vim编辑历史"),
                    (os.path.join(home, ".rediscli_history"), "Redis CLI历史"),
                    (os.path.join(roaming,
                        r"Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt"),
                        "PowerShell命令历史"),
                ],
            },
            # ===== 其他工具 =====
            "Electron缓存": {
                "paths": [
                    (os.path.join(home, ".electron-gyp"), "Electron编译缓存"),
                    (os.path.join(roaming, "Electron"), "Electron运行时缓存"),
                ],
            },
            "Playwright": {
                "paths": [
                    (os.path.join(local, "ms-playwright"), "Playwright浏览器(可能>1GB)"),
                    (os.path.join(local, "ms-playwright-go"), "Playwright Go版浏览器"),
                ],
            },
            "Prisma": {
                "paths": [
                    (os.path.join(local, "prisma-nodejs"), "Prisma引擎/模式缓存"),
                ],
            },
            "Scoop": {
                "paths": [
                    (os.path.join(home, "scoop"), "Scoop包管理器/所有安装的软件"),
                ],
            },
            "通用缓存目录": {
                "paths": [
                    (os.path.join(home, ".cache"), "各种工具的缓存总目录"),
                    (os.path.join(local, "Temp"), "Windows临时文件"),
                ],
            },
            "Outlook 邮件": {
                "paths": [
                    (os.path.join(local, r"Microsoft\Outlook"), "Outlook邮件本地缓存 (.ost)"),
                    (os.path.join(roaming, r"Microsoft\Outlook"), "Outlook个人签名与配置文件"),
                ],
            },
        }

    def scan(self) -> list:
        results = []
        for env_name, info in self.environments.items():
            for path, detail in info["paths"]:
                if check_path_exists(path):
                    if os.path.isdir(path):
                        size = format_size(get_dir_size_fast(path))
                        fcount = count_files_fast(path)
                        desc = f"{env_name} - {detail} (~{fcount}文件)"
                    else:
                        try:
                            size = format_size(os.path.getsize(path))
                        except OSError:
                            size = "未知"
                        desc = f"{env_name} - {detail}"

                    # 敏感项标记
                    if any(kw in detail for kw in ["密钥", "凭据", "token", "密码", "令牌", "认证"]):
                        desc = "⚠ " + desc

                    results.append((desc, path, size, True))

        # 动态扫描 OneDrive 路径
        onedrive_paths = []
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders", 0, winreg.KEY_READ)
            od_dir, _ = winreg.QueryValueEx(key, "OneDrive")
            winreg.CloseKey(key)
            if od_dir and check_path_exists(od_dir):
                onedrive_paths.append((od_dir, "OneDrive 本地同步目录(商业/个人数据)"))
        except Exception:
            pass
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\OneDrive", 0, winreg.KEY_READ)
            od_dir, _ = winreg.QueryValueEx(key, "UserFolder")
            winreg.CloseKey(key)
            if od_dir and check_path_exists(od_dir) and od_dir not in [p[0] for p in onedrive_paths]:
                onedrive_paths.append((od_dir, "OneDrive 本地同步目录"))
        except Exception:
            pass
            
        od_cache = os.path.join(local, "Microsoft", "OneDrive")
        if check_path_exists(od_cache):
            onedrive_paths.append((od_cache, "OneDrive 应用缓存与元数据"))
            
        for path, detail in onedrive_paths:
            size = format_size(get_dir_size_fast(path))
            fcount = count_files_fast(path)
            results.append((f"OneDrive - {detail} (~{fcount}文件)", path, size, True))

        # 扫描本地 Git 代码仓库
        git_repos = self._scan_git_repos()
        for name, repo_path, remote_url in git_repos:
            size = format_size(get_dir_size_fast(repo_path))
            fcount = count_files_fast(repo_path)
            desc = f"本地项目代码仓库 - ⚠ {name} ({remote_url}) (~{fcount}文件)"
            results.append((desc, repo_path, size, True))

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
                    if not os.path.exists(path):
                        logger.success(f"已删除目录: {path}")
                        cleaned += 1
                    else:
                        # 部分删除
                        logger.warning(f"部分删除(有文件被占用): {path}")
                        cleaned += 1
            except PermissionError:
                logger.error(f"权限不足: {path}（请先关闭相关程序）")
            except Exception as e:
                logger.error(f"删除失败 {path}: {e}")
        return cleaned

    def _scan_git_repos(self) -> list:
        repos = []
        home = os.path.expanduser("~")
        
        candidates = [
            os.path.join(home, "Desktop"),
            os.path.join(home, "Documents"),
            os.path.join(home, "Downloads"),
            os.path.join(home, "source", "repos"),
            os.path.join(home, "workspace"),
            os.path.join(home, "projects"),
            os.path.join(home, "code"),
        ]
        for drive in ["C:\\", "D:\\", "E:\\", "F:\\"]:
            if os.path.exists(drive):
                candidates.extend([
                    os.path.join(drive, "workspace"),
                    os.path.join(drive, "projects"),
                    os.path.join(drive, "code"),
                    os.path.join(drive, "git"),
                    os.path.join(drive, "github"),
                    os.path.join(drive, "gitlab"),
                ])
                
        search_dirs = []
        seen = set()
        for d in candidates:
            d_norm = os.path.normpath(d).lower()
            if d_norm not in seen and os.path.isdir(d):
                seen.add(d_norm)
                search_dirs.append(d)
                
        for base in search_dirs:
            try:
                for entry in os.scandir(base):
                    if not entry.is_dir(follow_symlinks=False):
                        continue
                    git_dir = os.path.join(entry.path, ".git")
                    if os.path.isdir(git_dir):
                        url = self._get_git_remote(entry.path)
                        repos.append((entry.name, entry.path, url))
                        continue
                    
                    try:
                        for sub_entry in os.scandir(entry.path):
                            if sub_entry.is_dir(follow_symlinks=False):
                                sub_git = os.path.join(sub_entry.path, ".git")
                                if os.path.isdir(sub_git):
                                    url = self._get_git_remote(sub_entry.path)
                                    repos.append((f"{entry.name}/{sub_entry.name}", sub_entry.path, url))
                    except Exception:
                        pass
            except Exception:
                pass
        return repos

    def _get_git_remote(self, repo_path: str) -> str:
        config_path = os.path.join(repo_path, ".git", "config")
        if not os.path.isfile(config_path):
            return "Local Repository"
        try:
            url = ""
            with open(config_path, "r", encoding="utf-8", errors="ignore") as f:
                in_remote = False
                for line in f:
                    line = line.strip()
                    if line.startswith('[remote "origin"]'):
                        in_remote = True
                    elif line.startswith("[") and not line.startswith('[remote'):
                        in_remote = False
                    elif in_remote and line.startswith("url ="):
                        url = line.split("=", 1)[1].strip()
                        break
            return url if url else "Local Repository"
        except Exception:
            return "Local Repository"
