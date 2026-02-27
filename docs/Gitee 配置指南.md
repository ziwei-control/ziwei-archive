# 紫微智控 · Gitee 配置指南

> 配置 Gitee 双平台同步

---

## 🎯 为什么需要 Gitee？

| 优势 | 说明 |
|------|------|
| **国内访问快** | Gitee 在中国大陆访问速度远快于 GitHub |
| **中文界面** | 全中文界面，更易用 |
| **备份冗余** | 双平台备份，更安全 |
| **合规性** | 符合国内数据合规要求 |

---

## 📋 第一步：获取 Gitee Token

### 1. 注册/登录 Gitee

访问：https://gitee.com

- 如果没有账号，先注册
- 已有账号直接登录

### 2. 创建个人访问令牌

1. 点击右上角头像 → **设置**
2. 左侧菜单选择 **安全设置**
3. 找到 **私人令牌** 或 **个人访问令牌**
4. 点击 **生成新令牌**

### 3. 配置令牌权限

勾选以下权限：
- ✅ `projects` - 访问项目
- ✅ `pull_requests` - 拉取请求
- ✅ `issues` - Issues
- ✅ `notes` - 评论/笔记
- ✅ `repository` - 仓库管理

### 4. 复制 Token

- 生成后**立即复制** Token
- Token 只显示一次，关闭后无法再查看
- 格式类似：`a1b2c3d4e5f6g7h8i9j0`

---

## 🔧 第二步：配置到紫微智控

### 1. 编辑 .env 文件

```bash
nano /home/admin/Ziwei/.env
```

### 2. 填写 Gitee 配置

找到这两行：

```bash
# Gitee 配置（中国镜像）
GITEE_TOKEN="your_gitee_token_here"
GITEE_REPO="https://gitee.com/ziwei-control/ziwei-archive.git"
```

修改为：

```bash
# Gitee 配置（中国镜像）
GITEE_TOKEN="你的真实 Token"
GITEE_REPO="https://gitee.com/你的用户名/ziwei-archive.git"
```

### 3. 保存退出

- `Ctrl+O` 保存
- `Enter` 确认
- `Ctrl+X` 退出

---

## 📁 第三步：创建 Gitee 仓库

### 方法 A: 自动创建（推荐）

运行同步脚本会自动处理：

```bash
cd /home/admin/Ziwei
bash scripts/sync-to-both.sh
```

### 方法 B: 手动创建

1. 访问 https://gitee.com
2. 点击右上角 `+` → **新建仓库**
3. 填写：
   - **仓库名称**: ziwei-archive
   - **仓库介绍**: 紫微智控项目
   - **公开性**: 私有（推荐）
4. 点击 **创建**
5. 复制仓库地址，更新 `.env` 中的 `GITEE_REPO`

---

## 🚀 第四步：测试同步

### 运行同步脚本

```bash
cd /home/admin/Ziwei
bash scripts/sync-to-both.sh
```

### 查看输出

```
╔════════════════════════════════════════════════════════╗
║          紫微智控 - 双平台同步 (GitHub + Gitee)         ║
╚════════════════════════════════════════════════════════╝

[1/5] 加载配置...
  ✓ GitHub 配置：已加载
  ✓ Gitee 配置：已加载

[2/5] 检查 Git 状态...
  ✓ 没有未提交的更改

[3/5] 推送到 GitHub...
  ✓ GitHub 推送成功

[4/5] 推送到 Gitee...
  ✓ Gitee 推送成功

[5/5] 生成同步报告...
  ✓ 同步报告已保存

╔════════════════════════════════════════════════════════╗
║              ✅ 双平台同步完成！                       ║
╚════════════════════════════════════════════════════════╝
```

---

## 📊 查看同步报告

同步报告会保存到：

```bash
data/logs/sync_report_YYYYMMDD_HHMMSS.md
```

查看最新报告：

```bash
cat data/logs/sync_report_*.md | tail -20
```

---

## 🔄 日常使用

### 快速同步

```bash
# 方式 1: 使用同步脚本（推荐）
bash scripts/sync-to-both.sh

# 方式 2: 手动推送到双平台
git add .
git commit -m "更新说明"
git push github main
git push gitee main
```

### 查看远程仓库

```bash
# 查看所有 remote
git remote -v

# 输出示例：
# github  https://github.com/ziwei-control/ziwei-archive.git (fetch)
# github  https://github.com/ziwei-control/ziwei-archive.git (push)
# gitee   https://gitee.com/ziwei-control/ziwei-archive.git (fetch)
# gitee   https://gitee.com/ziwei-control/ziwei-archive.git (push)
```

---

## ⚠️ 常见问题

### 问题 1: Gitee Token 无效

**原因**: Token 过期或权限不足

**解决**:
1. 重新生成 Token
2. 确保勾选了 `repository` 权限
3. 更新 `.env` 文件

### 问题 2: 推送失败

**原因**: 仓库不存在或权限不足

**解决**:
1. 手动在 Gitee 创建仓库
2. 检查 Token 权限
3. 确认仓库地址正确

### 问题 3: 只想推送到 GitHub

**解决**: 不配置 GITEE_TOKEN 即可

```bash
# 在 .env 中留空或删除
GITEE_TOKEN=""
```

脚本会自动跳过 Gitee 推送。

---

## 📋 配置检查清单

- [ ] 已注册 Gitee 账号
- [ ] 已生成个人访问令牌
- [ ] 已复制 Token 到 `.env`
- [ ] 已创建 Gitee 仓库（或自动创建）
- [ ] 已运行同步脚本测试
- [ ] 双平台都能看到代码

---

## 🔗 相关文档

- [[Obsidian 快速入门]] - Obsidian 使用教程
- [[工作流程图]] - 紫微智控工作流程
- [GitHub 仓库](https://github.com/ziwei-control/ziwei-archive)
- [Gitee 仓库](https://gitee.com/ziwei-control/ziwei-archive) (配置后可见)

---

**配置完成后，运行 `bash scripts/sync-to-both.sh` 即可双平台同步！** 🎉
