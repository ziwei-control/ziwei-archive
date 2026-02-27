# 紫微智控 · Obsidian 插件完全指南

> 16 个插件已全部安装，本文档说明如何启用和使用

---

## ✅ 安装状态

| 类别 | 插件 | 状态 |
|------|------|------|
| **必备** | Dataview | ✅ 已安装 |
| **必备** | Full Calendar | ✅ 已安装 |
| **必备** | Smart Connections | ✅ 已安装 |
| **高级** | Tasks | ✅ 已安装 |
| **高级** | Kanban | ✅ 已安装 |
| **高级** | Excalidraw | ✅ 已安装 |
| **高级** | Advanced Tables | ✅ 已安装 |
| **高级** | QuickAdd | ✅ 已安装 |
| **高级** | Templater | ✅ 已安装 |
| **高级** | Various Complements | ✅ 已安装 |
| **高级** | Recent Files | ✅ 已安装 |
| **专业** | Projects | ✅ 已安装 |
| **专业** | Bases | ✅ 已安装 |
| **专业** | Linter | ✅ 已安装 |
| **专业** | Waypoint | ✅ 已安装 |
| **专业** | Tracker | ✅ 已安装 |

---

## 🔧 如何启用插件

### 步骤 1: 打开 Obsidian 设置

1. 打开 Obsidian
2. 点击左下角 **设置** (齿轮图标)
3. 选择 **第三方插件**

### 步骤 2: 关闭安全模式

- 如果看到"安全模式已启用"，关闭它
- 这样 Obsidian 才会加载已安装的插件

### 步骤 3: 启用插件

在 **已安装的插件** 列表中，逐个启用：

---

## 📦 必备插件详解

### 1. Dataview

**用途**: 数据查询和动态视图

**启用后**:
- 设置 → 选项 → Dataview
- 启用 "Enable Dataview"

**紫微智控用法**:

````markdown
## 所有进行中任务
```dataview
TABLE 优先级，截止时间
FROM "data/tasks"
WHERE 状态 = "In Progress"
SORT 优先级 ASC
```

## 今日创建任务
```dataview
LIST
FROM "data/tasks"
WHERE date(file.day) = date(today)
```

## 高优先级任务
```dataview
TABLE 截止时间，状态
FROM "data/tasks"
WHERE 优先级 = "高"
SORT 截止时间 ASC
```
````

---

### 2. Full Calendar

**用途**: 日历视图

**启用后**:
- 左侧边栏会出现日历图标
- 点击打开日历视图

**紫微智控用法**:
- 显示任务截止时间
- 安排巡查时间表
- 标记审计日期
- 拖拽任务调整日期

---

### 3. Smart Connections

**用途**: AI 智能关联

**启用后**:
- 设置 → Smart Connections
- 需要配置 API（可选）

**紫微智控用法**:
- 自动发现相关任务
- 智能推荐文档
- 语义搜索

---

## 📦 高级插件详解

### 4. Tasks

**用途**: 任务管理

**启用后**:
- 设置 → Tasks
- 配置任务格式

**紫微智控用法**:

````markdown
## 待办事项
- [ ] 创建任务文档 #任务
- [ ] 分解任务 #任务
- [ ] 执行代码生成 #任务
- [ ] 提交审计 #任务

## 全局任务视图
```tasks
not done
sort by priority
```
````

---

### 5. Kanban

**用途**: 看板视图

**启用后**:
- 右键 → 新建看板
- 或使用模板

**紫微智控用法**:

````markdown
```kanban
# Inbox
- [ ] TASK-20250227-001 测试任务

# 进行中
- [ ] TASK-20250227-002

# 审计中
- [ ] TASK-20250227-003

# 已完成
- [x] TASK-20250226-001
```
````

---

### 6. Excalidraw

**用途**: 手绘图表

**启用后**:
- 右键 → 新建 Excalidraw 绘图
- 或使用命令面板

**紫微智控用法**:
- 绘制系统架构图
- 工作流程图
- 岗位协作关系图
- UI 设计草图

---

### 7. Advanced Tables

**用途**: 表格增强

**启用后**:
- 自动格式化表格
- 快捷键操作表格

**紫微智控用法**:
- 审计记录表格
- 巡查记录表格
- 岗位配置表格

**快捷键**:
- `Tab` - 下一单元格
- `Shift+Tab` - 上一单元格
- `Alt+Enter` - 插入行

---

### 8. QuickAdd

**用途**: 快速添加

**启用后**:
- 设置 → QuickAdd
- 配置宏和模板

**紫微智控用法**:
- 一键创建任务
- 快速记录沟通日志
- 快捷命令

---

### 9. Templater

**用途**: 增强模板

**启用后**:
- 设置 → Templater
- 配置模板文件夹

**紫微智控用法**:

````markdown
<%*
// 自动填入任务 ID
const taskId = "TASK-" + tp.date.now("YYYYMMDD") + "-001";
tR += `任务 ID: ${taskId}`;
%>
````

---

### 10. Various Complements

**用途**: 自动补全

**启用后**:
- 设置 → Various Complements
- 启用自动补全

**紫微智控用法**:
- 输入 `[[` 自动提示笔记
- 输入 `#` 自动提示标签
- 输入 `T-01` 提示岗位名称

---

### 11. Recent Files

**用途**: 最近文件

**启用后**:
- 左侧边栏显示最近文件
- 快速访问

**紫微智控用法**:
- 快速打开最近编辑的任务
- 查看最近修改的文档

---

## 📦 专业插件详解

### 12. Projects

**用途**: 项目管理

**启用后**:
- 左侧边栏出现 Projects 图标
- 创建项目数据库

**紫微智控用法**:
- 管理多个客户项目
- 项目进度追踪
- 资源分配

---

### 13. Bases

**用途**: 数据库功能

**启用后**:
- 创建自定义数据库
- 定义字段和视图

**紫微智控用法**:
- 任务数据库
- 客户数据库
- 岗位数据库

---

### 14. Linter

**用途**: 格式规范化

**启用后**:
- 设置 → Linter
- 配置格式规则

**紫微智控用法**:
- 统一 Markdown 格式
- 自动修复格式问题
- 保存时自动格式化

---

### 15. Waypoint

**用途**: 导航索引

**启用后**:
- 在文件夹中创建索引页
- 自动生成目录

**紫微智控用法**:
- 创建 SOP 文档索引
- 任务文件夹导航
- 知识库目录

---

### 16. Tracker

**用途**: 数据追踪

**启用后**:
- 设置 → Tracker
- 配置追踪字段

**紫微智控用法**:
- 追踪任务完成时间
- 成本统计
- 岗位工作效率

---

## 🎯 推荐启用顺序

### 第一批（立即启用）

1. ✅ **Dataview** - 数据查询核心
2. ✅ **Tasks** - 任务管理基础
3. ✅ **Kanban** - 可视化工作流
4. ✅ **Templater** - 模板增强

### 第二批（今天启用）

5. **Full Calendar** - 日历视图
6. **Advanced Tables** - 表格增强
7. **Various Complements** - 自动补全
8. **Recent Files** - 最近文件

### 第三批（本周启用）

9. **Excalidraw** - 绘图工具
10. **QuickAdd** - 快速添加
11. **Projects** - 项目管理
12. **Linter** - 格式规范

### 第四批（按需启用）

13. **Smart Connections** - AI 关联（需配置）
14. **Bases** - 数据库（高级功能）
15. **Waypoint** - 导航索引
16. **Tracker** - 数据追踪

---

## 📋 配置检查清单

启用插件后，检查以下配置：

### Dataview
- [ ] 启用 "Enable Dataview"
- [ ] 启用 "Enable Inline Queries"

### Tasks
- [ ] 配置任务格式
- [ ] 设置全局查询

### Templater
- [ ] 设置模板文件夹为 `docs/templates/`
- [ ] 配置快捷键

### Kanban
- [ ] 创建第一个看板
- [ ] 配置列名

### Linter
- [ ] 启用 "Lint on save"
- [ ] 配置格式规则

---

## 💡 紫微智控专属配置

### 任务模板增强

使用 Templater 创建动态任务模板：

````markdown
---
任务 ID: TASK-<% tp.date.now("YYYYMMDD") %>-001
创建时间：<% tp.date.now("YYYY-MM-DDTHH:mm:ssZ") %>
创建者：Martin
优先级：中
截止时间：<% tp.date.now("YYYY-MM-DD", 1) %>
状态：Inbox
---

# 任务：<% tp.file.title %>

## 任务描述
<% tp.file.cursor() %>

## 期望输出
1. 
2. 

## 验收标准
- [ ] 
- [ ] 

## 执行记录
- 分解时间：
- 分解者：T-01 首席架构师
````

---

### Dataview 查询模板

创建查询模板笔记：

````markdown
# 任务查询模板

## 所有进行中任务
```dataview
TABLE 优先级，截止时间，状态
FROM "data/tasks"
WHERE 状态 = "In Progress"
SORT 优先级 ASC
```

## 逾期任务
```dataview
TABLE 优先级，创建者
FROM "data/tasks"
WHERE 截止时间 < date(today)
WHERE 状态 != "Done"
```

## 今日任务
```dataview
LIST
FROM "data/tasks"
WHERE date(file.day) = date(today)
```
````

---

## 🔗 相关文档

- [[Obsidian 快速入门]] - 基础使用教程
- [[工作流程图]] - 紫微智控工作流程
- [[紫微智控驾驶舱]] - 系统总览

---

**插件安装完成！现在可以在 Obsidian 中启用并开始使用了！** 🎉
