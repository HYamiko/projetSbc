import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin

GRAPHDB_ENDPOINT = "http://graphdb-1036093977621.us-central1.run.app/repositories/projet-sbc"
GRAPHDB_USER = "ontouniv"
GRAPHDB_PASSWORD = "azertyAZERTY@#"


def extract_local_name(uri):
    if '#' in uri:
        return uri.split('#')[-1]
    return uri.split('/')[-1]




def requete_graphdb(sparql_query):
    base_url = "https://graphdb-1036093977621.us-central1.run.app/"
    endpoint = urljoin(base_url, "repositories/projet-sbc")

    headers = {
        "Accept": "application/sparql-results+json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(
            endpoint,
            headers=headers,
            auth=HTTPBasicAuth(GRAPHDB_USER, GRAPHDB_PASSWORD),
            data=f"query={sparql_query}",  # Format critique
            timeout=30,
            allow_redirects=False
        )

        if response.status_code == 302:
            redirect_url = response.headers['Location']
            response = requests.post(
                redirect_url,
                headers=headers,
                auth=HTTPBasicAuth(GRAPHDB_USER, GRAPHDB_PASSWORD),
                data=f"query={sparql_query}",
                timeout=30
            )

        # 5. Validation de la réponse
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = f"{response.status_code} - {response.text[:200]}"
            raise Exception(f"Erreur serveur : {error_msg}")

    except requests.exceptions.RequestException as e:
        raise Exception(f"Erreur réseau : {str(e)}")
    except Exception as e:
        raise Exception(f"Erreur inattendue : {str(e)}")

def recherche_universites(search_param):
    search_param = search_param.strip()
    query = f"""
        PREFIX tp3-3: <http://www.semanticweb.org/yamiko/ontologies/2024/11/tp3-3#>        
            SELECT ?nomUniversite ?universite
            WHERE {{
              ?universite tp3-3:NomUniversite ?nomUniversite .
              FILTER(CONTAINS(LCASE(?nomUniversite), LCASE("{search_param}")))
            }}
    """

    resultats = requete_graphdb(query)
    clean_results = []
    for binding in resultats['results']['bindings']:
        clean_results.append({
            'nomUniversite': extract_local_name(binding['nomUniversite']['value']),
            'universite': extract_local_name(binding['universite']['value'])
        })
    return clean_results



def recherche_programmes(search_param):
    search_param = search_param.strip()
    query = f"""
        PREFIX tp3-3: <http://www.semanticweb.org/yamiko/ontologies/2024/11/tp3-3#>

        SELECT ?nomProgramme ?nomUniversite
        WHERE {{
          ?universite tp3-3:offre ?programme ;
                      tp3-3:NomUniversite ?nomUniversite .
          ?programme tp3-3:NomProgramme ?nomProgramme .
          FILTER(
            CONTAINS(LCASE(?nomUniversite), LCASE("{search_param}")) ||
            CONTAINS(LCASE(?nomProgramme), LCASE("{search_param}"))
          )
        }}
        ORDER BY ?nomProgramme
    """
    results = requete_graphdb(query)

    clean_results = []
    for binding in results['results']['bindings']:
        clean_results.append({
            'programme': extract_local_name(binding['nomProgramme']['value']),
            'universite': extract_local_name(binding['nomUniversite']['value'])
        })

    return clean_results



def recherche_enseignant_cours_universite(search_param):
    search_param = search_param.strip()
    query = f"""
       PREFIX tp3-3: <http://www.semanticweb.org/yamiko/ontologies/2024/11/tp3-3#>
        SELECT ?nomEnseignant ?nomCours ?nomUniversite
        WHERE {{
          ?enseignant a tp3-3:PersonnelEnseignant ;
                      	tp3-3:enseigne ?cours;
        				tp3-3:NomPersonne ?nomEnseignant.
          ?cours tp3-3:universiteCours ?universite;
        		 tp3-3:NomCours ?nomCours.
          ?universite tp3-3:NomUniversite ?nomUniversite.
        FILTER(CONTAINS(LCASE(?nomEnseignant), LCASE("{search_param}")))
        }}
        ORDER BY ?nomEnseignant
    """
    results = requete_graphdb(query)

    clean_results = []
    for binding in results['results']['bindings']:
        clean_results.append({
            'enseignant': extract_local_name(binding['nomEnseignant']['value']),
            'cours': extract_local_name(binding['nomCours']['value']),
            'universite': extract_local_name(binding['nomUniversite']['value'])
        })

    return clean_results


def recherche_enseignant_etudiant(search_param):
    search_param = search_param.strip()
    query = f"""
         PREFIX tp3-3: <http://www.semanticweb.org/yamiko/ontologies/2024/11/tp3-3#>
            SELECT ?nomEnseignant ?nomProgramme ?nomUniversite
                WHERE {{
                  ?enseignant a tp3-3:PersonnelEnseignant ;
                              a tp3-3:Etudiant ;
                                tp3-3:estInscritA ?programmeUniversite;
                                tp3-3:NomPersonne ?nomEnseignant.
                    ?programmeUniversite tp3-3:inscritUniversite ?universite;
                                            tp3-3:inscritProgramme ?programme.
                    ?universite tp3-3:NomUniversite ?nomUniversite.
                    ?programme tp3-3:NomProgramme ?nomProgramme.
                 FILTER(CONTAINS(LCASE(?nomEnseignant), LCASE("{search_param}")))
                }}
                
                ORDER BY ?nomEnseignant
    """
    results = requete_graphdb(query)

    clean_results = []
    for binding in results['results']['bindings']:
        clean_results.append({
            'enseignant': extract_local_name(binding['nomEnseignant']['value']),
            'programme': extract_local_name(binding['nomProgramme']['value']),
            'universite': extract_local_name(binding['nomUniversite']['value'])
        })

    return clean_results


def recherche_personnel(recherche, nom_universite, type_personnel):
    recherche = recherche.strip()
    nom_universite = nom_universite.strip()
    type_personnel = type_personnel.strip()

    filter_conditions = []

    if recherche:
        filter_conditions.append(f'CONTAINS(LCASE(?nomPersonnel), LCASE("{recherche}"))')

    if nom_universite:
        filter_conditions.append(f'CONTAINS(LCASE(?nomUniversite), LCASE("{nom_universite}"))')

    if type_personnel:
        type_filter = {
            'enseignant': 'Personnel enseignant',
            'appui': 'Personnel d\'appui'
        }.get(type_personnel.lower(), type_personnel)
        filter_conditions.append(f'CONTAINS(LCASE(?typePersonnel), LCASE("{type_filter}"))')

    query = f"""
    PREFIX tp3-3: <http://www.semanticweb.org/yamiko/ontologies/2024/11/tp3-3#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?nomPersonnel ?typePersonnel ?nomUniversite
    WHERE {{
      {{
        ?personnel a/rdfs:subClassOf* tp3-3:PersonnelEnseignant ;
                   tp3-3:NomPersonne ?nomPersonnel .
        BIND("Personnel enseignant" AS ?typePersonnel)

        ?affiliation a tp3-3:PersonnelEnseignantUniversite ;
                     tp3-3:estPersonnelEnseignant ?personnel ;
                     tp3-3:estPersonnelDans ?universite .
      }}
      UNION
      {{
        ?personnel a/rdfs:subClassOf* tp3-3:PersonnelAppui ;
                   tp3-3:NomPersonne ?nomPersonnel .
        BIND("Personnel d'appui" AS ?typePersonnel)

        ?affiliation a tp3-3:PersonnelAppuiUniversite ;
                     tp3-3:estPersonnelAppui ?personnel ;
                     tp3-3:estPersonnelDans ?universite .
      }}

      ?universite tp3-3:NomUniversite ?nomUniversite .
      {f"FILTER({' && '.join(filter_conditions)})" if filter_conditions else ""}
    }}
    ORDER BY ?nomPersonnel
    """

    try:
        results = requete_graphdb(query)
        clean_results = []
        for binding in results['results']['bindings']:
            clean_results.append({
                'nomPersonnel': extract_local_name(binding['nomPersonnel']['value']),
                'typePersonnel': binding['typePersonnel']['value'],  # On garde la valeur originale
                'nomUniversite': extract_local_name(binding['nomUniversite']['value'])
            })
        return clean_results
    except Exception as e:
        raise Exception(f"Erreur lors de la recherche du personnel: {str(e)}")

def recherche_etudiant(search_param, nom_universite, nom_programme):
    search_param = search_param.strip()
    nom_universite = nom_universite.strip()
    nom_programme = nom_programme.strip()

    filters = []

    if search_param:
        filters.append(
            f'(CONTAINS(LCASE(?matricule), LCASE("{search_param}")) || CONTAINS(LCASE(?nomEtudiant), LCASE("{search_param}"))')

    if nom_universite:
        filters.append(f'CONTAINS(LCASE(?nomUniversite), LCASE("{nom_universite}"))')

    if nom_programme:
        filters.append(f'CONTAINS(LCASE(?nomProgramme), LCASE("{nom_programme}"))')

    query = f"""
    PREFIX tp3-3: <http://www.semanticweb.org/yamiko/ontologies/2024/11/tp3-3#>
    SELECT ?matricule ?nomEtudiant ?nomProgramme ?nomUniversite
    WHERE {{
      ?enseignant a tp3-3:Etudiant ;
                  tp3-3:estInscritA ?programmeUniversite;
                  tp3-3:NomPersonne ?nomEtudiant;
                  tp3-3:MatriculeEtudiant ?matricule.
      ?programmeUniversite tp3-3:inscritUniversite ?universite;
                           tp3-3:inscritProgramme ?programme.
      ?universite tp3-3:NomUniversite ?nomUniversite.
      ?programme tp3-3:NomProgramme ?nomProgramme.
      {"FILTER(" + " && ".join(filters) + ")" if filters else ""}
    }}
    ORDER BY ?nomEtudiant
    """

    try:
        results = requete_graphdb(query)
        clean_results = []
        for binding in results['results']['bindings']:
            clean_results.append({
                'etudiant': extract_local_name(binding['nomEtudiant']['value']),
                'matricule': extract_local_name(binding['matricule']['value']),
                'programme': extract_local_name(binding['nomProgramme']['value']),
                'universite': extract_local_name(binding['nomUniversite']['value'])
            })
        return clean_results
    except Exception as e:
        raise Exception(f"Erreur lors de la recherche : {str(e)}")