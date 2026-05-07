# 飞书课程报告生成服务 - 服务器部署指南

## 方案对比

| 特性 | GitHub Actions | 公司服务器 |
|------|---------------|-----------|
| 部署难度 | 简单 | 中等 |
| 可靠性 | 中等（定时任务可能被禁用） | 高 |
| 响应速度 | 15分钟延迟 | 实时/可自定义 |
| 维护成本 | 低 | 中等 |
| 数据安全 | 依赖GitHub | 完全可控 |
| 适用场景 | 个人项目、低频更新 | 企业应用、高频更新 |

## 服务器部署步骤

### 1. 环境准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和依赖
sudo apt install python3 python3-pip nginx -y

# 安装Python包
pip3 install flask requests gunicorn
```

### 2. 部署代码

```bash
# 创建部署目录
sudo mkdir -p /var/www/kechengbaogao
cd /var/www/kechengbaogao

# 克隆代码（或直接上传文件）
git clone https://github.com/wwzz168/kechengbaogao.git .

# 或者手动上传以下文件：
# - server.py
# - generate.py
# - generate_report_links.py
# - requirements.txt

# 安装依赖
pip3 install -r requirements.txt

# 设置权限
sudo chown -R www-data:www-data /var/www/kechengbaogao
sudo chmod +x server.py
```

### 3. 配置环境变量

```bash
# 方式一：在systemd服务中配置（推荐）
# 见下方systemd配置

# 方式二：创建.env文件
cat > /var/www/kechengbaogao/.env << EOF
FEISHU_APP_ID=cli_a971a71ab0395cce
FEISHU_APP_SECRET=T94yU3Og4QHiWxqmw4DNreSCipBmlJf7
EOF
```

### 4. 配置systemd服务

```bash
# 复制服务文件
sudo cp kechengbaogao.service /etc/systemd/system/

# 编辑服务文件，修改路径和用户
sudo nano /etc/systemd/system/kechengbaogao.service

# 重载systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start kechengbaogao

# 设置开机自启
sudo systemctl enable kechengbaogao

# 查看服务状态
sudo systemctl status kechengbaogao

# 查看日志
sudo journalctl -u kechengbaogao -f
```

### 5. 配置Nginx反向代理

```bash
# 复制nginx配置
sudo cp nginx.conf /etc/nginx/sites-available/kechengbaogao

# 修改域名
sudo nano /etc/nginx/sites-available/kechengbaogao
# 将 your-domain.com 改为实际域名或IP

# 创建软链接
sudo ln -s /etc/nginx/sites-available/kechengbaogao /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启nginx
sudo systemctl restart nginx
```

### 6. 配置防火墙（如果需要）

```bash
# 允许HTTP访问
sudo ufw allow 80/tcp

# 允许HTTPS访问（如果配置了SSL）
sudo ufw allow 443/tcp

# 重载防火墙
sudo ufw reload
```

## 服务使用

### 访问地址

- **管理界面**: `http://your-domain.com/`
- **API接口**: `http://your-domain.com/api/`
- **报告访问**: `http://your-domain.com/reports/{record_id}.html`

### API接口

#### 1. 手动触发生成
```bash
curl -X POST http://your-domain.com/api/generate
```

#### 2. 查看生成状态
```bash
curl http://your-domain.com/api/status
```

#### 3. 访问报告
```bash
curl http://your-domain.com/reports/rec27lwCjfCIjs.html
```

### 飞书集成

#### 方式一：使用飞书按钮（推荐）

1. 在飞书多维表格添加"按钮"字段
2. 配置按钮URL为：`http://your-domain.com/api/generate`
3. 点击按钮即可触发生成

#### 方式二：使用飞书webhook

修改 `generate_report_links.py`，在更新链接时回填报告URL：
```python
report_link = f"http://your-domain.com/reports/{record_id}.html"
```

## 服务管理命令

```bash
# 启动服务
sudo systemctl start kechengbaogao

# 停止服务
sudo systemctl stop kechengbaogao

# 重启服务
sudo systemctl restart kechengbaogao

# 查看状态
sudo systemctl status kechengbaogao

# 查看实时日志
sudo journalctl -u kechengbaogao -f

# 查看最近100行日志
sudo journalctl -u kechengbaogao -n 100
```

## 故障排查

### 1. 服务无法启动

```bash
# 查看详细错误日志
sudo journalctl -u kechengbaogao -xe

# 检查Python路径
which python3

# 检查文件权限
ls -la /var/www/kechengbaogao/

# 手动运行测试
cd /var/www/kechengbaogao
python3 server.py
```

### 2. 报告生成失败

```bash
# 手动测试生成脚本
cd /var/www/kechengbaogao
python3 generate.py

# 检查飞书API连接
python3 generate_report_links.py

# 查看reports目录权限
ls -la reports/
```

### 3. Nginx 502错误

```bash
# 检查Flask服务是否运行
sudo systemctl status kechengbaogao

# 检查端口占用
sudo netstat -tlnp | grep 5000

# 查看nginx错误日志
sudo tail -f /var/log/nginx/kechengbaogao_error.log
```

## 性能优化

### 1. 使用Gunicorn（生产环境推荐）

修改 `kechengbaogao.service`：
```ini
ExecStart=/usr/local/bin/gunicorn -w 4 -b 127.0.0.1:5000 server:app
```

### 2. 配置日志轮转

```bash
sudo nano /etc/logrotate.d/kechengbaogao
```

内容：
```
/var/log/nginx/kechengbaogao_*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
    endscript
}
```

### 3. 配置SSL证书（可选）

```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx -y

# 自动配置SSL
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

## 监控和告警

### 1. 添加健康检查接口

在 `server.py` 中添加：
```python
@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})
```

### 2. 配置监控脚本

```bash
# 创建监控脚本
cat > /usr/local/bin/check_kechengbaogao.sh << 'EOF'
#!/bin/bash
if ! curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "Service is down, restarting..."
    systemctl restart kechengbaogao
fi
EOF

chmod +x /usr/local/bin/check_kechengbaogao.sh

# 添加到crontab（每5分钟检查一次）
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/check_kechengbaogao.sh") | crontab -
```

## 备份策略

```bash
# 创建备份脚本
cat > /usr/local/bin/backup_reports.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/kechengbaogao"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/reports_$DATE.tar.gz /var/www/kechengbaogao/reports/

# 保留最近7天的备份
find $BACKUP_DIR -name "reports_*.tar.gz" -mtime +7 -delete
EOF

chmod +x /usr/local/bin/backup_reports.sh

# 每天凌晨2点备份
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup_reports.sh") | crontab -
```

## 总结

服务器部署的优势：
- ✅ 完全可控，不依赖第三方服务
- ✅ 实时响应，无延迟
- ✅ 可自定义定时频率
- ✅ 数据安全，内网部署
- ✅ 易于监控和维护

推荐用于企业生产环境。
