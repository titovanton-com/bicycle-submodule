# coding: UTF-8

from django.contrib import admin

from models import Variable


class VariableAdmin(admin.ModelAdmin):
    model = Variable
    list_display = ('title', 'name')
    exclude = ('name',)


admin.site.register(Variable, VariableAdmin)
