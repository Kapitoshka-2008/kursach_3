from django.contrib import admin

from mailings.models import Mailing, MailingAttempt, Message, Recipient


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'owner', 'created_at')
    search_fields = ('subject', 'body', 'owner__email')


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'owner')
    search_fields = ('email', 'full_name', 'owner__email')


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'start_time', 'end_time', 'owner')
    list_filter = ('status',)
    search_fields = ('id', 'owner__email')
    filter_horizontal = ('recipients',)


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ('mailing', 'recipient', 'status', 'attempt_time')
    list_filter = ('status',)
    search_fields = ('mailing__id', 'recipient__email')
