from django.contrib.auth.decorators import login_required
from django.core.mail import message
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views import View

from .forms import LoginForm, RegistrationForm, RendezVousForm, RendezVousUpdateForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Annonce, User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView
from .models import RendezVous
from django.core.exceptions import PermissionDenied
from django.views.generic import DeleteView
from django.contrib import messages


#gestion annonces
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Annonce
from .forms import AnnonceForm
from django.views.generic import ListView
def accueil(request):
    annonces = Annonce.objects.all().order_by('-date_postee')
    return render(request, 'core/acceuil.html', {'annonces': annonces})

def annonce_detail(request, pk):
    annonce = get_object_or_404(Annonce, pk=pk)
    return render(request, 'core/annonce_detail.html', {'annonce': annonce})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accueil')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenue {username} ! Vous êtes maintenant connecté.")
                return redirect('accueil')
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")
        return render(request, 'core/login.html', {'form': form})

    return render(request, 'core/login.html', {'form': LoginForm()})


@login_required
def logout_view(request):
    username = request.user.username
    logout(request)
    messages.success(request, f"Vous avez été déconnecté avec succès. À bientôt {username} !")
    return redirect('accueil')


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Compte créé avec succès ! Bienvenue {user.username}.")
            return redirect('accueil')
        return render(request, 'core/register.html', {'form': form})
    return render(request, 'core/register.html', {'form': RegistrationForm()})


def client_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'client':
        return redirect('login')

    return render(request, 'core/client_dashboard.html')

def proprietaire_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'proprietaire':
        return redirect('login')

    context = {
        'annonces': Annonce.objects.filter(proprietaire=request.user).order_by('-date_postee')[:5]
    }
    return render(request, 'core/proprietaire_dashboard.html', context)


# views.py

def dashboard_view(request):
    if request.user.role == 'proprietaire':
        return render(request, 'core/proprietaire_dashboard.html')
    else:
        return render(request, 'core/client_dashboard.html')




# Gestion des annonces
class MesAnnoncesView(LoginRequiredMixin, ListView):
    model = Annonce
    template_name = 'core/mes_annonces.html'
    context_object_name = 'annonces'

    def get_queryset(self):
        return Annonce.objects.filter(proprietaire=self.request.user)

class AnnonceCreateView(LoginRequiredMixin, CreateView):
    model = Annonce
    form_class = AnnonceForm
    template_name = 'core/create_annonce.html'
    success_url = reverse_lazy('mes_annonces')

    def form_valid(self, form):
        form.instance.proprietaire = self.request.user
        return super().form_valid(form)

class AnnonceUpdateView(LoginRequiredMixin, UpdateView):
    model = Annonce
    form_class = AnnonceForm
    template_name = 'core/update_annonce.html'
    success_url = reverse_lazy('mes_annonces')

class AnnonceDeleteView(LoginRequiredMixin, DeleteView):
    model = Annonce
    template_name = 'core/delete_annonce.html'
    success_url = reverse_lazy('mes_annonces')



class AnnonceListView(ListView):
    model = Annonce
    template_name = 'core/annonce_list.html'
    context_object_name = 'annonces'
    paginate_by = 10  # Optionnel

    def get_queryset(self):
        queryset = super().get_queryset()

        # Get search parameters from URL
        location = self.request.GET.get('location')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')

        # Build filters dynamically
        filters = Q()

        if location:
            filters &= Q(localisation__icontains=location)

        if min_price:
            filters &= Q(prix__gte=min_price)  # gte = greater than or equal

        if max_price:
            filters &= Q(prix__lte=max_price)  # lte = less than or equal

        return queryset.filter(filters).order_by('-date_postee')


#Rendez vous
class CreateRendezVousView(LoginRequiredMixin, CreateView):
    form_class = RendezVousForm
    template_name = 'core/creer_rdv.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.role == 'client':
            raise PermissionDenied("Seuls les clients peuvent prendre rendez-vous")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        annonce = get_object_or_404(Annonce, pk=self.kwargs['annonce_id'])
        form.instance.client = self.request.user
        form.instance.annonce = annonce
        form.instance.client_name = form.cleaned_data['client_name']
        form.instance.client_phone = form.cleaned_data['client_phone']
        response = super().form_valid(form)
        messages.success(self.request, "Rendez-vous créé avec succès!")
        return response

    def get_success_url(self):
        return reverse('mes_rdv')  # Redirect to client's appointments page


class RendezVousUpdateView(LoginRequiredMixin, UpdateView):
    form_class = RendezVousUpdateForm
    template_name = 'core/proprietaire/rendezvous_update.html'

    def form_valid(self, form):
        form.instance.proprietaire_name = form.cleaned_data['proprietaire_name']
        form.instance.proprietaire_phone = form.cleaned_data['proprietaire_phone']
        messages.success(self.request, "Rendez-vous mis à jour avec succès")
        return super().form_valid(form)

    model = RendezVous
    queryset = RendezVous.objects.all()  # Base queryset

    def get_queryset(self):
        """Restrict to only the owner's appointments"""
        qs = super().get_queryset()
        return qs.filter(annonce__proprietaire=self.request.user)

    def form_valid(self, form):
        form.instance.proprietaire_name = form.cleaned_data['proprietaire_name']
        form.instance.proprietaire_phone = form.cleaned_data['proprietaire_phone']
        messages.success(self.request, "Rendez-vous mis à jour avec succès")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('mes_rdv')
class MesRendezVousView(LoginRequiredMixin, ListView):
    model = RendezVous
    template_name = 'core/mes_rdv.html'
    context_object_name = 'rendezvous'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'client':
            return RendezVous.objects.filter(
                client=user,
                statut__in=['confirme', 'en_attente']
            ).select_related('annonce', 'annonce__proprietaire').order_by('-date_rdv')
        elif user.role == 'proprietaire':
            return RendezVous.objects.filter(
                annonce__proprietaire=user,
                statut__in=['confirme', 'en_attente']
            ).select_related('annonce', 'client').order_by('-date_rdv')
        return RendezVous.objects.none()

    def post(self, request, *args, **kwargs):
        if 'delete_rdv' in request.POST:
            rdv_id = request.POST.get('rdv_id')
            rdv = get_object_or_404(RendezVous, id=rdv_id, client=request.user)
            rdv.delete()
            messages.success(request, "Le rendez-vous a été supprimé avec succès")
        return redirect('mes_rdv')


class AnnulerRendezVousView(LoginRequiredMixin, View):
    template_name = 'core/confirmer_annulation.html'

    def dispatch(self, request, *args, **kwargs):
        self.rdv = get_object_or_404(RendezVous, pk=kwargs['pk'])

        # Vérifie que l'utilisateur est autorisé
        if not (request.user == self.rdv.client or request.user == self.rdv.annonce.proprietaire):
            messages.error(request, "Vous n'avez pas la permission d'annuler ce rendez-vous")
            return redirect('mes_rdv')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Affiche le formulaire de confirmation
        return render(request, self.template_name, {'object': self.rdv})

    def post(self, request, *args, **kwargs):
        # Annule le rendez-vous
        self.rdv.statut = 'annule'
        raison = request.POST.get('raison')
        # Si tu veux l'enregistrer, ajoute la logique ici
        self.rdv.save()

        messages.success(request, "Le rendez-vous a été annulé avec succès.")
        return redirect('mes_rdv')



class SupprimerRendezvousView(DeleteView):
    model = RendezVous
    success_url = reverse_lazy('proprietaire_rendezvous_list')
    template_name = 'supprimer_rendezvous.html'


# Dans views.py
class ConfirmerRendezVousView(LoginRequiredMixin, View):
    def post(self, request, pk):
        rdv = get_object_or_404(RendezVous, pk=pk, annonce__proprietaire=request.user)
        rdv.statut = 'confirme'
        rdv.save()
        messages.success(request, "Le rendez-vous a été confirmé")
        return redirect('proprietaire_rendezvous_list')