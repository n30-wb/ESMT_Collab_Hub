from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .models import Projet, Tache, User
from django.shortcuts import get_object_or_404
from .models import User
from django.utils import timezone
from django.db.models import Count, Q,F
from django.utils import timezone
from datetime import timedelta
from django.db.models import F
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .forms import InscriptionForm
from django.contrib.auth import login
from django.core.mail import send_mail
from .models import Tache


@login_required
def valider_tache(request, tache_id):
    tache = get_object_or_404(Tache, id=tache_id)

    # On passe la tâche en "Terminée"
    tache.statut = 'TERMINE'
    tache.save()

    # Notification au créateur du projet
    createur = tache.projet.createur
    if createur.email:
        send_mail(
            subject=f"✅ Tâche validée : {tache.nom}",
            message=f"Bonjour {createur.username},\n\nLa tâche '{tache.nom}' du projet '{tache.projet.nom}' a été marquée comme terminée.\n\nCordialement,\nL'équipe ESMT Collab.",
            from_email='noreply@esmt-collab.sn',
            recipient_list=[createur.email],
            fail_silently=False,
        )

    messages.success(request, "Tâche validée et créateur notifié !")
    return redirect('projet_details', projet_id=tache.projet.id)
def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user) # Connecte l'utilisateur immédiatement après inscription
            return redirect('dashboard')
    else:
        form = InscriptionForm()
    return render(request, 'registration/inscription.html', {'form': form})


@login_required
def profil(request):
    if request.method == 'POST':
        # Mise à jour des infos de base
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        request.user.email = request.POST.get('email')

        # Gestion du mot de passe (si rempli)
        new_password = request.POST.get('new_password')
        if new_password:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)  # Évite d'être déconnecté
        else:
            request.user.save()

        messages.success(request, "Profil mis à jour avec succès !")
        return redirect('profil')

    return render(request, 'core/profil.html')


@login_required
def dashboard(request):
    projets = Projet.objects.filter(membres=request.user).distinct()
    utilisateurs = User.objects.all()

    prime = 0
    stats = {
        'total': 0,
        'terminees': 0,
        'dans_delais': 0,
        'annuel': 0,
        'trimestriel': 0,
        'pourcentage': 0
    }

    if request.user.role == 'PROFESSEUR':
        taches_prof = Tache.objects.filter(assigne_a=request.user)
        maintenant = timezone.now()

        stats['total'] = taches_prof.count()
        stats['terminees'] = taches_prof.filter(statut='TERMINE').count()
        # Tâches finies AVANT ou LE JOUR de la deadline
        stats['dans_delais'] = taches_prof.filter(
            statut='TERMINE',
            date_fin_reelle__lte=F('date_limite')
        ).count()

        # Stats temporelles
        stats['annuel'] = taches_prof.filter(date_creation__year=maintenant.year).count()
        stats['trimestriel'] = taches_prof.filter(
            date_creation__date__gte=maintenant.date() - timedelta(days=90)).count()

        if stats['total'] > 0:
            stats['pourcentage'] = (stats['dans_delais'] / stats['total']) * 100

            # Logique stricte du cahier des charges
            if stats['pourcentage'] == 100:
                prime = 100000
            elif stats['pourcentage'] >= 90:
                prime = 30000
            else:
                prime = 0

    return render(request, 'core/dashboard.html', {
        'projets': projets,
        'prime': prime,
        'stats': stats,
        'utilisateurs': utilisateurs
    })
@login_required
def dashboard(request):
    projets = Projet.objects.filter(membres=request.user).distinct()
    utilisateurs = User.objects.all()

    # --- LOGIQUE DES PRIMES (Cahier des charges) ---
    prime = 0
    stats_taches = {}

    if request.user.role == 'PROFESSEUR':
        # 1. On récupère toutes les tâches assignées à ce prof
        taches_prof = Tache.objects.filter(assigne_a=request.user)
        total_taches = taches_prof.count()

        if total_taches > 0:
            # 2. Tâches terminées dans les délais
            taches_dans_delais = taches_prof.filter(
                statut='TERMINE',
                date_fin_reelle__lte=F('date_limite')
            ).count()

            # 3. Calcul du pourcentage de réussite
            pourcentage = (taches_dans_delais / total_taches) * 100

            if pourcentage == 100:
                prime = 100000
            elif pourcentage >= 90:
                prime = 30000
            else:
                prime = 0

        # --- STATISTIQUES (Trimestrielles/Annuelles) ---
        maintenant = timezone.now()
        stats_taches = {
            'annuel': taches_prof.filter(date_creation__year=maintenant.year).count(),
            'trimestre': taches_prof.filter(date_creation__month__gte=maintenant.month - 3).count(),
            'terminees': taches_prof.filter(statut='TERMINE').count()
        }

    return render(request, 'core/dashboard.html', {
        'projets': projets,
        'prime': prime,
        'stats': stats_taches,
        'utilisateurs': utilisateurs
    })


@login_required
def projet_details(request, projet_id):
    projet = get_object_or_404(Projet, id=projet_id)
    taches = projet.taches.all().order_by('date_limite')
    # On récupère tous les utilisateurs pour pouvoir les ajouter comme membres
    tous_les_utilisateurs = User.objects.exclude(id__in=projet.membres.all())

    return render(request, 'core/projet_details.html', {
        'projet': projet,
        'taches': taches,
        'utilisateurs': tous_les_utilisateurs
    })


@login_required
def ajouter_membre(request, projet_id):
    if request.method == "POST":
        projet = get_object_or_404(Projet, id=projet_id)
        user_id = request.POST.get('user_id')
        user_a_ajouter = get_object_or_404(User, id=user_id)
        projet.membres.add(user_a_ajouter)
    return redirect('projet_details', projet_id=projet_id)


# Vue pour la connexion avec notre design personnalisé
class CustomLoginView(LoginView):
    template_name = 'core/login.html'


@login_required
def dashboard(request):
    # On récupère les projets où l'utilisateur est soit créateur, soit membre
    projets = Projet.objects.filter(membres=request.user) | Projet.objects.filter(createur=request.user)

    # Calcul de la prime si c'est un professeur
    prime = request.user.calculer_prime() if request.user.role == 'PROFESSEUR' else 0

    return render(request, 'core/dashboard.html', {
        'projets': projets.distinct().order_by('-date_creation'),
        'prime': prime
    })


@login_required
def creer_projet(request):
    if request.method == "POST":
        nom = request.POST.get('nom')
        description = request.POST.get('description')

        if nom:
            # Création du projet dans la base MySQL
            nouveau_projet = Projet.objects.create(
                nom=nom,
                description=description,
                createur=request.user
            )
            # On ajoute automatiquement le créateur comme membre du projet
            nouveau_projet.membres.add(request.user)

            # Redirection vers le dashboard pour voir le nouveau projet
            return redirect('dashboard')

    return redirect('dashboard')  # Sécurité : si on accède en GET, on renvoie au dashboard


@login_required
def creer_tache(request, projet_id):
    projet = get_object_or_404(Projet, id=projet_id)
    if request.method == "POST":
        titre = request.POST.get('titre')
        description = request.POST.get('description')
        assigne_a_id = request.POST.get('assigne_a')
        date_limite = request.POST.get('date_limite')

        assigne_a = get_object_or_404(User, id=assigne_a_id)

        # LOGIQUE MÉTIER : Un étudiant ne peut pas assigner un prof
        if request.user.role == 'ETUDIANT' and assigne_a.role == 'PROFESSEUR':
            # On pourrait ajouter un message d'erreur ici
            return redirect('projet_details', projet_id=projet.id)

        Tache.objects.create(
            titre=titre,
            description=description,
            projet=projet,
            assigne_a=assigne_a,
            date_limite=date_limite,
            statut='A_FAIRE'
        )
    return redirect('projet_details', projet_id=projet.id)


@login_required
def changer_statut_tache(request, tache_id, nouveau_statut):
    tache = get_object_or_404(Tache, id=tache_id)

    # Sécurité : Seuls les membres du projet peuvent modifier les tâches
    if request.user in tache.projet.membres.all() or request.user == tache.projet.createur:
        tache.statut = nouveau_statut

        # Si la tâche est terminée, on enregistre l'heure précise
        if nouveau_statut == 'TERMINE':
            tache.date_fin_reelle = timezone.now()

        tache.save()

    return redirect('projet_details', projet_id=tache.projet.id)


@login_required
def dashboard(request):
    # On récupère les projets où l'utilisateur est membre ou créateur
    projets = Projet.objects.filter(membres=request.user).distinct()

    total_prime = 0
    if request.user.role == 'PROFESSEUR':
        for projet in projets:
            total_prime += projet.calculer_prime_totale()

    return render(request, 'core/dashboard.html', {
        'projets': projets,
        'prime': total_prime,  # On envoie le montant total au template
        'utilisateurs': User.objects.all()

    })


@login_required
def supprimer_projet(request, projet_id):
    projet = get_object_or_404(Projet, id=projet_id)

    # Sécurité : Seul le créateur peut supprimer
    if projet.createur == request.user:
        projet.delete()
        messages.success(request, "Le projet a été supprimé avec succès.")
    else:
        messages.error(request, "Vous n'avez pas les droits pour supprimer ce projet.")

    return redirect('dashboard')
@login_required
def live_stats(request):
    return render(request, 'core/live_stats.html')