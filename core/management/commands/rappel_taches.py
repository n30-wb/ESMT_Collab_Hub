from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from core.models import Tache

class Command(BaseCommand):
    help = 'Envoie un email pour les tâches qui expirent dans 24h'

    def handle(self, *args, **options):
        # On cible demain
        demain = timezone.now().date() + timedelta(days=1)
        taches_urgentes = Tache.objects.filter(date_limite=demain, statut='EN_COURS')

        for tache in taches_urgentes:
            if tache.assigne_a and tache.assigne_a.email:
                send_mail(
                    subject=f"⚠️ Échéance demain : {tache.titre}",
                    message=f"Bonjour {tache.assigne_a.username},\n\nLa tâche '{tache.titre}' du projet '{tache.projet.nom}' doit être terminée demain ({tache.date_limite}).\n\nBon courage !",
                    from_email='alerte@esmt-collab.sn',
                    recipient_list=[tache.assigne_a.email],
                )
                self.stdout.write(self.style.SUCCESS(f'Mail envoyé à {tache.assigne_a.username}'))