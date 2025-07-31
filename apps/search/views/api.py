import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from utils.database import es, index_name
from elasticsearch.exceptions import NotFoundError


def process_options(options):
    """
    遍历选项，检测text是否是图片路径（以'image'开头且以图片格式结尾），
    如果是，则标记 is_image=True 并放入 image 字段
    """
    image_exts = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
    processed = []
    for opt in options:
        new_opt = opt.copy()
        text = new_opt.get("text", "")
        if isinstance(text, str) and text.lower().startswith("image") and text.lower().endswith(image_exts):
            new_opt["is_image"] = True
            new_opt["image"] = text
            new_opt.pop("text", None)
        else:
            new_opt["is_image"] = False
        processed.append(new_opt)
    return processed


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
            source = res.get("_source", {})

            if "options" in source and isinstance(source["options"], list):
                source["options"] = process_options(source["options"])

            return JsonResponse(source, json_dumps_params={'ensure_ascii': False})
        except NotFoundError:
            return JsonResponse({"error": f"题目 ID {qid} 未找到"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "无效的 JSON 数据"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"查询失败: {str(e)}"}, status=500)


@csrf_exempt
def search_by_content(request):
    if request.method != "POST":
        return JsonResponse({"error": "仅支持 POST 请求"}, status=405)
    try:
        body = json.loads(request.body)
        keyword = body.get("content")
        if not keyword:
            return JsonResponse({"error": "请提供查询内容 content"}, status=400)

        size = int(body.get("size", 10))
        from_ = int(body.get("from", 0))

        res = es.search(
            index=index_name,
            query={
                "match": {
                    "content": {
                        "query": keyword,
                        "fuzziness": "AUTO"  # 添加模糊匹配
                    }
                }
            },
            size=size,
            from_=from_
        )
        hits = res.get("hits", {}).get("hits", [])
        if not hits:
            return JsonResponse({"error": "未找到匹配的题目"}, status=404)

        results = []
        for hit in hits:
            source = hit["_source"]
            if "answer" in source and source["answer"] is not None:
                source["answer"] = str(source["answer"])
            if "options" in source and isinstance(source["options"], list):
                source["options"] = process_options(source["options"])
            results.append(source)

        return JsonResponse({"results": results, "total": res["hits"]["total"]["value"]}, json_dumps_params={'ensure_ascii': False})

    except json.JSONDecodeError:
        return JsonResponse({"error": "无效的 JSON 数据"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"查询失败: {str(e)}"}, status=500)


@csrf_exempt
def list_all_questions(request):
    if request.method != "GET":
        return JsonResponse({"error": "仅支持 GET 请求"}, status=405)
    try:
        size = int(request.GET.get("size", 100))
        from_ = int(request.GET.get("from", 0))

        res = es.search(index=index_name, size=size, from_=from_, query={"match_all": {}})
        hits = [hit["_source"] for hit in res["hits"]["hits"]]  # 返回完整数据而非仅 ID

        return JsonResponse({
            "results": hits,
            "total": res["hits"]["total"]["value"],
            "size": size,
            "from": from_
        }, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        return JsonResponse({"error": f"查询失败: {str(e)}"}, status=500)