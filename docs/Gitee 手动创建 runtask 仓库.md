# Gitee 手动创建 runtask 仓库指南

> Token 已过期，需要手动创建仓库

---

## ⚠️ 情况说明

**Gitee Token 已过期/无效**

**解决方案**: 手动创建仓库，然后使用 SSH 推送

---

## 📋 创建步骤

### 步骤 1: 访问 Gitee 创建页面

打开浏览器访问：
```
https://gitee.com/new
```

---

### 步骤 2: 填写仓库信息

| 字段 | 填写内容 |
|------|---------|
| **仓库名称** | `runtask` |
| **介绍** | 紫微智控一键启动任务命令 |
| **公开性** | 公开 |
| **初始化 README** | ✅ 勾选 |
| **许可证** | MIT（可选） |

---

### 步骤 3: 点击创建

点击页面底部的 **创建** 按钮

---

### 步骤 4: 推送本地内容

仓库创建后，在终端执行：

```bash
cd /home/admin/Ziwei/projects/runtask

# 添加 Gitee remote（如果还没有）
git remote add gitee git@gitee.com:pandac0/runtask.git

# 推送到 Gitee
git push -u gitee main
```

---

## ✅ 验证

### 检查 GitHub 仓库

访问：https://github.com/ziwei-control/runtask

应该看到：
- ✅ README.md
- ✅ 项目说明

### 检查 Gitee 仓库

访问：https://gitee.com/pandac0/runtask

应该看到：
- ✅ README.md
- ✅ 项目说明

---

## 🔧 故障排查

### 问题 1: 权限错误

**错误**: `Permission denied (publickey)`

**解决**:
```bash
# 测试 SSH 连接
ssh -T git@gitee.com

# 如果失败，添加 SSH 公钥到 Gitee
# 访问：https://gitee.com/profile/sshkeys
```

### 问题 2: 仓库不存在

**错误**: `404 not found`

**解决**:
- 确认仓库已创建
- 确认仓库名称正确：`runtask`
- 确认用户名正确：`pandac0`

### 问题 3: remote 已存在

**错误**: `remote gitee already exists`

**解决**:
```bash
# 更新 remote URL
git remote set-url gitee git@gitee.com:pandac0/runtask.git

# 再次推送
git push -u gitee main
```

---

## 📊 完整状态

| 平台 | 状态 | 地址 |
|------|------|------|
| **GitHub** | ✅ 已创建 | https://github.com/ziwei-control/runtask |
| **Gitee** | ⏳ 待手动创建 | https://gitee.com/pandac0/runtask |

---

## 🎯 后续步骤

### 1. 创建 Gitee 仓库

按照上述步骤手动创建

### 2. 推送代码

```bash
cd /home/admin/Ziwei/projects/runtask
git push -u gitee main
```

### 3. 上传脚本（可选）

```bash
cd /home/admin/Ziwei/projects/runtask

# 复制脚本
cp /home/admin/Ziwei/scripts/install-runtask.sh .
cp /home/admin/Ziwei/scripts/uninstall-runtask.sh .

# 提交并推送
git add .
git commit -m "添加安装/卸载脚本"
git push
git push gitee main
```

---

## 🔗 相关链接

- [Gitee 新建仓库](https://gitee.com/new)
- [Gitee SSH 公钥设置](https://gitee.com/profile/sshkeys)
- [GitHub runtask 仓库](https://github.com/ziwei-control/runtask)

---

**手动创建后，双平台同步就完整了！** 🚀
