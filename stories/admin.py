from django.contrib import admin
from .models import Story, Section, Sectionlink

# Register your models here.

admin.site.register(Story)
admin.site.register(Section)
admin.site.register(Sectionlink)
