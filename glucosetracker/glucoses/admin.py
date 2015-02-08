from django.contrib import admin
from django.utils.text import Truncator

from .models import Glucose, Category


class GlucoseAdmin(admin.ModelAdmin):
    list_display = [
        'value',
        'category',
        'record_date',
        'record_time',
        'notes_truncated',
        'tag_list',
        'user',
        'created',
        'modified',
    ]

    list_filter = [
        'user',
        'category',
    ]

    def notes_truncated(self, obj):
        return Truncator(obj.notes).chars(75)
    notes_truncated.admin_order_field = 'notes'
    notes_truncated.short_description = 'Notes'

    def tag_list(self, obj):
        """
        Retrieve the tags separated by comma.
        """
        return ', '.join([t.name for t in obj.tags.all()])
    tag_list.short_description = 'Tags'


class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
    ]


admin.site.register(Glucose, GlucoseAdmin)
admin.site.register(Category, CategoryAdmin)
