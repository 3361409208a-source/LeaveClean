// ===== i18n Translations =====
const translations = {
  zh: {
    'nav.download': '下载',
    'hero.badge': 'v1.0 · 开源免费',
    'hero.title': '离职前，一键清理个人隐私数据',
    'hero.subtitle': '9大模块 · 30+ AI工具 · 零依赖 · 安全可控',
    'hero.cta1': '下载 EXE',
    'hero.cta2': '了解更多',
    'hero.trust': 'Python 标准库 · MIT 开源 · 无需安装依赖',
    'stats.modules': '清理模块',
    'stats.tools': 'AI 工具',
    'stats.apps': '软件支持',
    'stats.deps': '外部依赖',
    'features.title': '全面覆盖，一个不漏',
    'features.subtitle': '9 大清理模块，覆盖工作电脑上所有个人数据痕迹',
    'features.browser.title': '浏览器数据',
    'features.browser.desc': 'Chrome、Edge、Firefox 等 6 大浏览器的账号、密码、历史、Cookie',
    'features.browser.tag': '6 浏览器',
    'features.chat.title': '聊天通讯',
    'features.chat.desc': '微信、QQ、企业微信、钉钉、飞书、Telegram 等聊天记录与文件',
    'features.chat.tag': '8 通讯工具',
    'features.files.title': '个人文件',
    'features.files.desc': '桌面、下载、文档、图片、视频、回收站、临时文件',
    'features.files.tag': '7 目录',
    'features.creds.title': '凭证与隐私',
    'features.creds.desc': 'Windows 凭证、WiFi 密码、剪贴板、SSH 密钥、Git 配置',
    'features.creds.tag': '10+ 项',
    'features.ai.title': 'AI 编程工具',
    'features.ai.desc': 'Claude Code、Cursor、Windsurf、Copilot、Ollama 等 30+ 工具',
    'features.ai.tag': '30+ 工具',
    'features.dev.title': '开发环境',
    'features.dev.desc': 'Python、Node.js、Go、Rust、Docker、VS Code、JetBrains',
    'features.dev.tag': '15+ 环境',
    'features.software.title': '软件管理',
    'features.software.desc': '50+ 个人软件的卸载、残留数据清理、注册表清理',
    'features.software.tag': '50+ 软件',
    'features.uninstall.title': '软件卸载',
    'features.uninstall.desc': '调用系统卸载程序，彻底移除个人安装的应用',
    'features.uninstall.tag': '完整卸载',
    'features.self.title': '自我清理',
    'features.self.desc': '清理完成后，工具自身也不留痕迹',
    'features.self.tag': '无痕退出',
    'tools.title': '30+ AI 编程工具，一键清理',
    'tools.subtitle': '从 Claude Code 到 Cursor，从 Copilot 到 Ollama，全面覆盖主流 AI 开发工具',
    'steps.title': '安全四步，放心清理',
    'steps.subtitle': '先扫描、再预览、双确认、后清理，每一步都在你的掌控之中',
    'steps.scan.title': '扫描检测',
    'steps.scan.desc': '并行扫描 9 大模块，秒级发现所有可清理数据',
    'steps.preview.title': '预览详情',
    'steps.preview.desc': '查看每项数据详情，敏感信息自动打码保护',
    'steps.confirm.title': '双重确认',
    'steps.confirm.desc': '勾选需要清理的项目，弹窗二次确认防止误删',
    'steps.clean.title': '执行清理',
    'steps.clean.desc': '并行清理，实时显示进度，操作日志完整记录',
    'safety.title': '安全至上',
    'safety.subtitle': '每一个设计决策都以数据安全为第一优先级',
    'safety.item1': '只清理个人数据，不触碰系统文件',
    'safety.item2': '先扫描后清理，所有操作可预览',
    'safety.item3': '敏感信息自动打码显示',
    'safety.item4': '操作日志完整记录，可导出审计',
    'safety.item5': '双重确认弹窗，防止误操作',
    'safety.item6': '开源代码，完全透明可审计',
    'tech.title': '技术亮点',
    'tech.zero.title': '零依赖',
    'tech.zero.desc': '纯 Python 标准库，无需 pip install，开箱即用',
    'tech.fast.title': '并行扫描',
    'tech.fast.desc': '线程池并行扫描 9 大模块，秒级完成全盘检测',
    'tech.open.title': '开源透明',
    'tech.open.desc': 'MIT 协议，代码完全公开，欢迎审计与贡献',
    'cta.title': '准备离职？先清理数据',
    'cta.subtitle': '一行命令启动，无需安装任何依赖',
    'cta.download': '下载 EXE',
    'cta.source': '查看源码',
    'cta.note': 'Windows 10/11 · Python 3.8+',
    'footer.issues': '问题反馈',
    'footer.docs': '文档'
  },
  en: {
    'nav.download': 'Download',
    'hero.badge': 'v1.0 · Open Source & Free',
    'hero.title': 'Clean your personal data before you leave',
    'hero.subtitle': '9 Modules · 30+ AI Tools · Zero Dependencies · Safety First',
    'hero.cta1': 'Download EXE',
    'hero.cta2': 'Learn More',
    'hero.trust': 'Python stdlib only · MIT License · No pip install needed',
    'stats.modules': 'Cleanup Modules',
    'stats.tools': 'AI Tools',
    'stats.apps': 'Apps Supported',
    'stats.deps': 'Dependencies',
    'features.title': 'Complete Coverage, Nothing Left Behind',
    'features.subtitle': '9 cleanup modules covering every trace of personal data on your work computer',
    'features.browser.title': 'Browser Data',
    'features.browser.desc': 'Chrome, Edge, Firefox and more - accounts, passwords, history, cookies',
    'features.browser.tag': '6 Browsers',
    'features.chat.title': 'Chat & Messaging',
    'features.chat.desc': 'WeChat, QQ, WeCom, DingTalk, Feishu, Telegram - messages and files',
    'features.chat.tag': '8 Chat Apps',
    'features.files.title': 'Personal Files',
    'features.files.desc': 'Desktop, Downloads, Documents, Pictures, Videos, Recycle Bin, Temp files',
    'features.files.tag': '7 Directories',
    'features.creds.title': 'Credentials & Privacy',
    'features.creds.desc': 'Windows credentials, WiFi passwords, clipboard, SSH keys, Git config',
    'features.creds.tag': '10+ Items',
    'features.ai.title': 'AI Coding Tools',
    'features.ai.desc': 'Claude Code, Cursor, Windsurf, Copilot, Ollama and 30+ more tools',
    'features.ai.tag': '30+ Tools',
    'features.dev.title': 'Dev Environments',
    'features.dev.desc': 'Python, Node.js, Go, Rust, Docker, VS Code, JetBrains',
    'features.dev.tag': '15+ Envs',
    'features.software.title': 'Software Management',
    'features.software.desc': '50+ personal apps - uninstall, residual data cleanup, registry cleanup',
    'features.software.tag': '50+ Apps',
    'features.uninstall.title': 'Software Uninstall',
    'features.uninstall.desc': 'Invoke system uninstallers to completely remove personal applications',
    'features.uninstall.tag': 'Full Uninstall',
    'features.self.title': 'Self-Clean',
    'features.self.desc': 'After cleanup, the tool removes its own traces too',
    'features.self.tag': 'No Trace',
    'tools.title': '30+ AI Coding Tools, One Click Clean',
    'tools.subtitle': 'From Claude Code to Cursor, from Copilot to Ollama - comprehensive coverage of mainstream AI dev tools',
    'steps.title': '4 Safe Steps to Clean',
    'steps.subtitle': 'Scan, preview, confirm, clean - every step under your control',
    'steps.scan.title': 'Scan',
    'steps.scan.desc': 'Parallel scan across 9 modules, discover all cleanable data in seconds',
    'steps.preview.title': 'Preview',
    'steps.preview.desc': 'View details of each item, sensitive info auto-masked',
    'steps.confirm.title': 'Confirm',
    'steps.confirm.desc': 'Select items to clean, double confirmation prevents mistakes',
    'steps.clean.title': 'Clean',
    'steps.clean.desc': 'Parallel cleanup with real-time progress and complete operation logs',
    'safety.title': 'Safety First',
    'safety.subtitle': 'Every design decision prioritizes data safety above all else',
    'safety.item1': 'Only cleans personal data, never touches system files',
    'safety.item2': 'Scan before clean, all operations previewable',
    'safety.item3': 'Sensitive information auto-masked in previews',
    'safety.item4': 'Complete operation logging, exportable for audit',
    'safety.item5': 'Double confirmation dialogs prevent accidental deletion',
    'safety.item6': 'Open source code, fully transparent and auditable',
    'tech.title': 'Technical Highlights',
    'tech.zero.title': 'Zero Dependencies',
    'tech.zero.desc': 'Pure Python standard library, no pip install needed, works out of the box',
    'tech.fast.title': 'Parallel Scanning',
    'tech.fast.desc': 'Thread pool scans all 9 modules in parallel, completes in seconds',
    'tech.open.title': 'Open Source',
    'tech.open.desc': 'MIT License, fully open code, contributions welcome',
    'cta.title': 'Leaving your job? Clean your data first',
    'cta.subtitle': 'One command to start, no dependencies to install',
    'cta.download': 'Download EXE',
    'cta.source': 'View Source',
    'cta.note': 'Windows 10/11 · Python 3.8+',
    'footer.issues': 'Issues',
    'footer.docs': 'Docs'
  }
};

// ===== Language Toggle =====
let currentLang = localStorage.getItem('lang') || 'zh';

function setLanguage(lang) {
  currentLang = lang;
  localStorage.setItem('lang', lang);
  document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en';

  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (translations[lang][key]) {
      el.textContent = translations[lang][key];
    }
  });

  const toggle = document.getElementById('langToggle');
  toggle.textContent = lang === 'zh' ? 'EN' : '中文';
}

document.getElementById('langToggle').addEventListener('click', () => {
  setLanguage(currentLang === 'zh' ? 'en' : 'zh');
});

// Init language
setLanguage(currentLang);

// ===== Navbar Scroll Effect =====
const navbar = document.getElementById('navbar');
let lastScroll = 0;

window.addEventListener('scroll', () => {
  const scrollY = window.scrollY;
  if (scrollY > 50) {
    navbar.classList.add('scrolled');
  } else {
    navbar.classList.remove('scrolled');
  }
  lastScroll = scrollY;
}, { passive: true });

// ===== Scroll Animations =====
const animateObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      animateObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

document.querySelectorAll('[data-animate], [data-animate-stagger]').forEach(el => {
  animateObserver.observe(el);
});

// ===== Number Counter Animation =====
const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const counters = entry.target.querySelectorAll('[data-count]');
      counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-count'));
        const suffix = counter.getAttribute('data-suffix') || '';
        if (target === 0) {
          counter.textContent = '0' + suffix;
          return;
        }
        let current = 0;
        const duration = 1500;
        const step = target / (duration / 16);
        const animate = () => {
          current += step;
          if (current >= target) {
            counter.textContent = target + suffix;
          } else {
            counter.textContent = Math.floor(current) + suffix;
            requestAnimationFrame(animate);
          }
        };
        requestAnimationFrame(animate);
      });
      counterObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.3 });

const statsSection = document.querySelector('.stats');
if (statsSection) {
  counterObserver.observe(statsSection);
}

// ===== Smooth Scroll for Anchor Links =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', (e) => {
    const target = document.querySelector(anchor.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});
