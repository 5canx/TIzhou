import os
import json
import random
from datetime import datetime
from functools import wraps
import pandas as pd

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import NotFoundError
import redis

# 读取配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(BASE_DIR, "index/views/config.json"), "r", encoding="utf-8") as f:
    config = json.load(f)

redis_conf = config["redis"]
rename_map = config.get("rename_map", {})
allowed_fields = set(rename_map.values())
index_name = config.get("index_name", "questions")

# Redis客户端
client = redis.StrictRedis(
    host=redis_conf["host"],
    port=redis_conf["port"],
    db=redis_conf["db"],
    password=redis_conf["password"],
    decode_responses=True
)

es = Elasticsearch("http://localhost:9200")


def get_question_id():
    # 用 Redis 计数器生成每日唯一题号
    date_key = datetime.now().strftime("qid:%Y%m%d")
    num = client.incr(date_key)
    client.expire(date_key, 2 * 24 * 60 * 60)  # 2天过期
    return f"{datetime.now().strftime('%Y%m%d')}{num:04d}"


def csrf_exempt_post(view_func):
    @csrf_exempt
    @require_POST
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapped_view


@csrf_exempt_post
def search_by_id(request):
    try:
        body = json.loads(request.body)
        qid = body.get("id")
        if not qid:
            return JsonResponse({"error": "请提供题目编号 id"}, status=400)

        try:
            res = es.get(index=index_name, id=qid)
            return JsonResponse(res["_source"], json_dumps_params={'ensure_ascii': False})
        except NotFoundError:
            return JsonResponse({"error": f"题目 ID {qid} 未找到"}, status=404)

    except Exception as e:
        return JsonResponse({"error": f"查询失败: {e}"}, status=500)


@csrf_exempt_post
def search_by_content(request):
    try:
        body = json.loads(request.body)
        keyword = body.get("content")
        if not keyword:
            return JsonResponse({"error": "请提供查询内容 content"}, status=400)

        res = es.search(
            index=index_name,
            query={
                "match": {
                    "content": keyword
                }
            },
            size=10
        )
        hits = [hit["_source"] for hit in res.get("hits", {}).get("hits", [])]
        return JsonResponse({"results": hits}, json_dumps_params={'ensure_ascii': False})

    except Exception as e:
        return JsonResponse({"error": f"查询失败: {e}"}, status=500)


@csrf_exempt
def list_all_questions(request):
    try:
        res = es.search(index=index_name, size=1000, query={"match_all": {}})
        hits = [hit["_id"] for hit in res["hits"]["hits"]]
        return JsonResponse({"ids": hits}, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        return JsonResponse({"error": str(e)})
@csrf_exempt

def upload_file(request):

    if request.method != "POST":
        return JsonResponse({"error": "仅支持 POST 请求"}, status=405)

    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return JsonResponse({"error": "请上传文件"}, status=400)

    filename = uploaded_file.name.lower()
    data_list = []

    try:
        if filename.endswith(".json"):
            content = uploaded_file.read().decode("utf-8")
            raw_data = json.loads(content)

            if isinstance(raw_data, dict):
                raw_data = [raw_data]
            elif not isinstance(raw_data, list):
                return JsonResponse({"error": "JSON 文件必须是对象或对象列表"}, status=400)

            # ✅ 对每条题目执行字段映射
            for item in raw_data:
                if isinstance(item, dict):
                    mapped_item = {rename_map.get(k, k): v for k, v in item.items()}
                    data_list.append(mapped_item)

        elif filename.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
            df.columns = [rename_map.get(col, col) for col in df.columns]

            illegal_fields = [col for col in df.columns if col not in allowed_fields]
            if illegal_fields:
                return JsonResponse({"error": f"存在非法字段: {illegal_fields}"}, status=400)

            data_list = df.to_dict(orient="records")

        else:
            return JsonResponse({"error": "仅支持 .json 和 .xlsx 文件"}, status=400)

    except Exception as e:
        return JsonResponse({"error": f"文件解析失败: {str(e)}"}, status=400)

    # ✅ 数据导入处理
    actions = []
    inserted_ids = []
    skipped = 0

    for item in data_list:
        if not isinstance(item, dict):
            skipped += 1
            continue

        doc = {k: v for k, v in item.items() if k in allowed_fields}

        if not doc.get("content") or not doc.get("answer"):
            skipped += 1
            continue

        try:
            res = es.search(index=index_name, query={"term": {"content.keyword": doc["content"]}}, size=1)
            if res["hits"]["total"]["value"] > 0:
                skipped += 1
                continue
        except Exception:
            skipped += 1
            continue

        doc["question_id"] = get_question_id()
        doc["ingest_time"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        actions.append({
            "_index": index_name,
            "_id": doc["question_id"],
            "_source": doc
        })
        inserted_ids.append(doc["question_id"])

    if not actions:
        return JsonResponse({"error": "无有效数据导入", "skipped": skipped}, status=400)

    try:
        helpers.bulk(es, actions)
    except Exception as e:
        return JsonResponse({"error": f"写入 ES 失败: {str(e)}"}, status=500)

    return JsonResponse({
        "success": True,
        "inserted": len(actions),
        "skipped": skipped,
        "ids": inserted_ids,
    })
def upload_page(request):
    return render(request, 'upload.html')


def search_page(request):
    return render(request, 'search.html')
