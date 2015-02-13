from django.contrib import admin

from .models import Game, Seed, Cluster, Chain

@admin.register(Game, Seed, Cluster, Chain)
class GameAdmin(admin.ModelAdmin):
    pass
