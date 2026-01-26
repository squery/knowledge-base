# 部署指南

本指南将帮助您在不同环境下部署本地知识库系统。

---

## 📋 目录

- [系统要求](#系统要求)
- [本地开发部署](#本地开发部署)
- [生产环境部署](#生产环境部署)
- [Docker部署](#docker部署)
- [云服务器部署](#云服务器部署)
- [性能优化](#性能优化)
- [监控和日志](#监控和日志)

---

## 系统要求

### 最低配置
- **CPU**: 4核心
- **内存**: 8GB RAM
- **存储**: 20GB 可用空间
- **Python**: 3.10+
- **操作系统**: Windows 10/11, Ubuntu 20.04+, macOS 10.15+

### 推荐配置
- **CPU**: 8核心
- **内存**: 16GB RAM
- **存储**: 50GB SSD
- **GPU**: NVIDIA GPU (可选，用于加速)
- **Python**: 3.10.10

---

## 本地开发部署

### 1. 克隆项目

```bash
git clone https://github.com/your-repo/knowledge-base.git
cd knowledge-base
```

### 2. 创建虚拟环境

**Windows**:
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS**:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

**选择环境版本**:

```bash
# Pydantic 2.x + Chromadb 0.5+ (推荐)
pip install -r requirements_v2.txt

# 或 Pydantic 1.x + Chromadb 0.4
pip install -r requirements_v1.txt
```

### 4. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置
nano .env
```

### 5. 启动服务

**一键启动**:
```bash
# Windows
start_all.bat

# Linux/macOS
chmod +x start_all.sh
./start_all.sh
```

**分别启动**:
```bash
# 启动后端
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# 启动前端（新终端）
streamlit run frontend/app.py --server.port 8501
```

### 6. 验证部署

访问以下地址确认服务正常：
- 前端: http://localhost:8501
- 后端API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

---

## 生产环境部署

### 1. 使用 Supervisor 管理进程

**安装 Supervisor**:
```bash
sudo apt-get install supervisor
```

**配置文件** (`/etc/supervisor/conf.d/knowledge-base.conf`):
```ini
[program:knowledge-base-backend]
command=/path/to/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
directory=/path/to/knowledge-base
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/knowledge-base/backend.err.log
stdout_logfile=/var/log/knowledge-base/backend.out.log

[program:knowledge-base-frontend]
command=/path/to/venv/bin/streamlit run frontend/app.py --server.port 8501
directory=/path/to/knowledge-base
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/knowledge-base/frontend.err.log
stdout_logfile=/var/log/knowledge-base/frontend.out.log
```

**启动服务**:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

### 2. 使用 Nginx 反向代理

**安装 Nginx**:
```bash
sudo apt-get install nginx
```

**配置文件** (`/etc/nginx/sites-available/knowledge-base`):
```nginx
upstream backend {
    server 127.0.0.1:8000;
}

upstream frontend {
    server 127.0.0.1:8501;
}

server {
    listen 80;
    server_name your-domain.com;

    # 前端
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 后端API
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # API文档
    location /docs {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }

    # 文件上传限制
    client_max_body_size 100M;
}
```

**启用配置**:
```bash
sudo ln -s /etc/nginx/sites-available/knowledge-base /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. 配置 SSL (可选)

使用 Let's Encrypt:
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## Docker部署

### 1. 创建 Dockerfile (后端)

**backend/Dockerfile**:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements_v2.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements_v2.txt

# 复制应用代码
COPY backend/ ./backend/
COPY .env .env

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. 创建 Dockerfile (前端)

**frontend/Dockerfile**:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements_v2.txt .
RUN pip install --no-cache-dir -r requirements_v2.txt

# 复制前端代码
COPY frontend/ ./frontend/

# 暴露端口
EXPOSE 8501

# 启动命令
CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 3. 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./indexes:/app/indexes
      - ./logs:/app/logs
    environment:
      - DEBUG=False
      - LOG_LEVEL=INFO
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    ports:
      - "8501:8501"
    depends_on:
      - backend
    environment:
      - BACKEND_URL=http://backend:8000
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  data:
  indexes:
  logs:
```

### 4. 启动容器

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 云服务器部署

### AWS EC2

**1. 创建实例**:
- AMI: Ubuntu 22.04 LTS
- 实例类型: t3.large (推荐)
- 存储: 50GB EBS

**2. 安全组配置**:
- 开放端口: 80, 443, 8000, 8501

**3. 部署步骤**:
```bash
# 连接实例
ssh -i your-key.pem ubuntu@your-ec2-ip

# 更新系统
sudo apt-get update && sudo apt-get upgrade -y

# 安装依赖
sudo apt-get install python3-pip python3-venv git -y

# 按照本地部署步骤继续...
```

### Azure VM

类似AWS EC2，选择适当的VM大小（Standard_B2ms或更高）。

### Google Cloud Platform

使用Compute Engine，选择e2-medium或更高配置。

---

## 性能优化

### 1. 后端优化

**使用Gunicorn + Uvicorn Workers**:
```bash
pip install gunicorn

gunicorn backend.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

**配置文件** (gunicorn.conf.py):
```python
workers = 4
worker_class = 'uvicorn.workers.UvicornWorker'
bind = '0.0.0.0:8000'
timeout = 120
keepalive = 5
accesslog = 'logs/access.log'
errorlog = 'logs/error.log'
```

### 2. 缓存优化

**Redis缓存**:
```bash
# 安装Redis
sudo apt-get install redis-server

# 配置Redis
pip install redis
```

### 3. 数据库优化

- 定期清理日志文件
- 优化SQLite配置
- 考虑迁移到PostgreSQL（大规模部署）

### 4. GPU加速

如果有NVIDIA GPU:
```bash
# 安装CUDA
# 参考: https://developer.nvidia.com/cuda-downloads

# 安装PyTorch GPU版本
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 修改.env
EMBEDDING_DEVICE=cuda
LLM_DEVICE=cuda
```

---

## 监控和日志

### 1. 应用日志

日志文件位置:
- `logs/app.log` - 应用主日志
- `logs/error.log` - 错误日志
- `logs/access.log` - 访问日志

### 2. 系统监控

**安装监控工具**:
```bash
# 安装 Prometheus + Grafana
docker run -d -p 9090:9090 prom/prometheus
docker run -d -p 3000:3000 grafana/grafana
```

### 3. 日志轮转

**logrotate 配置** (`/etc/logrotate.d/knowledge-base`):
```
/path/to/knowledge-base/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        supervisorctl restart knowledge-base-backend
    endscript
}
```

---

## 备份策略

### 1. 数据备份

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/knowledge-base"
DATE=$(date +%Y%m%d_%H%M%S)

# 备份数据库
cp data/database.db $BACKUP_DIR/db_$DATE.db

# 备份索引
tar -czf $BACKUP_DIR/indexes_$DATE.tar.gz indexes/

# 备份文件
tar -czf $BACKUP_DIR/documents_$DATE.tar.gz data/documents/

# 清理旧备份（保留7天）
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

### 2. 定时备份

```bash
# 添加到crontab
crontab -e

# 每天凌晨2点备份
0 2 * * * /path/to/backup.sh
```

---

## 故障恢复

### 1. 服务重启

```bash
# Supervisor
sudo supervisorctl restart all

# Docker
docker-compose restart

# 手动
pkill -f uvicorn
pkill -f streamlit
./start_all.sh
```

### 2. 数据恢复

```bash
# 恢复数据库
cp /backup/knowledge-base/db_20260126_020000.db data/database.db

# 恢复索引
tar -xzf /backup/knowledge-base/indexes_20260126_020000.tar.gz

# 重启服务
sudo supervisorctl restart all
```

---

## 安全建议

1. **防火墙配置**: 只开放必要端口
2. **定期更新**: 保持系统和依赖更新
3. **SSL/TLS**: 生产环境必须启用HTTPS
4. **访问控制**: 考虑添加认证机制
5. **日志审计**: 定期检查日志文件
6. **备份加密**: 敏感数据备份加密存储

---

## 常见问题

### Q: 如何扩展到多服务器？
A: 使用负载均衡器（如Nginx/HAProxy）+ 共享存储（NFS/S3）

### Q: 如何提高并发性能？
A: 增加worker数量，使用Redis缓存，优化数据库查询

### Q: 内存占用过高怎么办？
A: 减少worker数量，优化模型加载策略，使用模型量化

---

**最后更新**: 2026年1月26日  
**文档版本**: 1.0.0
