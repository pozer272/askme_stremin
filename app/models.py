from django.db import models
from django.contrib.auth.models import User
from datetime import date


class QuestionManager(models.Manager):
    def with_num_answers_and_rating(self):
        return self.annotate(
            answers_count=models.Count("answer"),
        ).annotate(
            likes_count=models.Count(
                models.Case(
                    models.When(votetoquestion__is_like=True, then=1),
                    output_field=models.IntegerField(),
                )
            ),
            dislikes_count=models.Count(
                models.Case(
                    models.When(votetoquestion__is_like=False, then=1),
                    output_field=models.IntegerField(),
                )
            ),
        )

    def new(self):
        return self.get_queryset().order_by("-created_at")

    def hot(self):
        return (
            self.get_queryset()
            .annotate(
                total_votes=models.F("rating_likes") - models.F("rating_dislikes")
            )
            .order_by("-total_votes", "-created_at")
        )

    def one_with_rating(self, pk):
        return self.annotate(
            likes_count=models.Count(
                models.Case(
                    models.When(votetoquestion__is_like=True, then=1),
                    output_field=models.IntegerField(),
                )
            ),
            dislikes_count=models.Count(
                models.Case(
                    models.When(votetoquestion__is_like=False, then=1),
                    output_field=models.IntegerField(),
                )
            ),
        ).get(pk=pk)


class TagManager(models.Manager):
    def with_question_count(self):
        return self.annotate(question_count=models.Count("question")).order_by(
            "-question_count"
        )


class UserManager(models.Manager):
    def with_rating(self):
        return self.annotate(
            likes_count=models.Count(
                models.Case(
                    models.When(user_to_who_is_vote__is_like=True, then=1),
                    output_field=models.IntegerField(),
                )
            ),
            dislikes_count=models.Count(
                models.Case(
                    models.When(user_to_who_is_vote__is_like=False, then=1),
                    output_field=models.IntegerField(),
                )
            ),
        )


class AnswerManager(models.Manager):
    def answers_for_question(self, question):
        return (
            self.filter(question_to=question)
            .annotate(
                likes_count=models.Count(
                    models.Case(
                        models.When(votetoanswer__is_like=True, then=1),
                        output_field=models.IntegerField(),
                    )
                ),
                dislikes_count=models.Count(
                    models.Case(
                        models.When(votetoanswer__is_like=False, then=1),
                        output_field=models.IntegerField(),
                    )
                ),
            )
            .order_by("-likes_count")
        )


class Tag(models.Model):
    objects = TagManager()
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    title = models.CharField(max_length=255, default="Title")
    text = models.TextField(max_length=2000, default="Text")
    image = models.ImageField(upload_to="questions/", default="")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    rating_likes = models.BigIntegerField(default=0)
    rating_dislikes = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = QuestionManager()

    def __str__(self):
        return f"{self.title, self.get_status_display()}"


class Answer(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    question_to = models.ForeignKey(Question, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AnswerManager()

    def __str__(self):
        return self.text


class myUser(models.Model):
    django_user = models.OneToOneField(User, on_delete=models.PROTECT)
    avatar = models.ImageField(blank=True, null=True)
    rating_likes = models.BigIntegerField(default=0)
    rating_dislikes = models.BigIntegerField(default=0)

    def __str__(self):
        return self.django_user.username


class VoteToUser(models.Model):
    user_from = models.ForeignKey(
        myUser, on_delete=models.CASCADE, related_name="user_who_vote"
    )
    user_to = models.ForeignKey(
        myUser, on_delete=models.CASCADE, related_name="user_to_who_is_vote"
    )
    is_like = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    unique_together = [["user__from", "user_to"]]


class VoteToQuestion(models.Model):
    user_from = models.ForeignKey(
        myUser, on_delete=models.CASCADE, related_name="user_who_vote_to_q"
    )
    question_to = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_like = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    unique_together = [["user__from", "question_to"]]


class VoteToAnswer(models.Model):
    user_from = models.ForeignKey(
        myUser, on_delete=models.CASCADE, related_name="user_who_vote_to_a"
    )
    answer_to = models.ForeignKey(Answer, on_delete=models.CASCADE)
    is_like = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    unique_together = [["user__from", "answer_to"]]
