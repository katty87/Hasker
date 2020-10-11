from django.contrib import admin


from main.models import Question, Answer, Tag


admin.site.register(Tag)
admin.site.register(Question)
admin.site.register(Answer)

