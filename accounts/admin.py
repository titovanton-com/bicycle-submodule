# -*- coding: utf-8 -*-

class InvitationAdminMixin(object):
    list_display = ('unique_email', 'status')
    fields = ('unique_email',)
    actions = ('send_email',)

    def send_email(self, request, queryset):
        for invitation in queryset:
            invitation.send_email(request)
    send_email.short_description = 'Отправить приглашение'
