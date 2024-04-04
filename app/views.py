from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseNotFound



QUESTIONS = [
    {
        "id" : i,
        "title": f"Question {i}",
        "text": f"This is question number {i}"
    }for i in range(35)
]

ANSWERS = [
    {
        "text": f"This is ANSWER number {i}"
    }for i in range(35)
]

def get_tag_color(tag_id):
    colors = ["#2C3E50", "#16A085", "#F39C12", "#8E44AD", "#E74C3C", "#3498DB", "#1ABC9C", "#F1C40F"]
    return colors[tag_id % len(colors)]

TAGS = [
    {
        "id": i, 
        "name_tag": f"This is TAG number {i}",
        "color":get_tag_color(i)
    }for i in range(8)
]

def paginator_func( request, view_name, view_id):
    page_num = request.GET.get('page', 1)
    paginator = Paginator(QUESTIONS, 5)
    try:
        page_obj = paginator.page(page_num)
        page_obj.view_name = view_name
        page_obj.view_id = view_id
        return page_obj
    except PageNotAnInteger:
        page_obj = paginator.page(1)
        page_obj.view_name = view_name
        page_obj.view_id = view_id
        return page_obj
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
        page_obj.view_name = view_name
        page_obj.view_id = view_id
        return page_obj

def index(request):
    page_obj = paginator_func( request, 'index', None)
    return render(request, "index.html", {'questions': page_obj ,"tags": TAGS})

def hot(request):
    page_obj = paginator_func( request, 'hot', None)
    return render(request, "hot.html", {"questions":page_obj, "tags": TAGS})

def question(request, question_id):
    item = QUESTIONS[question_id]
    return render(request, "question.html", {"question": item, "answers":ANSWERS, "tags": TAGS })  

def tag(request, tag_id):
    page_obj = paginator_func( request, 'tag', tag_id)
    tag = next((tag for tag in TAGS if tag['id'] == tag_id), None)
    if not tag:
        return HttpResponseNotFound("Tag not found")
    
    return render(request, "tag.html", {"tag": tag, "questions": page_obj, "tags": TAGS})

def login(request):
    return render(request, "login.html", {"tags": TAGS})

def signup(request):
    return render(request, "signup.html", {"tags": TAGS})

def settings(request):
    return render(request, "settings.html", {"tags": TAGS})

def ask(request):
    return render(request, "ask.html", {"tags": TAGS})