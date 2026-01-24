from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from apps.bot.models import Broadcast, BroadcastLog, BotAdmin


class BroadcastLogInline(TabularInline):
    model = BroadcastLog
    extra = 0
    readonly_fields = ['user', 'telegram_id', 'status', 'error_message', 'sent_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Broadcast)
class BroadcastAdmin(ModelAdmin):
    list_display = [
        'id',
        'recipients_display',
        'content_type',
        'status',
        'total_recipients',
        'sent_count',
        'failed_count',
        'created_at',
    ]
    list_filter = ['status', 'content_type', 'created_at']
    search_fields = ['text', 'recipients_usernames']
    readonly_fields = [
        'recipients_usernames',
        'status',
        'total_recipients',
        'sent_count',
        'failed_count',
        'created_by',
        'created_by_telegram_id',
        'started_at',
        'completed_at',
        'created_at',
    ]
    inlines = [BroadcastLogInline]

    fieldsets = (
        ('Получатели', {
            'fields': ('recipients_usernames',),
        }),
        ('Контент', {
            'fields': ('content_type', 'text', 'file_id'),
        }),
        ('Статус', {
            'fields': ('status',),
        }),
        ('Статистика', {
            'fields': ('total_recipients', 'sent_count', 'failed_count'),
        }),
        ('Информация', {
            'fields': ('created_by', 'created_by_telegram_id', 'created_at', 'started_at', 'completed_at'),
        }),
    )

    @admin.display(description='Получатели')
    def recipients_display(self, obj):
        usernames = obj.recipients_usernames or []
        if not usernames:
            return '-'
        if len(usernames) <= 3:
            return ', '.join(f"@{u}" for u in usernames)
        return f"@{usernames[0]}, @{usernames[1]}... (+{len(usernames) - 2})"


@admin.register(BroadcastLog)
class BroadcastLogAdmin(ModelAdmin):
    list_display = ['id', 'broadcast', 'telegram_id', 'status', 'sent_at']
    list_filter = ['status', 'broadcast']
    search_fields = ['telegram_id', 'error_message']
    readonly_fields = ['broadcast', 'user', 'telegram_id', 'status', 'error_message', 'sent_at', 'created_at']


@admin.register(BotAdmin)
class BotAdminAdmin(ModelAdmin):
    list_display = ['username', 'telegram_id', 'first_name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['username', 'telegram_id', 'first_name', 'note']
    list_editable = ['is_active']
    readonly_fields = ['telegram_id', 'first_name', 'created_at']

    fieldsets = (
        ('Telegram', {
            'fields': ('username',),
            'description': 'Введите username с @ (например @username). Telegram ID заполнится автоматически.',
        }),
        ('Автозаполняемые поля', {
            'fields': ('telegram_id', 'first_name'),
            'classes': ('collapse',),
            'description': 'Эти поля заполняются автоматически при первом использовании команды /broadcast',
        }),
        ('Статус', {
            'fields': ('is_active',),
        }),
        ('Дополнительно', {
            'fields': ('note', 'created_at'),
        }),
    )
