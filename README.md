# TIzhou 题库管理系统

## 项目概述
这是一个基于Django的题库管理系统，支持题目上传、搜索和管理功能。

## 优化后的目录结构

```
TIzhou/
├── manage.py
├── requirements.txt
├── README.md
├── .env.example                    # 环境变量示例
├── .gitignore
├── djangoProject/                  # Django项目配置
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                # 基础配置
│   │   ├── development.py         # 开发环境配置
│   │   └── production.py          # 生产环境配置
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/                          # 应用目录
│   ├── __init__.py
│   ├── core/                      # 核心功能
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── admin.py
│   │   └── migrations/
│   ├── questions/                 # 题目管理
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── admin.py
│   │   ├── services.py           # 业务逻辑层
│   │   ├── serializers.py        # 序列化器
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   ├── api.py           # API视图
│   │   │   └── pages.py         # 页面视图
│   │   └── migrations/
│   ├── upload/                    # 文件上传
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── services.py
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   └── pages.py
│   │   └── migrations/
│   └── search/                    # 搜索功能
│       ├── __init__.py
│       ├── apps.py
│       ├── services.py
│       ├── views/
│       │   ├── __init__.py
│       │   └── api.py
│       └── migrations/
├── utils/                         # 工具模块
│   ├── __init__.py
│   ├── database.py               # 数据库连接
│   ├── elasticsearch_utils.py    # ES工具
│   ├── file_handlers.py          # 文件处理
│   └── validators.py             # 数据验证
├── static/                        # 静态文件
│   ├── css/
│   ├── js/
│   └── images/
├── templates/                     # 模板文件
│   ├── base.html
│   ├── admin/
│   ├── questions/
│   ├── upload/
│   └── search/
├── media/                         # 媒体文件
├── logs/                          # 日志文件
└── docs/                          # 文档
    ├── api.md
    └── deployment.md
```

## 主要优化点

### 1. 应用拆分
- **core**: 核心功能和通用模型
- **questions**: 题目管理相关功能
- **upload**: 文件上传功能
- **search**: 搜索功能

### 2. 分层架构
- **Views层**: 只负责HTTP请求处理
- **Services层**: 业务逻辑处理
- **Utils层**: 工具函数和通用功能

### 3. 配置管理
- 分离开发和生产环境配置
- 使用环境变量管理敏感信息

### 4. 静态文件优化
- 统一静态文件管理
- 按功能模块组织模板

## 迁移步骤

1. 创建新的应用结构
2. 迁移现有代码到对应模块
3. 更新URL配置
4. 测试功能完整性
5. 清理冗余文件

## 开发规范

### 代码组织
- 每个应用职责单一
- 视图文件按功能分类
- 业务逻辑放在services层

### 命名规范
- 文件名使用小写字母和下划线
- 类名使用驼峰命名
- 常量使用大写字母

### 配置管理
- 敏感信息使用环境变量
- 不同环境使用不同配置文件
- 配置项要有注释说明

