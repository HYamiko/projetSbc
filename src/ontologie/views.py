from pyexpat.errors import messages

from django.shortcuts import render
from .graphdb_requete import *

# Create your views here.
def Acccueil(request):
    recherche = request.GET
    print(recherche)
    resultats = recherche_universites('')
    print(resultats)
#    universites = [result['universite']["value"] for result in resultats["results"]["bindings"]]
    #for element in universites:
      #  print(element)
    return render(request, 'index.html', {"resultat": resultats})


def accueil(request):
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



    return render(request, 'index.html', {
        'recherche': recherche,
        'cle': cle,
        'clePersonnel': cle_personnel,
        'cleUniversite': cle_universite,
        'cleProgramme': cle_programme,
        'resultats': resultats,
        'erreur':error,
        'message':message
    })