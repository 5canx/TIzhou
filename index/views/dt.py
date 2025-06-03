#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Project : djangoProject
@File    : dt.py
@Author  : scan (https://github.com/hack-scan)
@Time    : 2025/6/1 13:58
"""
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")
index_name = "questions"

# 删除旧索引（如果存在）
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)
    print(f"已删除索引: {index_name}")

def generate_field_mappings(excel_columns):
    field_mappings = {
        "题目编号": "question_id",
        "题目": "content",
        "题目内容": "content",
        "题型": "question_type",
        "难度": "difficulty",
        "答案": "answer"
    }

    for i in range(5):
        option_label = f"选项{chr(65 + i)}"  # 选项A、选项B ...
        content_key = f"{option_label}内容"
        image_key = f"{option_label}图片"  # 假设Excel里存图片路径的列叫这个名

        # 映射选项文本字段
        if option_label in excel_columns or content_key in excel_columns or image_key in excel_columns:
            # 这里不映射 label 字段，label由代码赋值 A,B,C,D,E
            if content_key in excel_columns:
                field_mappings[content_key] = f"options.{i}.text"
            elif option_label in excel_columns:
                field_mappings[option_label] = f"options.{i}.text"

            if image_key in excel_columns:
                field_mappings[image_key] = f"options.{i}.image"

    return field_mappings

# 假设 Excel 有这些列
excel_columns = ['题目', '答案', '选项A', '选项B', '选项C', '选项A图片', '选项B图片', '题型']
FIELD_MAPPINGS = generate_field_mappings(excel_columns)
print("字段映射字典已生成：", FIELD_MAPPINGS)

mappings = {
    "dynamic": False,
    "properties": {
        "question_id": {"type": "keyword"},
        "content": {
            "type": "text",
            "fields": {
                "keyword": {"type": "keyword"}
            }
        },
        "question_type": {"type": "keyword"},
        "options": {
            "type": "nested",
            "properties": {
                "label": {"type": "keyword"},
                "text": {"type": "text"},
                "image": {"type": "keyword"}  # 图片路径字符串
            }
        },
        "answer": {"type": "keyword"},
        "difficulty": {"type": "keyword"},
        "ingest_time": {"type": "date"}
    }
}

if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name, mappings=mappings)
    print(f"索引 {index_name} 创建完成，已启用 content.keyword 精确匹配。")
else:
    print(f"索引 {index_name} 已存在，跳过创建。")
