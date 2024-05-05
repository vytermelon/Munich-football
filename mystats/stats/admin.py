from django.contrib import admin

# Register your models here.

from .models import Match,Stats

admin.site.register(Match)
admin.site.register(Stats)