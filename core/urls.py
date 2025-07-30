from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from .views import (
    register_view,
    login_view,
    AnnonceCreateView,
    MesAnnoncesView,
    AnnonceUpdateView,
    AnnonceDeleteView,
    AnnonceListView, CreateRendezVousView,
    MesRendezVousView,
    SupprimerRendezvousView,
    AnnulerRendezVousView, RendezVousUpdateView, logout_view,
    ConfirmerRendezVousView

)

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('connexion/', views.login_view, name='login'),
    path('deconnexion/', views.logout_view, name='logout'),
    path('inscription/', views.register_view, name='register'),
    path('client/dashboard/', views.client_dashboard, name='client_dashboard'),
    path('proprietaire/dashboard/', views.proprietaire_dashboard, name='proprietaire_dashboard'),
    path('annonce/<int:pk>/', views.annonce_detail, name='annonce_detail'),

    # URLs pour les annonces
    path('mes-annonces/', MesAnnoncesView.as_view(), name='mes_annonces'),
    path('creer/', AnnonceCreateView.as_view(), name='create_annonce'),
    path('annonces/<int:pk>/modifier/', AnnonceUpdateView.as_view(), name='update_annonce'),
    path('annonces/<int:pk>/supprimer/', AnnonceDeleteView.as_view(), name='delete_annonce'),
    path('annonces/', AnnonceListView.as_view(), name='annonce_list'),

    #RendezVous
    path('annonce/<int:annonce_id>/prendre-rendezvous/', CreateRendezVousView.as_view(), name='creer_rdv'),
    path('mes_rdv/', MesRendezVousView.as_view(), name='mes_rdv'),
    path('rendezvous/<int:pk>/annuler/',
         AnnulerRendezVousView.as_view(),
         name='confirmer_annulation'),
    path('proprietaire/rendezvous/', MesRendezVousView.as_view(), name='mes_rdv.html'),
    path('rendezvous/<int:pk>/modifier/', RendezVousUpdateView.as_view(), name='modifier_rendezvous'),
    path('client/mes-rendezvous/', MesRendezVousView.as_view(), name='mes_rdv.html'),
    path('rendezvous/<int:pk>/supprimer/', SupprimerRendezvousView.as_view(), name='supprimer_rendezvous'),
    path('rendezvous/<int:pk>/annuler/', AnnulerRendezVousView.as_view(), name='confirmer_annulation'),
    path('rendezvous/<int:pk>/confirmer/', ConfirmerRendezVousView.as_view(), name='confirmer_rendezvous'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
