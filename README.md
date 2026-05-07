# 飞书课程报告自动生成系统

## 功能说明
从飞书多维表格读取课程数据，自动生成精美的HTML课后学习报告，并回填报告链接到飞书表格。

## 系统架构
```
飞书表格 → GitHub Actions → 生成HTML → GitHub Pages → 回填链接到飞书
```

## 文件说明
- `generate.py` - 从飞书读取数据生成HTML报告
- `generate_report_links.py` - 回填报告链接到飞书表格
- `worker.js` - Cloudflare Worker触发器（可选）
- `.github/workflows/generate.yml` - GitHub Actions自动化工作流

## 部署步骤

### 1. GitHub仓库配置
在 Settings → Secrets and variables → Actions 中添加：
- `FEISHU_APP_ID` = `cli_a971a71ab0395cce`
- `FEISHU_APP_SECRET` = `T94yU3Og4QHiWxqmw4DNreSCipBmlJf7`

### 2. 启用GitHub Pages
Settings → Pages → Source 选择 `gh-pages` 分支

### 3. 触发方式

#### 方式一：定时自动生成（当前配置）
- 每15分钟自动检查并生成报告
- **注意**：GitHub可能需要仓库有活跃提交才会执行scheduled workflows
- 如果定时任务未运行，需要在Actions页面手动触发一次来激活

#### 方式二：手动触发
访问 Actions → Generate Reports → Run workflow

#### 方式三：飞书按钮触发（推荐）
1. 部署 `worker.js` 到Cloudflare Workers
2. 在飞书表格添加按钮字段，URL指向Worker地址
3. 点击按钮即时生成报告

## 定时任务不运行的解决方法

如果发现新增飞书内容后15分钟内没有自动生成报告链接：

### 检查清单
1. **确认Actions已启用**
   - 访问 https://github.com/wwzz168/kechengbaogao/settings/actions
   - 确保 "Actions permissions" 设置为 "Allow all actions"

2. **手动触发一次激活定时任务**
   - 访问 https://github.com/wwzz168/kechengbaogao/actions
   - 点击 "Generate Reports" → "Run workflow" → "Run workflow"
   - 等待运行完成后，定时任务应该会被激活

3. **检查仓库活跃度**
   - GitHub会禁用60天无提交的仓库的scheduled workflows
   - 解决方法：定期手动触发或使用repository_dispatch方式

4. **查看Actions运行日志**
   - 访问 https://github.com/wwzz168/kechengbaogao/actions
   - 查看是否有失败的运行记录
   - 点击查看详细日志排查问题

### 推荐方案：使用Cloudflare Worker即时触发
定时任务有延迟且不可靠，建议改用飞书按钮 + Cloudflare Worker方式：
- 填写完课程数据后点击"生成报告"按钮
- 即时触发GitHub Actions生成报告
- 10-20秒内完成，无需等待

## 本地测试
```bash
# 测试生成HTML报告
python generate.py

# 测试回填链接
python generate_report_links.py
```

## 报告访问地址
https://wwzz168.github.io/kechengbaogao/{record_id}.html
