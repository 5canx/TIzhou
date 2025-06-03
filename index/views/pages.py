from django.shortcuts import render

def upload(request):
    return render(request, 'upload.html')

def search(request):
    return render(request, 'search.html')

def custom_404_view(request, exception):
    return render(request, '404.html', status=404)
def upload_images_page(request):
    return render(request, "upload_images.html")