# 基于Django开发的题库系统

## 项目概述

本项目是一个集成 Django、Elasticsearch 和 Redis 的 Web 应用，使用 Jazzmin 作为管理后台主题。主要功能包括数据导入、搜索和管理功能。

## 功能特性

- ✅ 数据导入（支持 JSON 和 Excel 格式）
- 🔍 Elasticsearch 全文搜索
- 🏷️ Redis 缓存和唯一 ID 生成
- 🎨 Jazzmin 现代化管理界面
- 🔄 自动字段映射和验证
- 📊 数据批量处理

## 技术栈

| 技术          | 版本   | 用途           |
| ------------- | ------ | -------------- |
| Python        | 3.9.17 | 后端编程语言   |
| Django        | 4.2    | Web 框架       |
| Elasticsearch | 8.x    | 搜索和数据存储 |
| Redis         | 6.x    | 缓存和ID生成   |
| Jazzmin       | 3.0.1  | 管理后台主题   |
| Pandas        | latest | Excel 文件处理 |

## 安装指南

### 前置条件

- Python 3.9.17
- Redis 服务器
- Elasticsearch 8.x
- Node.js (可选，前端开发)

### 安装步骤

克隆仓库：

```bash
git https://github.com/hack-scan/question_bank.git
cd question_bank
```

快速启动:

```sh
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate     # Windows
pip install -r requirements.txt
python manage.py collectstatic  #收集静态文件
python manage.py runserver
```

访问:

```bash
http://127.0.0.1:8000/
```

目录结构：

``` python
djangoProject/
├── core/               # 核心功能
│   ├── utils.py        # 工具函数
│   └── services.py     # 服务类
├── index/              # 主应用
│   ├── models.py       # 数据模型
│   ├── views           # 视图文件夹
│   └── admin.py        # 管理配置
├── static/             # 静态文件
├── staticfiles/        # 静态文件
├── templates/          # 模板文件
├── manage.py           # Django 管理脚本
└── settings.py         # 项目配置
```



# 功能演示

## **上传题库**

<img src="https://fastly.jsdelivr.net/gh/hack-scan/Blog-pic/posts/202505260952932.gif" alt="May-26-2025 09-52-30" style="zoom:67%;" />

## 题目查询

<img src="https://fastly.jsdelivr.net/gh/hack-scan/Blog-pic/posts/202505261042851.gif" alt="May-26-2025 10-42-41" style="zoom: 67%;" />



