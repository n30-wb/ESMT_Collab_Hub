from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Projet, Tache
from .serializers import ProjetSerializer, TacheSerializer


class ProjetViewSet(viewsets.ModelViewSet):
    """
    API pour gérer les projets.
    """
    serializer_class = ProjetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # On ne retourne que les projets où l'utilisateur est présent (créateur ou membre)
        return Projet.objects.filter(membres=self.request.user).distinct()

    def perform_create(self, serializer):
        # On définit automatiquement l'utilisateur connecté comme créateur
        serializer.save(createur=self.request.user)


class TacheViewSet(viewsets.ModelViewSet):
    """
    API pour gérer les tâches avec recherche et filtrage.
    """
    queryset = Tache.objects.all()
    serializer_class = TacheSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Configuration des moteurs de filtrage et recherche
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    # Filtres exacts (ex: /api/taches/?statut=TERMINE)
    filterset_fields = ['statut',]

    # Recherche textuelle (ex: /api/taches/?search=backend)
    search_fields = ['titre', 'description']