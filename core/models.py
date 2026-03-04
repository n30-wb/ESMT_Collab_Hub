from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

# --- ON RAJOUTE LA CLASSE USER ICI ---
class User(AbstractUser):
    ROLE_CHOICES = (
        ('ETUDIANT', 'Étudiant'),
        ('PROFESSEUR', 'Professeur'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='ETUDIANT')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def calculer_prime(self):
        if self.role != 'PROFESSEUR':
            return 0

        taches = self.mes_taches.all()
        total = taches.count()
        if total == 0: return 0

        # On compte les tâches terminées dans les temps
        from django.utils import timezone
        terminees_a_temps = taches.filter(
            statut='TERMINE',
            date_fin_reelle__lte=models.F('date_limite')
        ).count()

        pourcentage = (terminees_a_temps / total) * 100

        if pourcentage == 100:
            return 100000
        elif pourcentage >= 90:
            return 30000
        return 0
    def __str__(self):
        return f"{self.username} ({self.role})"

# --- LE RESTE DE TON CODE ---
class Projet(models.Model):
    nom = models.CharField(max_length=200)
    description = models.TextField()
    createur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='projets_crees')
    membres = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='projets_participation')
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

    def calculer_prime_totale(self):
        prime_totale = 0
        taches_terminees = self.taches.filter(statut='TERMINE')

        for tache in taches_terminees:
            # On vérifie si le prof est l'assigné
            if tache.assigne_a.role == 'PROFESSEUR':
                # Si fini avant la deadline -> 100 000 FCFA
                if tache.date_fin_reelle <= tache.date_limite:
                    prime_totale += 100000
                # Si fini après la deadline -> 30 000 FCFA
                else:
                    prime_totale += 30000
        return prime_totale
class Tache(models.Model):
    STATUS_CHOICES = (
        ('A_FAIRE', 'À faire'),
        ('EN_COURS', 'En cours'),
        ('TERMINE', 'Terminé'),
    )

    titre = models.CharField(max_length=200)
    description = models.TextField()
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='taches')
    assigne_a = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mes_taches')
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='A_FAIRE')
    date_limite = models.DateTimeField()
    date_fin_reelle = models.DateTimeField(null=True, blank=True)

    def clean(self):
        # Logique métier : Un étudiant ne peut pas assigner une tâche à un professeur
        if hasattr(self.projet.createur, 'role') and hasattr(self.assigne_a, 'role'):
            if self.projet.createur.role == 'ETUDIANT' and self.assigne_a.role == 'PROFESSEUR':
                raise ValidationError("Un étudiant ne peut pas assigner une tâche à un professeur.")

    def __str__(self):
        return f"{self.titre} ({self.get_statut_display()})"