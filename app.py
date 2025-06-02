import streamlit as st
import random
import json
from reco_engine import reco_engine_sfar  # Appel du moteur depuis le fichier séparé

# Chargement du mapping à partir d'un fichier JSON
with open("mapping_reco_algorithmes.json", "r", encoding="utf-8") as f:
    label_to_code = json.load(f)

# Identités fictives
identities = [
    {"nom": "Durand", "prenom": "Claire", "ddn": "1967-08-14", "sexe": "F"},
    {"nom": "Martin", "prenom": "Luc", "ddn": "1959-03-22", "sexe": "M"},
    {"nom": "Bernard", "prenom": "Sophie", "ddn": "1975-11-09", "sexe": "F"},
    {"nom": "Petit", "prenom": "Julien", "ddn": "1983-01-02", "sexe": "M"},
    {"nom": "Moreau", "prenom": "Isabelle", "ddn": "1990-06-30", "sexe": "F"}
]

# Exemple d'interventions
chirurgies = [
    "Prothèse totale de hanche", "Colectomie droite", "Hystérectomie","Lobectomie pulmonaire",
    "Néphrectomie partielle", "Thyroïdectomie", "Pontage aorto-bifémoral", "Pontage carotidien"
]

# Liste d'interventions vasculaires (non fonctionnel...)
chirurgies_vasculaires = ["Pontage aorto-bifémoral", "Pontage carotidien", "Endartériectomie fémorale"]

if "identity" not in st.session_state:
    st.session_state["identity"] = random.choice(identities)
identity = st.session_state["identity"]

st.title("🩺 Exemple intégration mapping CPA")

with st.expander("1. Identité du patient", expanded=True):
    st.text_input("Nom", value=identity["nom"])
    st.text_input("Prénom", value=identity["prenom"])
    st.date_input("Date de naissance", value=identity["ddn"])
    st.selectbox("Sexe", ["F", "M"], index=0 if identity["sexe"] == "F" else 1)

with st.expander("2. Données chirurgicales"):
    intervention = st.selectbox("Intitulé de l'intervention", chirurgies, key="intervention")
    urgence = st.radio("Urgence chirurgicale ?", ["Oui", "Non"], horizontal=True, key="urgence")
    risque = st.selectbox("Risque cardiovasculaire estimé de la chirurgie", ["Risque faible", "Risque modéré", "Risque élevé"], key="risque")
    chirurgie_vasculaire = intervention in chirurgies_vasculaires
    chirurgie_vasculaire_input = st.radio("S'agit-il d'une chirurgie vasculaire ?", ["Oui", "Non"], index=0 if chirurgie_vasculaire else 1,horizontal=True)


with st.expander("4. Évaluation cardiovasculaire"):
    coronarien = st.radio("Coronarien connu", ["Oui", "Non"], horizontal=True)
    coronaropathie = "Non"
    if coronarien == "Oui":
        coronaropathie = st.radio("Stabilité de la coronaropathie", ["Coronaropathie stable", "Coronaropathie instable"], horizontal=True)
    st.markdown("**Score de Lee (facteurs cliniques)**")
    lee_score = sum([
        st.checkbox("Chirurgie à haut risque"),
        st.checkbox("Cardiopathie ischémique"),
        st.checkbox("Insuffisance cardiaque"),
        st.checkbox("ATCD AVC/AIT"),
        st.checkbox("Diabète insulinotraité"),
        st.checkbox("Insuffisance rénale")
    ])
    st.markdown(f"**Score de Lee clinique : {lee_score}**")
    met = st.selectbox("Capacité fonctionnelle (MET)", ["MET < 4", "MET ≥ 4", "MET inévaluable"])
    st.markdown("**Test d’ischémie**")
    test = st.radio("Test d’ischémie réalisé ?", ["Non réalisé", "Test d’ischémie positif", "Test d’ischémie négatif", "Test d’ischémie douteux"], horizontal=True)

# Appel fonction de recommandation
if st.button("Générer la recommandation"):
    inputs = {
        "Chirurgie urgente": "Chirurgie urgente" if urgence == "Oui" else "",
        "Risque": risque,
        "Coronaropathie": coronaropathie,
        "MET": met,
        "Test": test,
        "Score de Lee" : lee_score
      
    }
    inputs["chirurgie vasculaire"] = "chirurgie vasculaire" if chirurgie_vasculaire_input == "Oui" else "non"
    if chirurgie_vasculaire:
        inputs["chirurgie vasculaire"] = "chirurgie vasculaire"

    codes = {label_to_code[v.strip()]: label_to_code[v.strip()] for v in inputs.values() if isinstance(v, str) and v.strip() in label_to_code}
    if isinstance(inputs.get("Score de Lee"), int):
        codes["CV02.1"] = inputs["Score de Lee"]
    result = reco_engine_sfar(codes)
    if isinstance(result, list):
        result = {"recommandation": result[0] if result else "Aucune recommandation disponible", "code": "", "justification": list(codes.keys())}
    with st.sidebar:
        st.header("📝 Recommandation")
        st.success(result.get("recommandation", "Aucune recommandation disponible"))
        st.caption(f"Code de branche : {result.get('code', 'Non spécifié')}")
        st.markdown("**Justification (codes SFAR)**")
        for j in result.get("justification", []):
            st.code(j)
