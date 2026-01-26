# 变更日志

所有项目版本更新都记录在此文件中。

---

## [1.0.0] - 2026-01-26

### 🎉 首个正式版本发布

#### ✨ 新增功能
- **智能文件管理**: 支持文档（txt/pdf/docx/md/html）和代码文件（py/js/java等）批量上传
- **向量索引系统**: 基于 Sentence-Transformers 和 Chroma 的自动向量化与索引
- **语义检索**: 支持高效的向量相似度检索与元数据过滤
- **RAG 问答系统**: 集成检索增强生成（Retrieval-Augmented Generation），支持模板与 LLM 生成两种模式
- **实时索引管理**: 支持索引状态查询、重建、删除、统计等操作
- **前端交互界面**: Streamlit 现代化 UI，包含文件管理、智能问答、索引管理、系统设置、用户文档等功能
- **API 接口**: 完整的 RESTful API，支持 FastAPI 交互式文档

#### 🔧 核心技术
- **后端**: FastAPI + SQLAlchemy + MySQL
- **前端**: Streamlit
- **向量化**: Sentence-Transformers（多语言嵌入模型）
- **向量库**: Chroma（持久化）
- **文本处理**: PyMuPDF、python-docx、BeautifulSoup4
- **日志**: Loguru（轮转与级别）
- **配置**: Pydantic Settings（v1/v2 双兼容）

#### 📊 性能指标（Phase 6 测试）
- **文件上传**: 3.4秒 / 文件
- **索引速度**: 1800+ 字符 / 秒
- **问答响应**: 2-4秒
- **功能测试**: 89% 通过率
- **用户体验**: 88% 满足度

#### 📚 完整文档
- README.md - 项目概述与快速开始
- INSTALL.md - 安装指南
- docs/USER_GUIDE.md - 用户使用指南
- docs/FAQ.md - 常见问题与解答
- docs/QUICKSTART.md - 5分钟快速上手
- docs/API_DOCUMENTATION.md - 完整 API 接口说明
- docs/DEPLOYMENT_GUIDE.md - 部署指南（本地/Docker/云环境）
- docs/CONFIGURATION.md - 配置详解
- docs/TROUBLESHOOTING.md - 故障排查指南
- docs/ARCHITECTURE.md - 系统架构设计
- docs/DATABASE_DESIGN.md - 数据库设计文档
- docs/MODULE_DESIGN.md - 模块设计文档
- docs/API_DESIGN_SUMMARY.md - API 设计概要
- docs/VIDEO_SCRIPT.md - 演示录制脚本
- docs/README.md - 文档中心导航

#### 🎯 已完成阶段
- **Phase 1**: 基础框架搭建 ✅
- **Phase 2**: 文件管理模块 ✅
- **Phase 3**: 索引系统实现 ✅
- **Phase 4**: AI 问答与优化 ✅
- **Phase 5**: 启动脚本与部署 ✅
- **Phase 6**: 测试与优化 ✅
- **Phase 7**: 文档完善与发布 ✅

#### 🔐 安全性
- CORS 配置（本地开发全开放，建议生产环保守）
- 文件上传校验（类型、大小、路径安全）
- 环境变量与敏感信息分离（.env.example）
- SQL 注入防护（ORM 参数化查询）
- 异常处理完整（统一错误响应格式）

#### 🚀 启动方式
```bash
# Windows
start_all.bat

# Linux/macOS
chmod +x start_all.sh
./start_all.sh
```

#### 📝 已知限制与改进方向
- LLM 增强默认关闭（USE_LLM_QA=False）以避免网络下载问题，可在配置中启用
- 支持本地模型加载或国内镜像源配置
- 未来计划：全文搜索、高级分析、鉴权、速率限制、Streaming 响应

#### 🙏 致谢
感谢 FastAPI、Streamlit、Chroma、Sentence-Transformers、SQLAlchemy、Loguru 等开源项目的支持。

---

## 版本规划

### 1.1.0 (规划中)
- 全文搜索支持
- API 鉴权（API Key/JWT）
- 速率限制与配额管理
- 流式问答（SSE/WebSocket）
- 性能优化（缓存、批量处理）

### 1.2.0 (规划中)
- 用户管理与多租户支持
- 高级分析与统计
- 自定义模型集成
- Web 端问答 Streaming
- 移动适配优化

---

**项目地址**: https://github.com/your-org/knowledge-base  
**许可证**: MIT  
**维护状态**: 🟢 主动开发中
