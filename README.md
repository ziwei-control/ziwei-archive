# 紫微智控 (Ziwei Control & Intelligence)

> AI 驱动的一人公司系统

## 快速开始

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入真实的 API Key
```

### 2. 安装依赖

```bash
pip3 install -r scripts/requirements.txt
```

### 3. 启动系统

```bash
# 启动本地监控
python3 scripts/local_monitor.py &

# 启动进度监工（18 分钟巡查）
python3 scripts/supervisor.py &
```

## 目录结构

```
Ziwei/
├── SOP/                    # 标准作业程序文档
├── config/                 # 配置文件
│   └── agents.yaml        # 岗位配置
├── scripts/               # 脚本
│   ├── deploy.sh         # 部署脚本
│   ├── local_monitor.py  # 本地监控
│   └── supervisor.py     # 进度监工
├── data/                  # 数据
│   ├── logs/             # 日志
│   ├── tasks/            # 任务
│   └── health/           # 健康监控
├── docs/                  # 文档
├── projects/              # 项目
└── repo_archive/          # 归档库
```

## 核心机制

- **巡查机制**: 每 18 分钟巡查，每 4 小时简报
- **审计机制**: 四维审查，最多 20 次重做
- **急救机制**: 心跳监控，云端会诊
- **学习机制**: 每小时轮转 5 分钟

## 文档

详见 `SOP/` 文件夹中的完整规范。

## 联系方式

- 康纳：19922307306@189.cn
- Martin: pandac00@163.com
