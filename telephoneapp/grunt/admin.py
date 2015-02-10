from django.contrib import admin

from .models import Game, Seed, Cluster, Chain, Entry

@admin.register(Game, Seed, Cluster, Chain, Entry)
class GameAdmin(admin.ModelAdmin):
    pass
