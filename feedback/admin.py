# coding: UTF-8

from django.contrib import admin

from models import Feedback


class FeedbackAdmin(admin.ModelAdmin):
    model = Feedback
    list_display = ('name', 'email', 'user', 'created', 'updated')
    readonly_fields = ('created', 'updated')


admin.site.register(Feedback, FeedbackAdmin)
