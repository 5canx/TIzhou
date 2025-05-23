import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import es, index_name
from elasticsearch.exceptions import NotFoundError


@csrf_exempt
def search_by_id(request):
    if request.method != "POST":
        return JsonResponse({"error": "仅支持 POST 请求"}, status=405)

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


@csrf_exempt
def search_by_content(request):
    if request.method != "POST":
        return JsonResponse({"error": "仅支持 POST 请求"}, status=405)

    try:
        body = json.loads(request.body)
        keyword = body.get("content")
        if not keyword:
            return JsonResponse({"error": "请提供查询内容 content"}, status=400)

        res = es.search(
            index=index_name,
            query={"match": {"content": keyword}},
            size=1
        )

        hits = res.get("hits", {}).get("hits", [])
        if not hits:
            return JsonResponse({"error": "未找到匹配的题目"}, status=404)

        source = hits[0]["_source"]

        # 确保 answer 是字符串
        if "answer" in source and source["answer"] is not None:
            source["answer"] = str(source["answer"])

        return JsonResponse(source, json_dumps_params={'ensure_ascii': False})

    except Exception as e:
        return JsonResponse({"error": f"查询失败: {e}"}, status=500)



@csrf_exempt
def list_all_questions(request):
    if request.method != "GET":
        return JsonResponse({"error": "仅支持 GET 请求"}, status=405)

    try:
        res = es.search(index=index_name, size=1000, query={"match_all": {}})
        hits = [hit["_id"] for hit in res["hits"]["hits"]]
        return JsonResponse({"ids": hits}, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
