"""Core admin."""
from django import forms
from django.contrib import admin
from tinymce.widgets import TinyMCE

from apps.core.models import PageContent


class PageContentForm(forms.ModelForm):
    """Форма с TinyMCE редактором."""

    content = forms.CharField(
        widget=TinyMCE(attrs={'cols': 80, 'rows': 30}),
        label='Содержимое'
    )

    class Meta:
        model = PageContent
        fields = '__all__'


@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    """Админка для страниц."""

    form = PageContentForm
    list_display = ['slug', 'title', 'is_active', 'updated_at']
    list_filter = ['is_active', 'slug']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = [
        (None, {
            'fields': ['slug', 'title', 'is_active']
        }),
        ('Содержимое', {
            'fields': ['content'],
        }),
        ('Даты', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse'],
        }),
    ]
