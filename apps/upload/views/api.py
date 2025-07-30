"""
上传API视图
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..services import UploadService

upload_service = UploadService()


@csrf_exempt
def upload_file(request):
    """上传文件API"""
    if request.method != "POST":
        return JsonResponse({"error": "仅支持 POST 请求"}, status=405)
    
    try:
        if 'file' not in request.FILES:
            return JsonResponse({"error": "请选择要上传的文件"}, status=400)
        
        uploaded_file = request.FILES['file']
        
        # 检查文件大小
        if uploaded_file.size > 10 * 1024 * 1024:  # 10MB
            return JsonResponse({"error": "文件大小不能超过10MB"}, status=400)
        
        result = upload_service.upload_file(uploaded_file)
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"上传失败: {e}"}, status=500)


@csrf_exempt
def upload_images(request):
    """上传图片API"""
    if request.method != "POST":
        return JsonResponse({"error": "仅支持 POST 请求"}, status=405)
    
    try:
        if 'file' not in request.FILES:
            return JsonResponse({"error": "请选择要上传的ZIP文件"}, status=400)
        
        uploaded_file = request.FILES['file']
        
        # 检查文件类型
        if not uploaded_file.name.lower().endswith('.zip'):
            return JsonResponse({"error": "请上传ZIP格式的文件"}, status=400)
        
        # 检查文件大小
        if uploaded_file.size > 50 * 1024 * 1024:  # 50MB
            return JsonResponse({"error": "文件大小不能超过50MB"}, status=400)
        
        result = upload_service.upload_images(uploaded_file)
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"上传失败: {e}"}, status=500) 