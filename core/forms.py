from django import forms
from django.contrib.auth.forms import UserCreationForm
from core.models import User, Annonce  # <-- Importe ton modèle personnalisé
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Annonce
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import RendezVous
from django.utils import timezone

# Login Form
class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label='Nom d’utilisateur',
        widget=forms.TextInput(attrs={'placeholder': 'Nom d’utilisateur'})
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe'})
    )

# Registration Form with role choice
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        label='Vous êtes :',
        widget=forms.RadioSelect  # ou forms.Select pour une liste déroulante
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user


class AnnonceForm(forms.ModelForm):
    class Meta:
        model = Annonce
        fields = ['titre', 'description', 'prix', 'localisation', 'image']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de l’annonce'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'prix': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Prix'}),
            'localisation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Localisation'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }




# Vérifie que l'utilisateur est un propriétaire
class ProprioRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'proprietaire'

# Liste des annonces (propriétaire)
class AnnonceListView(LoginRequiredMixin, ProprioRequiredMixin, ListView):
    model = Annonce
    template_name = 'core/mes_annonces.html'
    context_object_name = 'annonces'

    def get_queryset(self):
        return Annonce.objects.filter(proprietaire=self.request.user)

# Créer une annonce
class AnnonceCreateView(LoginRequiredMixin, ProprioRequiredMixin, CreateView):
    model = Annonce
    template_name = 'core/create_annonce.html'
    fields = ['titre', 'description', 'prix', 'localisation', 'image']
    success_url = reverse_lazy('annonce_list')

    def form_valid(self, form):
        form.instance.proprietaire = self.request.user
        return super().form_valid(form)

# Modifier une annonce
class AnnonceUpdateView(LoginRequiredMixin, ProprioRequiredMixin, UpdateView):
    model = Annonce
    template_name = 'core/update_annonce.html'
    fields = ['titre', 'description', 'prix', 'localisation', 'image']
    success_url = reverse_lazy('annonce_list')

    def get_queryset(self):
        return Annonce.objects.filter(proprietaire=self.request.user)

# Supprimer une annonce
class AnnonceDeleteView(LoginRequiredMixin, ProprioRequiredMixin, DeleteView):
    model = Annonce
    template_name = 'core/delete_annonce.html'
    success_url = reverse_lazy('annonce_list')

    def get_queryset(self):
        return Annonce.objects.filter(proprietaire=self.request.user)


class RendezVousForm(forms.ModelForm):
    client_phone = forms.CharField(
        label="Votre numéro de téléphone",
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Pour que le propriétaire puisse vous contacter',
            'class': 'form-control'
        })
    )
    client_name = forms.CharField(
        label="Votre nom complet",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = RendezVous
        fields = ['date_rdv', 'duree', 'notes', 'client_phone', 'client_name']
        widgets = {
            'date_rdv': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Précisez vos disponibilités alternatives...'
            }),
        }

class RendezVousUpdateForm(forms.ModelForm):
    proprietaire_phone = forms.CharField(
        label="Votre numéro de téléphone",
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Pour que le client puisse vous contacter',
            'class': 'form-control'
        })
    )
    proprietaire_name = forms.CharField(
        label="Votre nom",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = RendezVous
        fields = ['statut', 'proprietaire_phone', 'proprietaire_name', 'notes']
        widgets = {
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Informations complémentaires...'
            }),
        }