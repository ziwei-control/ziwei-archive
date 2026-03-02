# 📦 创建远程仓库指南

## GitHub

1. 访问 https://github.com/new
2. 仓库名：`ziwei-audit-system`
3. 描述：紫微智控 - 全面自动化审计系统
4. 公开仓库 ✅
5. 点击 "Create repository"
6. 推送代码：
   ```bash
   cd /home/admin/Ziwei/projects/ziwei-audit-system
   git remote set-url github git@github.com:ziwei-control/ziwei-audit-system.git
   git push -u github main
   ```

## Gitee

1. 访问 https://gitee.com/new
2. 仓库名：`ziwei-audit-system`
3. 描述：紫微智控 - 全面自动化审计系统
4. 公开仓库 ✅
5. 点击 "创建"
6. 推送代码：
   ```bash
   cd /home/admin/Ziwei/projects/ziwei-audit-system
   git remote set-url gitee git@gitee.com:ziwei-control/ziwei-audit-system.git
   git push -u gitee main
   ```

## 一键推送（创建后执行）

```bash
cd /home/admin/Ziwei/projects/ziwei-audit-system
git push github main
git push gitee main
```
