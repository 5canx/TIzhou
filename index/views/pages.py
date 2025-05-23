from django.shortcuts import render

def upload(request):
    return render(request, 'upload.html')

def search(request):
    return render(request, 'search.html')
