from django.contrib import admin

from .models import Game, Chain, Message

@admin.register(Game, Chain, Message)
class GameAdmin(admin.ModelAdmin):
    pass
