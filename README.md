# 本地知识库系统

[![Python](https://img.shields.io/badge/Python-3.10.10-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📚 项目简介

一个基于Python的**本地知识库系统**，支持文档和代码的智能检索与问答。用户可以上传各种类型的文件，系统自动建立向量索引，通过集成的AI模型进行自然语言查询。

### ✨ 核心特性

- 📁 **智能文件管理** - 支持文档和代码文件批量上传
- 🔍 **向量检索** - 基于FAISS/Chroma的高效语义搜索
- 💬 **AI问答** - 集成开源大模型，支持本地部署
- ⚡ **自动索引** - 文件上传后自动建立向量索引
- 🖥️ **友好界面** - Streamlit构建的现代Web界面
- 📊 **实时反馈** - 索引进度和文件状态实时显示
- 🔗 **来源追踪** - 回答问题时显示相关文档来源

## 🚀 快速开始

### 系统要求

- **Python**: 3.10.10
- **内存**: 8GB 以上推荐
- **存储**: 10GB 以上自由空间
- **操作系统**: Windows / Linux / macOS

### 一键启动

#### Windows
```bash
start_all.bat
```

#### Linux / macOS
```bash
chmod +x start_all.sh
./start_all.sh
```

脚本将自动：
1. ✓ 创建虚拟环境
2. ✓ 安装所有依赖
3. ✓ 启动后端服务
4. ✓ 启动前端应用
5. ✓ 打开浏览器

### 访问应用

- **前端**: http://localhost:8501
- **API文档**: http://localhost:8000/docs

## 📖 使用指南

### 1. 上传文件

在"文件管理"页面：
1. 点击"选择文件或文件夹"
2. 选择要上传的文件
3. 点击"开始上传"

**支持的文件类型:**
- 📄 文档: .txt, .pdf, .docx, .md, .html
- 💻 代码: .py, .js, .java, .cpp, .go, .rs, .ts等

### 2. 查看索引状态

文件上传后，系统自动建立向量索引。在文件列表中可以看到：
- ✅ 已索引
- ⏳ 索引中
- ❌ 失败
- ⚪ 未索引

### 3. 提问查询

在"智能问答"页面：
1. 输入您的问题
2. 系统从已索引的文件中检索相关内容
3. AI模型基于检索结果生成答案
4. 答案会显示参考文档来源

### 4. 管理文件

- **删除文件**: 选中文件后点击删除，索引也会自动清除
- **批量操作**: 支持多文件同时删除
- **查看详情**: 点击文件名查看文件元信息

## 🛠️ 项目结构

```
knowledge-base/
├── backend/                    # 后端代码 (FastAPI)
│   ├── main.py                # 应用入口
│   ├── config.py              # 配置管理
│   ├── logger_config.py       # 日志配置
│   ├── routers/               # API路由 (待实现)
│   ├── services/              # 业务逻辑 (待实现)
│   └── models/                # 数据模型 (待实现)
├── frontend/                  # 前端代码 (Streamlit)
│   └── app.py                 # 应用界面
├── data/                      # 数据存储
│   ├── documents/             # 上传的文档
│   └── code/                  # 上传的代码
├── indexes/                   # 向量索引存储
├── logs/                      # 应用日志
├── config/                    # 配置文件
├── requirements.txt           # 依赖列表
├── .env.example               # 环境变量示例
├── start_backend.bat          # 后端启动脚本 (Windows)
├── start_backend.sh           # 后端启动脚本 (Linux/macOS)
├── start_frontend.bat         # 前端启动脚本 (Windows)
├── start_frontend.sh          # 前端启动脚本 (Linux/macOS)
├── start_all.bat              # 一键启动 (Windows)
├── start_all.sh               # 一键启动 (Linux/macOS)
├── INSTALL.md                 # 安装指南
├── README.md                  # 项目说明 (本文件)
├── 需求文档.txt                # 原始需求
├── 本地知识库系统需求文档.md    # 详细需求
└── 计划任务.md                 # 开发计划
```

## 📋 开发计划

项目分为7个阶段实现，详见 [计划任务.md](计划任务.md)

| Phase | 任务 | 状态 |
|-------|------|------|
| Phase 1 | 框架搭建 | ✅ 进行中 |
| Phase 2 | 文件管理 | ⏳ 计划中 |
| Phase 3 | 索引系统 | ⏳ 计划中 |
| Phase 4 | AI问答 | ⏳ 计划中 |
| Phase 5 | 启动脚本 | ✅ 完成 |
| Phase 6 | 测试优化 | ⏳ 计划中 |
| Phase 7 | 文档发布 | ⏳ 计划中 |

## 🔧 配置说明

### 环境变量

复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

主要配置项：

```ini
# 应用配置
DEBUG=True
LOG_LEVEL=INFO

# 服务器配置
HOST=0.0.0.0
PORT=8000

# 模型配置
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
LLM_MODEL_NAME=chatglm-6b
EMBEDDING_DEVICE=cpu  # 改为 cuda 如果有GPU

# 检索配置
RETRIEVAL_K=3
SIMILARITY_THRESHOLD=0.5
```

## 📦 技术栈

### 后端
- **框架**: FastAPI
- **Server**: Uvicorn
- **日志**: Loguru
- **验证**: Pydantic

### 前端
- **框架**: Streamlit
- **组件**: Streamlit-chat

### 向量化与检索
- **向量数据库**: Chroma / FAISS
- **嵌入模型**: Sentence-Transformers
- **文本处理**: LangChain (规划)

### AI模型
- **推荐模型**: ChatGLM-6B / Qwen-7B
- **框架**: Transformers / Accelerate
- **推理**: ONNX (规划)

### 文件处理
- **PDF**: PyMuPDF (fitz)
- **Word**: python-docx
- **HTML**: BeautifulSoup4
- **Markdown**: markdown

## 🎯 性能目标

| 指标 | 目标 | 状态 |
|------|------|------|
| 文件上传响应 | < 5秒 | 待测试 |
| 索引创建速度 | > 1000字符/秒 | 待测试 |
| 问答响应时间 | < 10秒 | 待测试 |
| 并发用户支持 | 10+ | 待测试 |

## 🐛 常见问题

### Q: 如何更改端口？
A: 编辑 `backend/config.py` 中的 `PORT` 参数，或修改前端启动脚本中的 `--server.port`

### Q: 如何使用GPU加速？
A: 在 `.env` 中将 `EMBEDDING_DEVICE` 和 `LLM_DEVICE` 改为 `cuda`，并确保已安装CUDA

### Q: 支持哪些AI模型？
A: 支持任何Hugging Face模型，推荐使用ChatGLM-6B或Qwen-7B等中文优化模型

### Q: 如何添加更多支持的文件类型？
A: 修改 `backend/config.py` 中的 `ALLOWED_DOCUMENT_TYPES` 或 `ALLOWED_CODE_TYPES`

## 📚 更多资源

- [安装指南](INSTALL.md) - 详细安装步骤
- [计划任务](计划任务.md) - 开发路线图
- [API文档](http://localhost:8000/docs) - 交互式API文档

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 联系方式

- 提交Issue: GitHub Issues
- 电子邮件: contact@example.com

---

**版本**: v1.0.0  
**最后更新**: 2026年1月  
**状态**: Phase 1 进行中 ✅
