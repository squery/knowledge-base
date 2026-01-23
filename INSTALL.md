# 本地知识库系统 - 安装指南

## 系统要求

- **Python版本**: 3.10.10
- **操作系统**: Windows / Linux / macOS
- **内存**: 推荐 8GB 以上
- **存储**: 至少 10GB 自由空间

## 快速开始

### 1. 环境准备

#### Windows
```bash
# 克隆或下载项目
cd D:\Git Workspace\knowledge-base

# 运行一键启动脚本
start_all.bat
```

#### Linux / macOS
```bash
# 克隆或下载项目
cd ~/knowledge-base

# 给脚本执行权限
chmod +x start_backend.sh start_frontend.sh start_all.sh

# 运行一键启动脚本
./start_all.sh
```

### 2. 分别启动服务

如果一键启动失败，可以分别启动后端和前端：

#### 启动后端
**Windows:**
```bash
start_backend.bat
```

**Linux / macOS:**
```bash
./start_backend.sh
```

后端服务将在 `http://localhost:8000` 启动

#### 启动前端
**Windows:**
```bash
start_frontend.bat
```

**Linux / macOS:**
```bash
./start_frontend.sh
```

前端应用将在 `http://localhost:8501` 启动

### 3. 访问应用

- **前端应用**: http://localhost:8501
- **API文档**: http://localhost:8000/docs
- **API ReDoc**: http://localhost:8000/redoc

## 手动安装步骤

如果脚本启动失败，可以手动执行以下步骤：

### 1. 创建虚拟环境
```bash
python -m venv venv
```

### 2. 激活虚拟环境

**Windows:**
```bash
venv\Scripts\activate.bat
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 启动后端
```bash
python backend/main.py
```

### 5. 新开一个终端，启动前端
```bash
streamlit run frontend/app.py
```

## 常见问题

### Python版本过低
```bash
# 检查Python版本
python --version

# 需要3.9或更高版本
# 访问 https://www.python.org/downloads/ 下载安装
```

### 端口被占用

如果8000或8501端口被占用，可以修改配置：

编辑 `backend/config.py` 中的 `PORT` 参数或修改 `start_frontend.bat/.sh` 中的 `--server.port` 参数

### 依赖安装失败

可能是由于网络问题或包源问题：

```bash
# 使用清华源重新安装
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用阿里源
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 无法连接到API

确保后端已启动，且在 http://localhost:8000/health 能获到正常响应

```bash
# 测试后端健康状态
curl http://localhost:8000/health
```

## 配置文件

### 环境变量配置

复制 `.env.example` 为 `.env` 并根据需要修改：

```bash
cp .env.example .env
```

主要配置项：
- `HOST`: API服务主机地址 (默认: 0.0.0.0)
- `PORT`: API服务端口 (默认: 8000)
- `EMBEDDING_MODEL`: 嵌入模型 (默认: sentence-transformers模型)
- `LLM_MODEL_NAME`: 对话模型 (默认: chatglm-6b)
- `EMBEDDING_DEVICE`: 运算设备 (cpu或cuda)

## 项目结构

```
knowledge-base/
├── backend/                # 后端代码
│   ├── main.py            # FastAPI应用入口
│   ├── config.py          # 配置管理
│   └── logger_config.py   # 日志配置
├── frontend/              # 前端代码
│   └── app.py             # Streamlit应用
├── data/                  # 数据存储
│   ├── documents/         # 文档文件
│   └── code/              # 代码文件
├── indexes/               # 向量索引
├── logs/                  # 日志文件
├── requirements.txt       # 依赖列表
├── .env.example          # 环境变量示例
└── start_*.bat/sh         # 启动脚本
```

## 后续步骤

1. 根据 `计划任务.md` 实现Phase 2-7的功能
2. 在 `data/documents` 和 `data/code` 目录中放入要索引的文件
3. 通过前端界面上传文件并进行问答

## 获取帮助

如有问题，请参考：
- API文档: http://localhost:8000/docs
- 查看日志文件: `logs/` 目录
- 提交Issue或联系开发者

---

**版本**: v1.0.0  
**最后更新**: 2026年1月
