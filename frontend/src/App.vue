<template>
  <div class="h-screen w-screen flex flex-col bg-slate-50 text-slate-700 select-none overflow-hidden font-sans">
    
    <!-- 1. 顶部 Header -->
    <header class="h-12 bg-blue-600 flex items-center justify-between px-4 text-white shadow-md z-10">
      <div class="flex items-center space-x-2">
        <el-icon class="text-xl animate-pulse"><Cpu /></el-icon>
        <span class="text-base font-bold tracking-wide">离职数据清理助手 v4.0 (Web GUI)</span>
      </div>
      <div class="flex items-center space-x-4">
        <span class="text-xs bg-blue-500 bg-opacity-50 px-2.5 py-1 rounded-full text-blue-100 font-mono">
          {{ currentTime }}
        </span>
      </div>
    </header>

    <!-- 2. 统计卡片与进度条 -->
    <div class="bg-white border-b border-slate-200 p-3 shadow-sm flex flex-col space-y-2">
      <!-- 卡片网格 -->
      <div class="grid grid-cols-5 gap-3">
        <div v-for="card in statCards" :key="card.key" class="bg-slate-50 border border-slate-100 rounded-lg p-2.5 flex items-center justify-between transition hover:shadow-sm">
          <div class="flex items-center space-x-2.5">
            <div class="p-2 rounded-lg" :class="card.bgClass">
              <el-icon :class="card.textClass" class="text-lg"><component :is="card.icon" /></el-icon>
            </div>
            <div>
              <div class="text-xs text-slate-400 font-medium">{{ card.title }}</div>
              <div class="text-lg font-bold" :class="card.textClass">{{ card.value }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 进度条 -->
      <div class="flex items-center space-x-3 pt-1">
        <div class="flex-1">
          <el-progress 
            :percentage="progress" 
            :status="progress === 100 ? 'success' : undefined" 
            :stroke-width="8"
            :show-text="false"
          />
        </div>
        <span class="text-xs text-slate-500 font-bold w-20 text-right">{{ progressText }}</span>
      </div>
    </div>

    <!-- 3. 主操作区 -->
    <div class="flex-1 flex overflow-hidden">
      <!-- 3.1 左侧导航栏 -->
      <aside class="w-56 bg-white border-r border-slate-200 flex flex-col p-2 space-y-1">
        <div class="text-xs font-bold text-slate-400 px-3 py-1.5 uppercase tracking-wider">视图分类</div>
        <button 
          v-for="(cat, key) in categories" 
          :key="key"
          @click="selectCategory(key)"
          class="w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition duration-200 text-left group"
          :class="currentCategory === key ? 'bg-blue-50 text-blue-600' : 'text-slate-600 hover:bg-slate-50'"
        >
          <div class="flex items-center space-x-2.5">
            <el-icon class="text-base" :class="currentCategory === key ? 'text-blue-600' : 'text-slate-400 group-hover:text-slate-600'">
              <component :is="cat.icon" />
            </el-icon>
            <span>{{ cat.name }}</span>
          </div>
          <span 
            v-if="cat.count > 0"
            class="text-xs px-2 py-0.5 rounded-full font-bold"
            :class="currentCategory === key ? 'bg-blue-200 text-blue-700' : 'bg-slate-100 text-slate-500'"
          >
            {{ cat.count }}
          </span>
        </button>
      </aside>

      <!-- 3.2 中间表格区域 -->
      <main class="flex-1 flex flex-col bg-slate-50 overflow-hidden p-3 space-y-3">
        <!-- 按钮工具栏 -->
        <div class="flex items-center justify-between bg-white p-2 border border-slate-200 rounded-lg shadow-sm">
          <div class="flex items-center space-x-2">
            <el-checkbox 
              v-model="isAllSelected" 
              @change="toggleSelectAll" 
              :indeterminate="isIndeterminate"
              label="全选" 
              border
              size="small"
            />
            <el-button 
              type="danger" 
              icon="Delete" 
              size="small" 
              :disabled="selectedPaths.length === 0"
              @click="handleBatchClean"
            >
              清除选中 ({{ selectedPaths.length }})
            </el-button>
          </div>
          <div class="flex items-center space-x-2">
            <el-button 
              type="primary" 
              icon="Search" 
              size="small" 
              :loading="isScanning"
              @click="startScan"
            >
              {{ isScanning ? '正在扫描...' : '开始扫描' }}
            </el-button>
          </div>
        </div>

        <!-- 数据表格 -->
        <div class="flex-1 bg-white border border-slate-200 rounded-lg overflow-hidden shadow-sm relative">
          <el-table 
            v-if="filteredItems.length > 0"
            :data="filteredItems" 
            height="100%" 
            style="width: 100%"
            size="small"
            @row-click="handleRowClick"
            highlight-current-row
          >
            <!-- 勾选列 -->
            <el-table-column width="45" align="center">
              <template #default="scope">
                <el-checkbox 
                  v-model="scope.row.checked" 
                  @change="toggleItem(scope.row)"
                  @click.stop
                />
              </template>
            </el-table-column>

            <!-- 描述/名称列 -->
            <el-table-column label="项目" min-width="240">
              <template #default="scope">
                <div class="flex items-center space-x-1.5">
                  <span v-if="scope.row.isWarning" class="text-red-500 font-bold text-xs bg-red-50 px-1.5 py-0.5 rounded">⚠</span>
                  <span :class="{ 'font-medium text-slate-800': true, 'text-red-600': scope.row.isWarning }">
                    {{ scope.row.desc }}
                  </span>
                </div>
              </template>
            </el-table-column>

            <!-- 路径列 -->
            <el-table-column label="路径" min-width="260">
              <template #default="scope">
                <span class="font-mono text-xs text-slate-400 block truncate" :title="scope.row.displayPath">
                  {{ scope.row.displayPath }}
                </span>
              </template>
            </el-table-column>

            <!-- 大小列 -->
            <el-table-column label="大小" width="95" align="center">
              <template #default="scope">
                <span class="font-semibold text-slate-600 text-xs">{{ scope.row.size }}</span>
              </template>
            </el-table-column>

            <!-- 状态列 -->
            <el-table-column label="状态" width="80" align="center">
              <template #default="scope">
                <el-tag :type="getStatusTagType(scope.row.status)" size="small" effect="plain">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>

            <!-- 操作类型列 -->
            <el-table-column label="类型" width="85" align="center">
              <template #default="scope">
                <el-tag :type="getOpTagType(scope.row.optype)" size="small" effect="light">
                  {{ scope.row.optype }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>

          <!-- 空数据状态 -->
          <div v-else class="h-full flex flex-col items-center justify-center text-slate-400 space-y-3">
            <el-empty :description="isScanning ? '正在扫描计算机，请稍候...' : '暂无扫描结果，请点击“开始扫描”按钮。'" />
          </div>
        </div>
      </main>

      <!-- 3.3 右侧侧边栏 (日志 + 预览) -->
      <aside class="w-96 bg-white border-l border-slate-200 flex flex-col overflow-hidden">
        <!-- 详情面板 -->
        <div class="h-1/2 border-b border-slate-200 flex flex-col overflow-hidden">
          <div class="h-9 bg-slate-50 border-b border-slate-200 flex items-center justify-between px-3 text-xs font-bold text-slate-500 uppercase tracking-wide">
            <span>📁 数据详情预览</span>
            <div class="space-x-1.5" v-if="selectedRow">
              <el-button type="primary" link size="small" icon="FolderOpened" @click="openSelectedPath">打开目录</el-button>
              <el-button type="primary" link size="small" icon="DocumentCopy" @click="copySelectedPath">复制路径</el-button>
            </div>
          </div>
          
          <div class="flex-1 p-3 overflow-y-auto bg-slate-50 font-mono text-xs text-slate-600">
            <div v-if="selectedRow">
              <div class="font-bold text-sm text-blue-600 mb-2 border-b border-blue-100 pb-1">{{ selectedRow.desc }}</div>
              <div class="grid grid-cols-4 gap-y-1 gap-x-2 mb-3">
                <div class="text-slate-400 font-medium">路径:</div>
                <div class="col-span-3 text-slate-700 break-all select-text">{{ selectedRow.realPath }}</div>
                <div class="text-slate-400 font-medium">类型:</div>
                <div class="col-span-3 text-slate-700">{{ selectedRow.optype }}</div>
                <div class="text-slate-400 font-medium">大小:</div>
                <div class="col-span-3 text-slate-700 font-semibold">{{ selectedRow.size }}</div>
              </div>

              <!-- 智能预览文本 -->
              <div v-if="detailLoading" class="flex justify-center py-4">
                <el-icon class="is-loading text-xl text-blue-500"><Loading /></el-icon>
              </div>
              <div v-else-if="detailContent">
                <div class="text-slate-400 font-bold mb-1 border-t border-slate-200 pt-2">内部详情:</div>
                <pre class="bg-white border border-slate-200 rounded p-2 overflow-x-auto text-[10px] leading-relaxed max-h-48 whitespace-pre-wrap select-text">{{ detailContent }}</pre>
              </div>
            </div>
            <div v-else class="h-full flex items-center justify-center text-slate-400 italic">
              点击左侧表格行查看详细数据预览
            </div>
          </div>
        </div>

        <!-- 终端日志面板 -->
        <div class="h-1/2 flex flex-col overflow-hidden bg-slate-900">
          <div class="h-9 border-b border-slate-800 flex items-center justify-between px-3 text-xs font-bold text-slate-400 uppercase tracking-wide">
            <div class="flex items-center space-x-1.5">
              <span class="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse"></span>
              <span>控制台操作日志</span>
            </div>
            <el-button type="info" link size="small" @click="clearLogs">清空</el-button>
          </div>
          
          <div ref="logContainer" class="flex-1 p-3 overflow-y-auto font-mono text-[10px] leading-relaxed space-y-1 text-slate-300 select-text">
            <div v-for="(log, idx) in logs" :key="idx" :class="getLogClass(log.type)">
              <span class="text-slate-500 mr-1.5">[{{ log.time }}]</span>
              <span>{{ log.msg }}</span>
            </div>
            <div v-if="logs.length === 0" class="text-slate-500 italic text-center pt-8">
              暂无操作日志记录
            </div>
          </div>
        </div>
      </aside>
    </div>

    <!-- 4. 手动审核防误删警告 Modal -->
    <el-dialog
      v-model="warningVisible"
      title="⚠️ 安全保护提示"
      width="450px"
      align-center
    >
      <div class="flex flex-col items-center text-center space-y-3 p-2">
        <el-icon class="text-red-500 text-5xl animate-bounce"><WarningFilled /></el-icon>
        <h3 class="font-bold text-base text-slate-800">该目录包含您的核心工作文件！</h3>
        <p class="text-xs text-slate-500 leading-relaxed">
          为了防止误抹除您的重要个人文件（如<b>个人照片、简历、工作交接报告、合同</b>等），此目录在清理助手中已被设置为<b>只读保护</b>。
        </p>
        <div class="bg-red-50 border border-red-100 rounded-lg p-3 w-full text-left text-xs text-red-700 font-mono break-all">
          目录路径：<br>
          <span class="font-bold select-text">{{ protectedPath }}</span>
        </div>
        <p class="text-xs font-bold text-blue-600">
          建议方案：请先手动备份重要资料，核对无误后再进行手动清空。
        </p>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="warningVisible = false">我知道了</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// --- 状态变量 ---
const currentCategory = ref('all')
const items = ref([])
const progress = ref(0)
const progressText = ref('就绪')
const isScanning = ref(false)
const selectedRow = ref(null)
const detailContent = ref('')
const detailLoading = ref(false)
const logs = ref([])
const currentTime = ref('')
const logContainer = ref(null)

// 保护提示
const warningVisible = ref(false)
const protectedPath = ref('')

// 时钟更新
let clockTimer = null
const updateClock = () => {
  const d = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  currentTime.value = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

// 分类目录列表
const categories = ref({
  all: { name: '全部', icon: 'Memo', count: 0 },
  uninstall: { name: '软件卸载', icon: 'Delete', count: 0 },
  browser: { name: '浏览器数据', icon: 'ChromeFilled', count: 0 },
  chat: { name: '聊天与通讯', icon: 'ChatLineRound', count: 0 },
  credentials: { name: '凭据与隐私', icon: 'Lock', count: 0 },
  devenv: { name: '开发环境', icon: 'Tools', count: 0 },
  aitools: { name: 'AI编程工具', icon: 'Connection', count: 0 },
  software: { name: '个人软件管理', icon: 'List', count: 0 },
  files: { name: '个人文件', icon: 'Folder', count: 0 },
  selfclean: { name: '本应用自身', icon: 'DeleteFilled', count: 0 }
})

// 统计卡片数据
const stats = ref({
  total: '0',
  size: '0 B',
  cleaned: '0',
  scanTime: '0.0s',
  modules: '0/9'
})

const statCards = computed(() => [
  { key: 'total', title: '发现数量', value: stats.value.total, icon: 'Search', bgClass: 'bg-blue-50', textClass: 'text-blue-600' },
  { key: 'size', title: '文件大小', value: stats.value.size, icon: 'Histogram', bgClass: 'bg-red-50', textClass: 'text-red-600' },
  { key: 'cleaned', title: '已清理项', value: stats.value.cleaned, icon: 'CircleCheck', bgClass: 'bg-green-50', textClass: 'text-green-600' },
  { key: 'scanTime', title: '扫描用时', value: stats.value.scanTime, icon: 'Clock', bgClass: 'bg-orange-50', textClass: 'text-orange-600' },
  { key: 'modules', title: '模块加载', value: stats.value.modules, icon: 'Cpu', bgClass: 'bg-purple-50', textClass: 'text-purple-600' }
])

// --- Fallback 模拟 API (用于在普通浏览器预览调试) ---
const hasPyWebView = typeof window.pywebview !== 'undefined'

const callBackend = async (method, ...args) => {
  if (hasPyWebView) {
    try {
      return await window.pywebview.api[method](...args)
    } catch (e) {
      addLog('error', `调用后端接口 ${method} 失败: ${e}`)
      throw e
    }
  } else {
    // 浏览器本地 Mock 数据
    return await mockAPI(method, ...args)
  }
}

// --- 过滤选项逻辑 ---
const filteredItems = computed(() => {
  if (currentCategory.value === 'all') {
    return items.value
  }
  return items.value.filter(item => item.cat === currentCategory.value)
})

// --- 全选与勾选联动逻辑 ---
const selectedPaths = computed(() => {
  return items.value.filter(item => item.checked).map(item => item.path)
})

const isAllSelected = computed({
  get() {
    const list = filteredItems.value
    if (list.length === 0) return false
    return list.every(item => item.checked)
  },
  set(val) {
    filteredItems.value.forEach(item => {
      item.checked = val
    })
  }
})

const isIndeterminate = computed(() => {
  const list = filteredItems.value
  if (list.length === 0) return false
  const checkedCount = list.filter(item => item.checked).length
  return checkedCount > 0 && checkedCount < list.length
})

const selectCategory = (key) => {
  currentCategory.value = key
  selectedRow.value = null
  detailContent.value = ''
}

const toggleItem = (row) => {
  // 可以根据需要添加联动
}

const toggleSelectAll = (val) => {
  // 已经在 set 属性处理了
}

// --- 扫描逻辑 ---
let logPollInterval = null
const startLogPolling = () => {
  if (logPollInterval) clearInterval(logPollInterval)
  logPollInterval = setInterval(async () => {
    try {
      const records = await callBackend('get_new_logs')
      if (records && records.length > 0) {
        records.forEach(rec => {
          let type = 'info'
          let msg = rec
          if (rec.startsWith('[成功]')) {
            type = 'success'
            msg = rec.substring(4).trim()
          } else if (rec.startsWith('[错误]')) {
            type = 'error'
            msg = rec.substring(4).trim()
          } else if (rec.startsWith('[警告]')) {
            type = 'warning'
            msg = rec.substring(4).trim()
          } else if (rec.startsWith('[信息]')) {
            type = 'info'
            msg = rec.substring(4).trim()
          }
          addLog(type, msg)
        });
      }
    } catch (e) {}
  }, 250)
}

const stopLogPolling = () => {
  if (logPollInterval) {
    clearInterval(logPollInterval)
    logPollInterval = null
  }
}

const startScan = async () => {
  if (isScanning.value) return
  isScanning.value = true
  progress.value = 0
  progressText.value = '正在初始化...'
  items.value = []
  selectedRow.value = null
  detailContent.value = ''
  
  // 清零统计
  stats.value.total = '0'
  stats.value.size = '0 B'
  stats.value.scanTime = '0.0s'
  stats.value.modules = '0/9'
  
  addLog('info', '开始全系统扫描数据痕迹...')
  
  startLogPolling()
  
  // 开启定时计时器
  const startTime = Date.now()
  const timer = setInterval(() => {
    if (!isScanning.value) {
      clearInterval(timer)
      return
    }
    stats.value.scanTime = ((Date.now() - startTime) / 1000).toFixed(1) + 's'
  }, 100)

  try {
    const rawResults = await callBackend('scan')
    // 处理扫描结果，把 list 装载到 items.ref
    const processed = []
    let totalSize = 0
    const catCounts = { all: 0, uninstall: 0, browser: 0, chat: 0, credentials: 0, devenv: 0, aitools: 0, software: 0, files: 0, selfclean: 0 }
    
    // 初始化模块数
    let loadedModules = 0

    // 根据后端返回的数据进行整理
    for (const [catKey, list] of Object.entries(rawResults)) {
      loadedModules++
      const activeList = list.filter(r => r[3]) // exists 是 true
      catCounts[catKey] = activeList.length
      
      activeList.forEach(r => {
        const desc = r[0]
        const path = r[1]
        const sizeStr = r[2]
        
        let status = '存在'
        let optype = '清除'
        if (path.startsWith?.('uninstall:') || desc.includes('[卸载]')) {
          status = '可卸载'
          optype = '卸载'
        } else if (path.startsWith?.('regclean:') || desc.includes('[注册表]')) {
          status = '残留'
          optype = '注册表'
        } else if (path.startsWith?.('selfdestruct:') || desc.includes('[本应用]')) {
          status = '可卸载'
          optype = '自卸载'
        } else if (path.startsWith?.('manual_review:') || desc.includes('[手动审核]')) {
          status = '建议手动'
          optype = '手动处理'
        }

        // 提取绝对路径用于前端展示
        let realPath = path
        for (const prefix of ['uninstall:', 'data:', 'regclean:', 'selfdestruct:', 'manual_review:']) {
          if (realPath.startsWith(prefix)) {
            realPath = realPath.substring(prefix.length)
            break
          }
        }
        
        let displayPath = realPath
        if (displayPath.length > 50) {
          displayPath = '...' + displayPath.substring(displayPath.length - 47)
        }

        const isWarning = desc.includes('⚠') || desc.includes('★') || optype === '手动处理'

        processed.push({
          cat: catKey,
          desc,
          path, // 完整路径，带前缀
          realPath, // 真实磁盘路径/命令
          displayPath,
          size: sizeStr,
          status,
          optype,
          checked: false, // 默认不勾选，防误杀
          isWarning
        })

        // 累加大小
        totalSize += parseSize(sizeStr)
      })
    }

    items.value = processed
    stats.value.total = String(processed.length)
    stats.value.size = formatSize(totalSize)
    stats.value.modules = `${loadedModules}/9`
    
    // 更新分类计数
    for (const key in categories.value) {
      if (key === 'all') {
        categories.value[key].count = processed.length
      } else {
        categories.value[key].count = catCounts[key] || 0
      }
    }
    
    progress.value = 100
    progressText.value = '扫描完成'
    addLog('success', `扫描完成！共发现 ${processed.length} 项可清理内容，文件总大小 ${stats.value.size}`)
  } catch (e) {
    addLog('error', `扫描失败: ${e}`)
    progressText.value = '扫描失败'
  } finally {
    isScanning.value = false
    stopLogPolling()
    // 强制执行一次最后的日志同步
    setTimeout(async () => {
      const finalRecs = await callBackend('get_new_logs')
      if (finalRecs) {
        finalRecs.forEach(r => addLog('info', r))
      }
    }, 500)
  }
}

// --- 清理逻辑 ---
const handleBatchClean = () => {
  const selectedList = items.value.filter(item => item.checked)
  if (selectedList.length === 0) return
  
  // 统计软件卸载与文件清理个数
  const uninstallCount = selectedList.filter(item => item.optype === '卸载' || item.optype === '自卸载').length
  const cleanCount = selectedList.length - uninstallCount
  
  let msg = `确定要清理选中的 ${selectedList.length} 项数据吗？<br><br>`
  if (uninstallCount > 0) {
    msg += `<b>⚠ 警告：包含 ${uninstallCount} 个软件将被卸载！</b><br>`
  }
  msg += `清除后数据将永久删除且不可恢复。`

  ElMessageBox.confirm(
    msg,
    '批量清理确认',
    {
      confirmButtonText: '确定继续',
      cancelButtonText: '取消',
      type: 'warning',
      dangerouslyUseHTMLString: true
    }
  ).then(async () => {
    // 最终确认
    ElMessageBox.confirm(
      '重要数据删除后无法恢复，这是最后一次确认，是否继续？',
      '最终确认',
      {
        confirmButtonText: '最终确定',
        cancelButtonText: '我再想想',
        type: 'error'
      }
    ).then(async () => {
      await executeBatchClean(selectedList)
    }).catch(() => {})
  }).catch(() => {})
}

const executeBatchClean = async (selectedList) => {
  addLog('warning', `启动批量清理任务，共 ${selectedList.length} 项...`)
  progress.value = 0
  progressText.value = '正在清理...'
  startLogPolling()

  // 按分类对路径分组，方便后端批量按模块清理
  const byCat = {}
  selectedList.forEach(item => {
    if (!byCat[item.cat]) byCat[item.cat] = []
    byCat[item.cat].push(item.path)
  })

  let cleanedCount = 0
  const totalToClean = selectedList.length

  try {
    for (const [catKey, paths] of Object.entries(byCat)) {
      addLog('info', `正在处理分类 [${categories.value[catKey]?.name || catKey}]...`)
      // 调用 PyAPI 清理
      const resCount = await callBackend('clean_paths', catKey, paths)
      cleanedCount += resCount
      progress.value = Math.min(Math.round((cleanedCount / totalToClean) * 100), 99)
      progressText.value = `已清理 ${cleanedCount}/${totalToClean}`
    }

    progress.value = 100
    progressText.value = '清理完成'
    stats.value.cleaned = String(parseInt(stats.value.cleaned) + cleanedCount)
    ElMessage.success('批量清理完成！')
    
    // 重新扫描以确认
    setTimeout(startScan, 1500)
  } catch (e) {
    addLog('error', `清理执行中发生异常: ${e}`)
    progressText.value = '清理异常'
  } finally {
    stopLogPolling()
  }
}

// --- 单行点击逻辑 ---
const handleRowClick = async (row) => {
  selectedRow.value = row
  detailContent.value = ''
  
  if (row.optype === '手动处理') {
    // 触发安全警示模态框
    protectedPath.value = row.realPath
    warningVisible.value = true
    return
  }

  // 异步获取数据详情预览
  detailLoading.value = true
  try {
    const details = await callBackend('get_path_details', row.cat, row.path)
    detailContent.value = details
  } catch (e) {
    detailContent.value = `无法获取详情: ${e}`
  } finally {
    detailLoading.value = false
  }
}

// --- 单个按钮操作 ---
const openSelectedPath = async () => {
  if (!selectedRow.value) return
  try {
    const ok = await callBackend('open_path', selectedRow.value.path)
    if (!ok) ElMessage.error('目录不存在或无法打开')
  } catch (e) {}
}

const copySelectedPath = async () => {
  if (!selectedRow.value) return
  try {
    await callBackend('copy_path', selectedRow.value.path)
    ElMessage.success('路径已成功复制到剪贴板！')
  } catch (e) {}
}

// --- 控制台日志辅助 ---
const addLog = (type, msg) => {
  const d = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  const timeStr = `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
  logs.value.push({ type, msg, time: timeStr })
  
  // 滚动到底部
  setTimeout(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    }
  }, 50)
}

const clearLogs = () => {
  logs.value = []
}

const getLogClass = (type) => {
  switch (type) {
    case 'error': return 'text-red-400 font-bold'
    case 'success': return 'text-green-400 font-bold'
    case 'warning': return 'text-yellow-400'
    case 'info':
    default: return 'text-blue-300'
  }
}

// Tag 样式映射
const getStatusTagType = (status) => {
  switch (status) {
    case '存在': return 'danger'
    case '残留': return 'warning'
    case '可卸载': return 'primary'
    case '建议手动':
    default: return 'info'
  }
}

const getOpTagType = (optype) => {
  switch (optype) {
    case '卸载': return 'warning'
    case '自卸载': return 'danger'
    case '注册表': return 'info'
    case '手动处理': return 'info'
    case '清除':
    default: return 'success'
  }
}

// 辅助方法：解析大小字符串
const parseSize = (sizeStr) => {
  if (!sizeStr) return 0
  const match = sizeStr.trim().match(/^([0-9.]+)\s*([a-zA-Z]+)$/)
  if (!match) return 0
  const val = parseFloat(match[1])
  const unit = match[2].toUpperCase()
  const sm = { B: 1, KB: 1024, MB: 1024 ** 2, GB: 1024 ** 3, TB: 1024 ** 4 }
  return val * (sm[unit] || 1)
}

const formatSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// --- 生命钩子 ---
onMounted(() => {
  updateClock()
  clockTimer = setInterval(updateClock, 1000)
})

onUnmounted(() => {
  if (clockTimer) clearInterval(clockTimer)
  stopLogPolling()
})

// --- Mock 模拟 API 逻辑 (纯前端环境) ---
const mockLogs = ref([
  '[信息] 初始化本地清理模块...',
  '[信息] 准备就绪，欢迎使用离职数据清理助手。'
])

const mockAPI = async (method, ...args) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      if (method === 'get_new_logs') {
        const copy = [...mockLogs.value]
        mockLogs.value = []
        resolve(copy)
      } 
      else if (method === 'scan') {
        mockLogs.value.push('[成功] [开发环境] 扫描完毕！')
        mockLogs.value.push('[警告] [手动审核] 扫描到桌面和文档可能包含敏感数据。')
        resolve({
          browser: [
            ['Chrome - 登录的Google/MS账号', 'data:C:\\Users\\Mock\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Preferences', '2.4 MB', true],
            ['Chrome - 已保存的密码', 'data:C:\\Users\\Mock\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Login Data', '450 KB', true],
            ['Edge - 浏览历史记录', 'data:C:\\Users\\Mock\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\History', '12 MB', true]
          ],
          chat: [
            ['微信 - [聊天记录] 数据库', 'data:C:\\Users\\Mock\\Documents\\WeChat Files\\wxid_123\\Msg', '420 MB', true],
            ['微信 - 聊天文件/文档', 'data:C:\\Users\\Mock\\Documents\\xwechat_files\\wxid_123\\msg\\file', '1.2 GB', true],
            ['钉钉 - 应用数据/聊天文件', 'data:C:\\Users\\Mock\\AppData\\Local\\DingTalk', '850 MB', true]
          ],
          credentials: [
            ['Windows 凭据管理器 (5条)', 'credentials', '5 条', true],
            ['SSH密钥目录', 'data:C:\\Users\\Mock\\.ssh', '4 KB', true],
            ['Git明文密码存储!', 'data:C:\\Users\\Mock\\.git-credentials', '120 B', true],
            ['系统环境变量 - ⚠ AWS_SECRET_ACCESS_KEY', 'env:HKLM:AWS_SECRET_ACCESS_KEY', '环境变量', true]
          ],
          devenv: [
            ['VS Code - 扩展/配置', 'data:C:\\Users\\Mock\\.vscode', '680 MB', true],
            ['JetBrains 全家桶 - 缓存/索引', 'data:C:\\Users\\Mock\\AppData\\Local\\JetBrains', '2.3 GB', true],
            ['本地项目代码仓库 - ⚠ LeaveClean (https://github.com/...)', 'data:C:\\Users\\Mock\\Desktop\\LeaveClean', '1.2 MB', true]
          ],
          aitools: [
            ['Claude Code - 对话历史/MCP配置', 'data:C:\\Users\\Mock\\.claude', '42 KB', true],
            ['Cursor - 应用数据/缓存/账号令牌', 'data:C:\\Users\\Mock\\AppData\\Roaming\\Cursor', '180 MB', true]
          ],
          software: [
            ['[卸载] 百度网盘', 'uninstall:"C:\\Program Files\\BaiduNetdisk\\uninst.exe"', '已安装', true],
            ['[数据] 向日葵远程控制', 'data:C:\\Users\\Mock\\AppData\\Roaming\\Oray', '45 MB', true]
          ],
          files: [
            ['[敏感文件] Desktop - ⚠ 2026年劳动合同.pdf', 'data:C:\\Users\\Mock\\Desktop\\2026年劳动合同.pdf', '1.2 MB', true],
            ['[大安装包/压缩包] Downloads - node-v20.11.0-x64.msi', 'data:C:\\Users\\Mock\\Downloads\\node-v20.11.0-x64.msi', '31.2 MB', true],
            ['[手动审核] 建议手动核对 Desktop 目录 (152项)', 'manual_review:C:\\Users\\Mock\\Desktop', '4.2 GB', true],
            ['[手动审核] 建议手动核对 Documents 目录 (88项)', 'manual_review:C:\\Users\\Mock\\Documents', '1.5 GB', true]
          ],
          selfclean: [
            ['[本应用] LeaveClean 清理助手（自卸载）', 'selfdestruct:C:\\Users\\Mock\\Desktop\\LeaveClean', '44 KB', true]
          ]
        })
      }
      else if (method === 'get_path_details') {
        const path = args[1] || ''
        if (path.includes('2026年劳动合同.pdf')) {
          resolve('PDF 格式文件，暂无法预览文本，可点击上方“打开目录”直接查看此敏感文件')
        } else if (path.includes('.git-credentials')) {
          resolve('https://username:password123@github.com\n\n警告：包含明文的 Git 凭据信息！')
        } else if (path.includes('.ssh')) {
          resolve('📁 包含密钥文件:\n  📄 id_rsa (私钥 - ⚠️ 严禁留置)\n  📄 id_rsa.pub (公钥)\n  📄 known_hosts')
        } else {
          resolve(`当前路径: ${path}\n\n该项数据可由清理助手进行一键安全销毁。`)
        }
      }
      else if (method === 'clean_paths') {
        const len = (args[1] || []).length
        mockLogs.value.push(`[成功] 已批量清除 ${len} 项数据痕迹`)
        resolve(len)
      }
      else if (method === 'open_path') {
        mockLogs.value.push(`[信息] 打开路径: ${args[0]}`)
        resolve(true)
      }
      else if (method === 'copy_path') {
        mockLogs.value.push(`[信息] 复制路径到剪贴板: ${args[0]}`)
        resolve(true)
      }
    }, 500)
  })
}
</script>

<style>
/* 额外精细样式微调 */
.el-table .cell {
  padding: 0 4px !important;
}
.el-table__row {
  cursor: pointer;
}
.el-table__row:hover {
  background-color: #f8fafc !important;
}
</style>
