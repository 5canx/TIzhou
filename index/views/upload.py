from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import pandas as pd
from datetime import datetime
from elasticsearch import helpers
from .utils import rename_map, allowed_fields, get_question_id, es, index_name

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
                content = uploaded_file.read().decode("utf-8")
                raw_data = json.loads(content)
                if isinstance(raw_data, dict):
                    raw_data = [raw_data]
                elif not isinstance(raw_data, list):
                    return JsonResponse({"error": f"文件 {filename} JSON 格式不正确"}, status=400)

                for item in raw_data:
                    if isinstance(item, dict):
                        mapped_item = {rename_map.get(k, k): v for k, v in item.items()}
                        data_list.append(mapped_item)

            elif filename.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
                df.columns = [rename_map.get(col, col) for col in df.columns]
                illegal_fields = [col for col in df.columns if col not in allowed_fields]
                if illegal_fields:
                    return JsonResponse({"error": f"文件 {filename} 存在非法字段: {illegal_fields}"}, status=400)
                data_list = df.to_dict(orient="records")

            else:
                return JsonResponse({"error": f"文件 {filename} 类型不支持，仅支持 .json 和 .xlsx"}, status=400)

        except Exception as e:
            return JsonResponse({"error": f"文件 {filename} 解析失败: {str(e)}"}, status=400)

        # ✅ 针对每个文件的数据列表，统一处理
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
                "ingest_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            }

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
