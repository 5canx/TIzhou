# 基于Django开发的题库系统 1.2

## 项目概述

本项目是一个集成 Django、Elasticsearch 和 Redis 的 Web 应用，使用 Jazzmin 作为管理后台主题。主要功能包括数据导入、搜索和管理功能。

## 版权与使用限制

### 允许用途
✅ **本系统授权用于以下合法场景**：
- 学校教育及培训机构的教学活动
- 企业内部的员工培训与考核
- 个人非商业性学习使用
- 符合当地法律法规的学术研究

### 严格禁止
❌ **任何以下行为都将被视为违规**：
- 存储或传播违法、涉密内容
- 用于考试作弊等学术不端行为
- 对系统进行逆向工程或恶意攻击
- 未经授权的商业性使用
- 违反《网络安全法》《数据安全法》的行为

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

### 示例数据

https://github.com/hack-scan/TIzhou/blob/main/%E9%A2%98%E7%9B%AE%E4%B8%8E%E7%AD%94%E6%A1%88.xlsx

https://github.com/hack-scan/TIzhou/blob/main/%E5%9B%BE%E7%89%87.zip

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
python dt.py  #设置索引
python manage.py runserver
```

访问:

```bash
http://127.0.0.1:8000/upload/
http://127.0.0.1:8000/upload/images/page/
http://127.0.0.1:8000/search/
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

## XLSX文件题目图片上传（压缩包）

![Jun-03-2025 18-37-51](https://fastly.jsdelivr.net/gh/hack-scan/Blog-pic/posts/202506031838104.gif)



## 题目查询

<img src="https://fastly.jsdelivr.net/gh/hack-scan/Blog-pic/posts/202505261042851.gif" alt="May-26-2025 10-42-41" style="zoom: 67%;" />

<img src="https://fastly.jsdelivr.net/gh/hack-scan/Blog-pic/posts/202506031849890.gif" alt="Jun-03-2025 18-49-00" style="zoom:67%;" />

