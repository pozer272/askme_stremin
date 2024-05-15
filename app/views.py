from pyexpat.errors import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from app.models import Question, Answer, Tag
from django.db.models import Count
from django.views.decorators.csrf import requires_csrf_token
from django.contrib.auth import authenticate, logout
from django.urls import reverse
from app.forms import LoginForm, SignUpForm, SettingsForm, AnswerForm, QuestionForm
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


# @login_required(login_url="/login")
def index(request):
    questions_query = Question.objects.new().annotate(num_answers=Count("answer"))
    page_obj = paginator_func(request, questions_query, "index", None)
    popular_tags = Tag.objects.with_question_count()[:10]
    return render(request, "index.html", {"questions": page_obj, "tags": popular_tags})


# @login_required(login_url="/login")
def hot(request):
    questions_query = Question.objects.hot().annotate(num_answers=Count("answer"))
    page_obj = paginator_func(request, questions_query, "hot", None)
    popular_tags = Tag.objects.with_question_count()[:10]
    return render(request, "hot.html", {"questions": page_obj, "tags": popular_tags})


# @login_required(login_url="/login")
@require_http_methods(["GET", "POST"])
def question(request, question_id):
    q = Question.objects.with_num_answers_and_rating().get(pk=question_id)
    continue_url = request.GET.get("continue", reverse("question", args=[q.id]))
    answers = Answer.objects.answers_for_question(q)
    page_obj = paginator_func(request, answers, "question", question_id)
    popular_tags = Tag.objects.with_question_count()[:10]
    num_answers = answers.count()
    if request.method == "POST":
        answer_form = AnswerForm(request.POST)
        if answer_form.is_valid():
            answer = answer_form.save(commit=False)
            answer.user = request.user
            answer.question_to = q
            answer.author = q.author
            answer.save()
            return redirect(continue_url)
    else:
        answer_form = AnswerForm()
    return render(
        request,
        "question.html",
        {
            "question": q,
            "answers": page_obj,
            "num_answers": num_answers,
            "tags": popular_tags,
            "answer_form": answer_form,
        },
    )


# @login_required(login_url="/login")
def tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    questions_query = (
        Question.objects.filter(tags=tag)
        .order_by("-created_at")
        .annotate(num_answers=Count("answer"))
    )
    page_obj = paginator_func(request, questions_query, "tag", tag_id)
    popular_tags = Tag.objects.with_question_count()[:10]
    return render(
        request,
        "tag.html",
        {
            "tag": tag,
            "questions": page_obj,
            "tags": popular_tags,
        },
    )


@require_http_methods(["GET", "POST"])
def login(request):
    popular_tags = Tag.objects.with_question_count()[:10]
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
        context={"tags": popular_tags, "login_form": login_form},
    )


@require_http_methods(["GET", "POST"])
def signup(request):
    popular_tags = Tag.objects.with_question_count()[:10]
    continue_url = request.GET.get("continue", reverse("index"))
    if request.method == "GET":
        signup_form = SignUpForm()
    else:
        signup_form = SignUpForm(request.POST, request.FILES)
        if signup_form.is_valid():
            user = signup_form.save()
            if user:
                auth_login(request, user)
                return redirect(continue_url)
            else:
                signup_form.add_error(field=None, error="User saving error")
    return render(
        request, "signup.html", {"tags": popular_tags, "signup_form": signup_form}
    )


@require_http_methods(["GET", "POST"])
def settings(request):
    user = request.user
    continue_url = request.GET.get("continue", reverse("settings"))
    popular_tags = Tag.objects.with_question_count()[:10]
    if request.method == "GET":
        settings_form = SettingsForm(instance=user)
    if request.method == "POST":
        settings_form = SettingsForm(request.POST, request.FILES, instance=user)
        if settings_form.is_valid():
            settings_form.save()
            return redirect(continue_url)
    return render(
        request, "settings.html", {"tags": popular_tags, "settings_form": settings_form}
    )


def logout_view(request):
    logout(request)
    if request.GET.get("next"):
        return redirect(request.GET.get("next"))
    return redirect(reverse("index"))


@require_http_methods(["GET", "POST"])
def ask(request):
    popular_tags = Tag.objects.with_question_count()[:10]

    if request.method == "GET":
        ask_form = QuestionForm()
    elif request.method == "POST":
        ask_form = QuestionForm(request.POST, request.FILES)
        ask_form.author = request.user
        if ask_form.is_valid():
            question = ask_form.save()
            question.author = request.user
            question.save()
            continue_url = request.GET.get(
                "continue", reverse("question", args=[question.id])
            )
            return redirect(continue_url)
    return render(
        request,
        "ask.html",
        {"tags": popular_tags, "ask_form": ask_form},
    )
