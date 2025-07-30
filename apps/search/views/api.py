"""
搜索API视图
"""
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..services import SearchService

search_service = SearchService()


@csrf_exempt
def search_by_id(request):
    """根据ID搜索题目"""
    if request.method != "POST":
        return JsonResponse({"error": "仅支持 POST 请求"}, status=405)
    
    try:
        body = json.loads(request.body)
        question_id = body.get("id")
        if not question_id:
            return JsonResponse({"error": "请提供题目编号 id"}, status=400)

        result = search_service.search_by_id(question_id)
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"查询失败: {e}"}, status=500)


@csrf_exempt
def search_by_content(request):
    """根据内容搜索题目"""
    if request.method != "POST":
        return JsonResponse({"error": "仅支持 POST 请求"}, status=405)
    
    try:
        body = json.loads(request.body)
        keyword = body.get("content")
        if not keyword:
            return JsonResponse({"error": "请提供查询内容 content"}, status=400)

        size = int(body.get("size", 10))
        from_ = int(body.get("from", 0))

        result = search_service.search_by_content(keyword, size, from_)
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        return JsonResponse({"error": f"查询失败: {e}"}, status=500)


@csrf_exempt
def list_all_questions(request):
    """列出所有题目"""
    if request.method != "GET":
        return JsonResponse({"error": "仅支持 GET 请求"}, status=405)
    
    try:
        size = int(request.GET.get("size", 100))
        from_ = int(request.GET.get("from", 0))

        result = search_service.list_all_questions(size, from_)
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        return JsonResponse({"error": f"查询失败: {e}"}, status=500) 