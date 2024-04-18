from django.contrib import admin
from .models import (
    Tag,
    myUser,
    Question,
    Answer,
    VoteToUser,
    VoteToQuestion,
    VoteToAnswer,
)


class TagAdmin(admin.ModelAdmin):
    pass


class myUserAdmin(admin.ModelAdmin):
    pass


class QuestionAdmin(admin.ModelAdmin):
    pass


class AnswerAdmin(admin.ModelAdmin):
    pass


class VoteToUserAdmin(admin.ModelAdmin):
    pass


class VoteToQuestionAdmin(admin.ModelAdmin):
    pass


class VoteToAnswerAdmin(admin.ModelAdmin):
    pass


admin.site.register(Tag, TagAdmin)
admin.site.register(myUser, myUserAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(VoteToUser, VoteToUserAdmin)
admin.site.register(VoteToAnswer, VoteToAnswerAdmin)
admin.site.register(VoteToQuestion, VoteToQuestionAdmin)
