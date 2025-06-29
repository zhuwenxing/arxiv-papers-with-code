# ArXiv Paper Fetcher - 获取带开源代码的论文

这个Python项目用于从ArXiv获取信息检索(Information Retrieval)和数据库(Database)分类中包含开源代码的论文。

## 功能特点

- 自动搜索ArXiv上的IR和DB分类论文
- 智能识别论文中的代码链接（GitHub、GitLab等）
- 支持检查论文页面以发现更多代码链接
- 输出JSON和CSV格式的结果
- 可配置搜索参数（时间范围、结果数量等）

## 安装

1. 克隆或下载项目到本地
2. 进入项目目录：
```bash
cd arxiv_paper_fetcher
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### 基本使用

获取最近30天内的所有带代码的IR和DB论文：
```bash
python main.py
```

### 高级选项

```bash
# 只搜索信息检索类论文
python main.py --categories information_retrieval

# 只搜索数据库类论文
python main.py --categories databases

# 搜索两个分类
python main.py --categories information_retrieval databases

# 设置每个分类的最大结果数（默认100）
python main.py --max-results 200

# 设置时间范围（默认30天）
python main.py --days-back 60

# 只输出JSON格式
python main.py --output-format json

# 只输出CSV格式
python main.py --output-format csv

# 指定输出目录
python main.py --output-dir /path/to/output
```

### 命令行参数说明

- `--categories`: 要搜索的分类，可选 'information_retrieval' 和/或 'databases'
- `--max-results`: 每个分类的最大结果数（默认：100）
- `--days-back`: 搜索最近多少天的论文（默认：30）
- `--output-format`: 输出格式，可选 'json'、'csv' 或 'both'（默认：both）
- `--check-pages`: 是否检查论文页面以找到更多代码链接（默认：True）
- `--output-dir`: 输出文件保存目录（默认：data）

## 输出格式

### JSON格式
包含以下字段：
- title: 论文标题
- authors: 作者列表
- published: 发布日期
- arxiv_id: ArXiv ID
- url: ArXiv链接
- pdf_url: PDF下载链接
- category: 搜索分类
- primary_category: 主要分类
- abstract: 摘要
- code_links: 代码链接列表
- comment: 备注信息

### CSV格式
与JSON格式相同的字段，其中code_links用分号分隔。

## 项目结构

```
arxiv_paper_fetcher/
├── src/
│   └── arxiv_client.py    # ArXiv API客户端
├── data/                  # 输出数据目录
├── config/                # 配置文件目录
├── main.py               # 主程序
├── requirements.txt      # 依赖包列表
└── README.md            # 本文档
```

## 注意事项

1. 程序会自动限制请求频率，避免对ArXiv服务器造成压力
2. 检查论文页面功能会增加运行时间，但能发现更多代码链接
3. 结果按发布时间降序排列（最新的在前）

## 示例输出

运行后会在控制台显示：
- 搜索进度
- 找到的带代码论文信息
- 统计摘要（总数、分类分布、GitHub链接数等）
- 前5篇论文的详细信息

## GitHub Actions 自动化

本项目配置了GitHub Actions来每天自动运行并发布到GitHub Pages：

### 功能特点
- 每天UTC时间00:00自动运行
- 获取最近30天的论文数据
- 自动生成网页并发布到GitHub Pages
- 支持手动触发工作流

### 设置步骤

1. **Fork或上传项目到GitHub**

2. **启用GitHub Pages**
   - 进入仓库Settings
   - 找到Pages部分
   - Source选择"GitHub Actions"

3. **工作流会自动**：
   - 每天获取新论文
   - 生成HTML网页
   - 发布到 `https://[你的用户名].github.io/[仓库名]/`

### 手动触发
在GitHub仓库的Actions标签页中，可以手动触发"Daily Paper Fetch and Publish"工作流。

### 网页功能
- 展示所有收集的论文
- 支持按分类筛选（IR/DB）
- 支持搜索功能
- 显示统计信息
- 响应式设计，支持移动端