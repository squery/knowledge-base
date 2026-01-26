# 快速上手（5分钟）

版本: 1.0.0  
最后更新: 2026-01-26

---

## 1. 启动服务

### Windows
```bat
start_all.bat
```

### Linux/macOS
```bash
chmod +x start_all.sh
./start_all.sh
```

访问：
- 前端：http://localhost:8501
- API 文档：http://localhost:8000/docs

---

## 2. 上传与索引
1. 打开“文件管理”页，选择文件/文件夹
2. 点击“开始上传”并等待索引完成
3. 在列表中查看文件索引状态与详情

---

## 3. 智能问答
1. 打开“智能问答”页
2. 输入问题（例如：“这个系统做什么？”）
3. 查看答案与参考来源

---

## 4. 常用管理
- 删除文件：在“文件管理”页勾选后删除
- 重新索引：在“索引管理”页对指定文件重建
- 重建所有索引：清空向量库后全量重索引

---

## 5. API 快测

### 相似检索
```bash
curl -X POST "http://localhost:8000/api/index/search" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"人工智能是什么\", \"top_k\": 3}"
```

### 问答接口
```bash
curl -X POST "http://localhost:8000/api/qa/ask" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"如何上传文件？\", \"top_k\": 3}"
```

---

## 6. 更多文档
- 使用指南: `docs/USER_GUIDE.md`
- FAQ: `docs/FAQ.md`
- 部署指南: `docs/DEPLOYMENT_GUIDE.md`
- 配置说明: `docs/CONFIGURATION.md`
