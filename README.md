# TBox Computer Configuration MCP Server

TBox Computer Configuration 是一个基于 Model Context Protocol (MCP) 的服务，用于帮助用户根据预算和需求配置计算机硬件。

## 功能特点

- 根据预算推荐计算机配置
- 支持多种配置级别（基础、游戏、专业等）
- 提供详细的硬件规格和价格信息
- 可以根据特定用途优化配置（游戏、办公、设计等）

## 目录结构

```
tbox_computer/
├── config.py                 # 配置文件
├── mcp_server.py             # MCP服务器主文件
├── computer_configurator.py  # 计算机配置核心逻辑
├── llm_util.py               # LLM工具函数
├── render.py                 # 渲染工具
├── template/                 # 模板文件
│   └── template_config.html  # 配置模板
├── output/                   # 输出文件
│   └── output_config.html    # 生成的配置文件
└── json/                     # 硬件数据文件
    ├── cpu.json              # CPU数据
    ├── motherboard.json      # 主板数据
    ├── memory.json           # 内存数据
    └── video-card.json       # 显卡数据
```

## 使用方法

1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 配置环境变量:
```bash
cp .env.sample .env
# 编辑 .env 文件设置您的API密钥
```

3. 运行服务器:
```bash
python mcp_server.py
```

4. 服务器将在 `http://localhost:8000/mcp` 启动

## API 工具

- `generate_computer_config`: 根据预算和用途生成计算机配置
- `get_hardware_info`: 获取特定硬件的详细信息