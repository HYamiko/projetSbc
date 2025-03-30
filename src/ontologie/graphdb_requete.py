import requests
GRAPHDB_ENDPOINT = "http://localhost:7200/repositories/test-graph-db"


def extract_local_name(uri):
    if '#' in uri:
        return uri.split('#')[-1]
    return uri.split('/')[-1]


def requete_graphdb(sparql_query):
    headers = {"Accept": "application/sparql-results+json"}
    try:
        response = requests.post(
            GRAPHDB_ENDPOINT,
            headers=headers,
            data={"query": sparql_query},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"Erreur SPARQL : {str(e)}")


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



def recherche_personnel(recherche,nom_universite,type_personnel):
    recherche = recherche.strip()
    nom_universite= nom_universite.strip()
    type_personnel = type_personnel.strip()
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
              
              FILTER(
           ({"true" if not recherche else f'CONTAINS(LCASE(?nomPersonnel), LCASE("{recherche}"))'})
           &&
           ({"true" if not nom_universite else f'CONTAINS(LCASE(?nomUniversite), LCASE("{nom_universite}"))'})
           &&
           ({"true" if not type_personnel else f'CONTAINS(LCASE(?typePersonnel), LCASE("{type_personnel}"))'})
         )
            }}
            ORDER BY ?nomPersonnel
    """
    results = requete_graphdb(query)

    clean_results = []
    for binding in results['results']['bindings']:
        clean_results.append({
            'nomPersonnel': extract_local_name(binding['nomPersonnel']['value']),
            'typePersonnel': extract_local_name(binding['typePersonnel']['value']),
            'nomUniversite': extract_local_name(binding['nomUniversite']['value'])
        })

    return clean_results



def recherche_etudiant(search_param, nom_universite,nom_programme):
    search_param = search_param.strip()
    nom_universite = nom_universite.strip()
    nom_programme = nom_programme.strip()
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

      FILTER(
        ({"true" if not search_param else f'(CONTAINS(LCASE(?matricule), LCASE("{search_param}")) || CONTAINS(LCASE(?nomEtudiant), LCASE("{search_param}")))'})
        &&
        ({"true" if not nom_universite else f'CONTAINS(LCASE(?nomUniversite), LCASE("{nom_universite}"))'})
        &&
        ({"true" if not nom_programme else f'CONTAINS(LCASE(?nomProgramme), LCASE("{nom_programme}"))'})
      )
    }}
    ORDER BY ?nomEtudiant
    """
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
