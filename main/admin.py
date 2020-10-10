from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import UserProfile, Question, Answer, Tag


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = UserAdmin.list_display + ('avatar',)


admin.site.register(Tag)
admin.site.register(Question)
admin.site.register(Answer)

