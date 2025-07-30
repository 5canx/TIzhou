# 部署指南

## 环境要求
- Python 3.9+
- Redis 6.x
- Elasticsearch 8.x

## 安装步骤
1. 克隆项目
2. 创建虚拟环境
3. 安装依赖: `pip install -r requirements.txt`
4. 配置环境变量
5. 运行迁移: `python manage.py migrate`
6. 启动服务: `python manage.py runserver`

## 环境变量配置
复制 `env.example` 为 `.env` 并修改相应配置。
