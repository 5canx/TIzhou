#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Project : djangoProject
@File    : uploa1d.py
@Author  : scan (https://github.com/hack-scan)
@Time    : 2025/6/1 17:51
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import pandas as pd
from datetime import datetime
from elasticsearch import helpers
from .utils import rename_map, allowed_fields, get_question_id, es, index_name
import os
import shutil
from django.conf import settings
import re
# 处理 JSON 文件的函数
def handle_json_file(uploaded_file):
    content = uploaded_file.read().decode("utf-8")
    raw_data = json.loads(content)
    data_list = []

    if isinstance(raw_data, dict):
        raw_data = [raw_data]
    elif not isinstance(raw_data, list):
        raise ValueError("JSON 格式不正确")

    for item in raw_data:
        if isinstance(item, dict):
            mapped_item = {rename_map.get(k, k): v for k, v in item.items()}
            data_list.append(mapped_item)

    return data_list


def handle_xlsx_file(uploaded_file):
    import os
    import pandas as pd
    from datetime import datetime
    from django.conf import settings

    # 1. 保存上传的 Excel 文件到临时路径
    temp_dir = './temp'
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, uploaded_file.name)
    with open(temp_path, 'wb') as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)

    # 2. 读取数据
    df = pd.read_excel(temp_path)
    df.columns = [rename_map.get(col, col) for col in df.columns]

    illegal_fields = [col for col in df.columns if col not in allowed_fields and not col.startswith('options.')]
    if illegal_fields:
        raise ValueError(f"文件存在非法字段: {illegal_fields}")

    # 3. 准备保存图片目录
    today = datetime.now().strftime("%Y%m%d")
    tmp_img_dir = os.path.join(settings.BASE_DIR, "staticfiles", "images", today, "tmp")
    save_dir = os.path.join(settings.BASE_DIR, "staticfiles", "images", today)
    os.makedirs(save_dir, exist_ok=True)

    data_list = []

    # 4. 遍历每一题
    for idx, row in df.iterrows():
        item = {}
        for col in df.columns:
            if col.startswith("options."):
                continue
            val = row[col]
            if pd.notna(val):
                item[col] = str(val).strip()

        # 获取题目 ID
        question_id = int(get_question_id()) + 1
        item["question_id"] = question_id

        options = []

        for i in range(5):  # 最多支持 A-E
            label = chr(65 + i)  # A, B, C, ...
            key = f"options.{i}.text"
            val = row.get(key)

            if pd.notna(val):
                val_str = str(val).strip()

                # 判断是否形如 1_A、2_C 等（即数字_大写字母）
                if "_" in val_str and val_str.split("_")[-1].isalpha():
                    img_filename = val_str + ".png"
                    src_img_path = os.path.join(tmp_img_dir, img_filename)
                    dst_img_filename = f"{question_id + 2}_{label}.png"
                    dst_img_path = os.path.join(save_dir, dst_img_filename)

                    if os.path.exists(src_img_path):
                        shutil.copy(src_img_path, dst_img_path)
                        rel_path = f"images/{today}/{dst_img_filename}"
                        options.append({"label": label, "text": rel_path})
                        continue
                    else:
                        print(f"题目 {question_id} 选项 {label} 无文本且未找到对应图片 {img_filename}")

                # 普通文本选项
                options.append({"label": label, "text": val_str})
            else:
                # 无文本，默认跳过或打印
                print(f"题目 {question_id} 选项 {label} 无文本且未找到对应内容")

        if options:
            item["options"] = options

        data_list.append(item)

    # 清理上传临时文件
    if os.path.exists(temp_path):
        os.remove(temp_path)

    if not data_list:
        raise ValueError("无有效数据导入")

    for i, q in enumerate(data_list, 1):
        print(f"题目 {i}: {q}")

    return data_list
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from datetime import datetime
import os
import zipfile
from io import BytesIO

@csrf_exempt
def upload_images(request):
    if request.method != 'POST':
        return JsonResponse({"error": "仅支持 POST 请求"}, status=405)

    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return JsonResponse({"error": "请上传图片压缩包(.zip)"}, status=400)

    filename = uploaded_file.name.lower()
    if not filename.endswith(".zip"):
        return JsonResponse({"error": "仅支持上传 .zip 文件"}, status=400)

    today = datetime.now().strftime("%Y%m%d")
    save_dir = os.path.join(settings.BASE_DIR, "staticfiles", "images", today, "tmp")
    os.makedirs(save_dir, exist_ok=True)

    try:
        zip_file = zipfile.ZipFile(BytesIO(uploaded_file.read()))

        for file_info in zip_file.infolist():
            file_name = file_info.filename

            # 跳过 __MACOSX/ 和目录
            if file_name.startswith('__MACOSX/') or file_name.endswith('/'):
                continue

            # 可选：只处理图片文件（.png, .jpg, .jpeg）
            if not file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue

            # 解压文件
            target_path = os.path.join(save_dir, os.path.basename(file_name))
            with zip_file.open(file_info) as source, open(target_path, "wb") as target:
                target.write(source.read())

        zip_file.close()

    except Exception as e:
        return JsonResponse({"error": f"解压失败: {str(e)}"}, status=500)

    return JsonResponse({"success": True, "message": f"图片解压成功，保存目录: images/{today}/tmp"})


@csrf_exempt
def upload_file(request):
    if request.method != "POST":
        return JsonResponse({"error": "仅支持 POST 请求"}, status=405)

    uploaded_files = request.FILES.getlist("files")
    if not uploaded_files:
        return JsonResponse({"error": "请上传至少一个文件"}, status=400)

    inserted, skipped = 0, 0
    inserted_ids = []
    exists_contents = []
    actions = []

    for uploaded_file in uploaded_files:
        filename = uploaded_file.name.lower()
        data_list = []

        try:
            if filename.endswith(".json"):
                data_list = handle_json_file(uploaded_file)
            elif filename.endswith(".xlsx"):
                data_list = handle_xlsx_file(uploaded_file)
            else:
                return JsonResponse({"error": f"文件 {filename} 类型不支持，仅支持 .json 和 .xlsx"}, status=400)
        except ValueError as e:
            return JsonResponse({"error": f"文件处理失败: {str(e)}"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"文件解析失败: {str(e)}"}, status=400)

        for item in data_list:
            if not isinstance(item, dict):
                skipped += 1
                continue

            content = item.get("content")
            answer = item.get("answer")
            if not content or not answer:
                skipped += 1
                continue

            try:
                res = es.search(
                    index=index_name,
                    query={"term": {"content.keyword": content}},
                    size=1
                )
                if res["hits"]["total"]["value"] > 0:
                    exists_contents.append(content)
                    skipped += 1
                    continue
            except Exception:
                skipped += 1
                continue

            doc = {
                "question_id": get_question_id(),
                "content": str(content),
                "options": item.get("options"),
                "answer": str(answer),
                "question_type": item.get("question_type", "未知类型"),
                "explanation": item.get("explanation"),
                "source": item.get("source"),
                "ingest_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            }

            for key in item:
                if key.endswith('_img'):
                    doc[key] = item[key]

            actions.append({
                "_index": index_name,
                "_id": doc["question_id"],
                "_source": doc
            })

            inserted_ids.append(doc["question_id"])
            inserted += 1

    if not actions:
        return JsonResponse({
            "error": "无有效数据导入",
            "skipped": skipped,
            "exists": exists_contents
        }, status=400)

    try:
        helpers.bulk(es, actions)
    except Exception as e:
        return JsonResponse({"error": f"写入 ES 失败: {str(e)}"}, status=500)

    return JsonResponse({
        "success": True,
        "inserted": inserted,
        "skipped": skipped,
        "exists": exists_contents,
        "ids": inserted_ids,
    })
