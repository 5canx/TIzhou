from django.shortcuts import render
from django.core.paginator import Paginator
from .utils import es, index_name

def es_question_list(request):
    query = request.GET.get("q", "")
    page_num = int(request.GET.get("page", 1))
    page_size = 10

    if query:
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["content", "answer"]
                }
            }
        }
    else:
        body = {"query": {"match_all": {}}}

    res = es.search(index=index_name, body=body, from_=(page_num - 1) * page_size, size=page_size)
    hits = res["hits"]["hits"]
    total = res["hits"]["total"]["value"]

    questions = []
    for hit in hits:
        source = hit["_source"]
        source["id"] = hit["_id"]
        questions.append(source)

    paginator = Paginator(range(total), page_size)  # 只用来做分页控件

    context = {
        "questions": questions,
        "query": query,
        "paginator": paginator,
        "page_obj": paginator.page(page_num),
    }
    return render(request, "admin/index.html", context)
