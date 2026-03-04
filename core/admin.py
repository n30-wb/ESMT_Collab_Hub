from django.contrib import admin
from .models import User, Projet, Tache

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'email')
    list_filter = ('role',)

@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = ('nom', 'createur', 'date_creation')

@admin.register(Tache)
class TacheAdmin(admin.ModelAdmin):
    list_display = ('titre', 'projet', 'assigne_a', 'statut', 'date_limite')
    list_filter = ('statut', 'projet')