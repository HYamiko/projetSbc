from pyexpat.errors import messages

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .graphdb_requete import *


def index(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            error_message = 'Veuillez entrer une adresse E-mail et un mot de passe.'
            return render(request, "login.html", {'error':True,'error_message': error_message})

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')  # Rediriger vers la page d'accueil ou une autre page après connexion
        else:
            error_message = 'Adresse E-mail ou mot de passe incorrect.'
            return render(request, "login.html", { 'error':True, 'error_message': error_message})

    return render(request, "login.html")


@login_required(login_url='/login/')
def deconnexion(request):
    logout(request)
    return redirect('/')

@login_required(login_url='/login/')
def home(request):
    recherche = ''
    cle = ''
    cle_personnel = ''
    cle_universite = ''
    cle_programme = ''
    resultats = []
    error = False
    message = ""

    if request.method == 'POST':
        recherche = request.POST.get('recherche')
        cle = request.POST.get('cle')
        if cle == '':
            error = True
            message = "Choisissez une clé pour la recherche"
        else:
            if cle == 'UNIVERSITE':
                resultats = recherche_universites(recherche)
            elif cle == 'PROGRAMME':
                resultats = recherche_programmes(recherche)
            elif cle == 'ENSEIGNANT':
                resultats = recherche_enseignant_cours_universite(recherche)
            elif cle == 'ENSEIGNANT-ETUDIANT':
                resultats = recherche_enseignant_etudiant(recherche)
            elif cle == 'PERSONNEL':
                cle_universite = request.POST.get('cleUniversite')
                cle_personnel = request.POST.get('clePersonnel')
                if cle_personnel is None:
                    cle_personnel =''
                if cle_universite is None:
                    cle_universite = ''
                resultats = recherche_personnel(recherche,cle_universite,cle_personnel)
            elif cle == 'ETUDIANT':
                cle_universite = request.POST.get('cleUniversite')
                cle_programme = request.POST.get('cleProgramme')
                if cle_universite is None:
                    cle_universite = ''
                if cle_programme is None:
                    cle_programme = ''
                resultats = recherche_etudiant(recherche,cle_universite,cle_programme)
            else:
                recherche = []



    return render(request, 'home.html', {
        'recherche': recherche,
        'cle': cle,
        'clePersonnel': cle_personnel,
        'cleUniversite': cle_universite,
        'cleProgramme': cle_programme,
        'resultats': resultats,
        'erreur':error,
        'message':message
    })