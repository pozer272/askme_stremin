from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from app.models import Question, Answer, Tag
from django.db.models import Count
from django.views.decorators.csrf import requires_csrf_token
from django.contrib.auth import authenticate, logout
from django.urls import reverse
from app.forms import LoginForm, SignUpForm
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login

# def paginator_func(request, qs):
#     try:
#         limit = int(request.GET.get("limit", 10))
#     except ValueError:
#         limit = 10
#     if limit > 100:
#         limit = 10
#     try:
#         num_page = int(request.GET.get("page", 1))
#     except ValueError:
#         raise Http404
#     paginator = Paginator(qs, limit)
#     try:
#         page = paginator.page(num_page)
#     except EmptyPage:
#         page = paginator.page(paginator.num_pages)
#     return page


def paginator_func(request, qs, view_name, view_id):
    page_num = request.GET.get("page", 1)
    paginator = Paginator(qs, 5)
    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    page_obj.view_name = view_name
    page_obj.view_id = view_id
    return page_obj


def index(request):
    questions_query = Question.objects.new().annotate(num_answers=Count("answer"))
    page_obj = paginator_func(request, questions_query, "index", None)
    return render(
        request, "index.html", {"questions": page_obj, "tags": Tag.objects.all()[:10]}
    )


def hot(request):
    questions_query = Question.objects.hot().annotate(num_answers=Count("answer"))
    page_obj = paginator_func(request, questions_query, "hot", None)
    return render(
        request, "hot.html", {"questions": page_obj, "tags": Tag.objects.all()[:10]}
    )


def question(request, question_id):
    q = Question.objects.with_num_answers_and_rating().get(pk=question_id)
    answers = Answer.objects.answers_for_question(q)
    page_obj = paginator_func(request, answers, "question", question_id)
    num_answers = answers.count()
    return render(
        request,
        "question.html",
        {
            "question": q,
            "answers": page_obj,
            "num_answers": num_answers,
            "tags": Tag.objects.all()[:10],
        },
    )


def tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    questions_query = (
        Question.objects.filter(tags=tag)
        .order_by("-created_at")
        .annotate(num_answers=Count("answer"))
    )
    page_obj = paginator_func(request, questions_query, "tag", tag_id)
    return render(
        request,
        "tag.html",
        {"tag": tag, "questions": page_obj, "tags": Tag.objects.all()[:10]},
    )


@require_http_methods(["GET", "POST"])
def login(request):
    print(request.POST)
    continue_url = request.GET.get("continue", reverse("index"))
    if request.method == "GET":
        login_form = LoginForm()
    if request.method == "POST":
        login_form = LoginForm(data=request.POST)
        if login_form.is_valid():
            user = authenticate(request, **login_form.cleaned_data)
            if user:
                auth_login(request, user)
                return redirect(continue_url)
    return render(
        request,
        "login.html",
        context={"tags": Tag.objects.all()[:10], "form": login_form},
    )


def logout_view(request):
    logout(request)
    return redirect(reverse("login"))


@require_http_methods(["GET", "POST"])
def signup(request):
    if request.method == "GET":
        user_form = SignUpForm()
    if request.method == "POST":
        user_form = SignUpForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            if user:
                return redirect(reverse("index"))
            else:
                user_form.add_error(field=None, error="User saving error")
    return render(
        request, "signup.html", {"tags": Tag.objects.all()[:10], "form": user_form}
    )


@login_required
def settings(request):
    return render(request, "settings.html", {"tags": Tag.objects.all()[:10]})


def ask(request):
    return render(request, "ask.html", {"tags": Tag.objects.all()[:10]})
