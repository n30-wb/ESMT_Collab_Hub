"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core.views import dashboard
from core.views import dashboard, CustomLoginView, creer_projet, projet_details, ajouter_membre, creer_tache, changer_statut_tache, profil, supprimer_projet, inscription, live_stats
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.api_views import ProjetViewSet, TacheViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'projets', ProjetViewSet, basename='projet-api')
router.register(r'taches', TacheViewSet, basename='tache-api')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('', dashboard, name='dashboard'),
path('creer-projet/', creer_projet, name='creer_projet'),
path('projet/<int:projet_id>/', projet_details, name='projet_details'),
    path('projet/<int:projet_id>/ajouter-membre/', ajouter_membre, name='ajouter_membre'),
path('projet/<int:projet_id>/creer-tache/', creer_tache, name='creer_tache'),
path('tache/<int:tache_id>/statut/<str:nouveau_statut>/', changer_statut_tache, name='changer_statut_tache'),
path('profil/', profil, name='profil'),
path('projet/<int:projet_id>/supprimer/', supprimer_projet, name='supprimer_projet'),
path('inscription/', inscription, name='inscription'),
    # API Routes
    path('api/', include(router.urls)),

    # JWT Authentication (pour le frontend)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
path('live-stats/', live_stats, name='live_stats'),
]
