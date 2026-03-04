from rest_framework import serializers
from .models import User, Projet, Tache

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

class ProjetSerializer(serializers.ModelSerializer):
    createur = UserSerializer(read_only=True)
    nombre_taches = serializers.IntegerField(source='taches.count', read_only=True)

    class Meta:
        model = Projet
        fields = ['id', 'nom', 'description', 'createur', 'membres', 'nombre_taches', 'date_creation']

class TacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tache
        fields = '__all__'