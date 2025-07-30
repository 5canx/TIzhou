# API文档

## 搜索API

### 根据ID搜索题目
- **URL**: `/api/search/id/`
- **方法**: POST
- **参数**: `{"id": "题目ID"}`

### 根据内容搜索题目
- **URL**: `/api/search/content/`
- **方法**: POST
- **参数**: `{"content": "搜索关键词", "size": 10, "from": 0}`

### 列出所有题目
- **URL**: `/api/search/all/`
- **方法**: GET
- **参数**: `size=100&from=0`

## 上传API

### 上传题目文件
- **URL**: `/api/upload/file/`
- **方法**: POST
- **参数**: 文件表单数据

### 上传图片文件
- **URL**: `/api/upload/images/`
- **方法**: POST
- **参数**: ZIP文件表单数据
