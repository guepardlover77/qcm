import streamlit as st
import json
import os
DATA_FILE = "questions_reponses.json"

def charger_donnees():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"questions": []}


def sauvegarder_donnees(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def ajouter_question(question, images_paths):
    data = charger_donnees()
    data["questions"].append({
        "question": question,
        "reponses": [],
        "images": images_paths  # Nouveau champ pour stocker les chemins d'images
    })
    sauvegarder_donnees(data)




def ajouter_reponse(index_question, reponse, images_paths):
    data = charger_donnees()
    data["questions"][index_question]["reponses"].append({
        "texte": reponse,
        "like": 0,
        "dislike": 0,
        "images": images_paths  # Nouveau champ pour stocker les chemins d'images
    })
    sauvegarder_donnees(data)

def mettre_a_jour_score(index_question, index_reponse, action):
    data = charger_donnees()
    if action == "like":
        data["questions"][index_question]["reponses"][index_reponse]["like"] += 1
    elif action == "dislike":
        data["questions"][index_question]["reponses"][index_reponse]["dislike"] += 1
    sauvegarder_donnees(data)

def sauvegarder_image(image, nom_fichier):
    dossier = os.path.dirname(nom_fichier)
    if not os.path.exists(dossier):
        os.makedirs(dossier)

    with open(nom_fichier, "wb") as f:
        f.write(image.getbuffer())


def ajouter_images(images, prefix, idx):
    image_paths = []
    if images:
        for image_index, image in enumerate(images):
            # Créer un nom de fichier unique basé sur l'index et le temps
            image_path = f"images/{prefix}_{idx}_{image_index}.jpg"
            sauvegarder_image(image, image_path)
            image_paths.append(image_path)
    return image_paths

st.set_page_config(
    page_title="FAQ Anonyme - Médecine et Biophysique",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="auto"
)

st.title("🩺 Foire Aux Questions Anonyme")
st.markdown("""
Oyé oyé preux chevaliers. Vous avez ici de quoi parler entre vous anonymement donc posez vos questions bêtes !!!! L'idée c'est, d'une part que les tuteurs vous répondent mais aussi que vous parliez entre vous parce qu'on commence pas à jouer au foot avec Messi... Et à part cette FAQ (totalement anonyme, c'est important), vous pouvez toujours venir poser des questions aux @les_perdrisotopes sur insta !!! Allez kissou kissou et bon courage <3
""")



data = charger_donnees()
if data["questions"]:
    for idx, q in enumerate(data["questions"]):
        with st.expander(f"Question {idx + 1}: {q['question']}"):
            if "images" in q and q["images"]:
                for image_url in q["images"]:
                    st.image(image_url, use_column_width=True)
            if q["reponses"]:
                reponses_tries = sorted(q["reponses"], key=lambda rep: rep.get("like", 0), reverse=True)
                for rep_idx, rep in enumerate(reponses_tries):
                    if isinstance(rep, dict) and "texte" in rep:
                        texte_rep = rep["texte"]
                        like = rep["like"]
                        dislike = rep["dislike"]
                        st.write(f"Réponse {rep_idx + 1}: {texte_rep} (👍 {like}, 👎 {dislike})")
                        if "images" in rep and rep["images"]:
                            for image_url in rep["images"]:
                                st.image(image_url, use_column_width=True)
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"👍 J'aime ({like})", key=f"like_{idx}_{rep_idx}"):
                                mettre_a_jour_score(idx, rep_idx, "like")
                                st.rerun()
                        with col2:
                            if st.button(f"👎 Je n'aime pas ({dislike})", key=f"dislike_{idx}_{rep_idx}"):
                                mettre_a_jour_score(idx, rep_idx, "dislike")
                                st.rerun()
                    else:
                        st.error(f"Erreur dans la structure des données pour la réponse {rep_idx + 1}.")
            else:
                st.info("Aucune réponse pour cette question pour le moment.")
            nouvelle_reponse = st.text_area(f"Ajouter une réponse à la question {idx + 1}", key=f"reponse_{idx}")
            images_reponse = st.file_uploader(f"Joindre des images à la réponse {idx + 1} (facultatif)",
                                              accept_multiple_files=True, type=["png", "jpg", "jpeg"],
                                              key=f"images_reponse_{idx}")
            if st.button(f"Soumettre la réponse pour la question {idx + 1}", key=f"submit_reponse_{idx}"):
                if nouvelle_reponse.strip() != "":
                    images_paths = ajouter_images(images_reponse, "reponse", idx)  # Enregistrer les images
                    ajouter_reponse(idx, nouvelle_reponse.strip(), images_paths)
                    st.success("Votre réponse a été soumise avec succès !")
                else:
                    st.error("Veuillez entrer une réponse avant de soumettre.")
st.subheader("Poser une nouvelle question (Anonyme)")
nouvelle_question = st.text_area("Tapez votre question ici :", "", key="nouvelle_question")
images_question = st.file_uploader("Joindre des images à la question (facultatif)", accept_multiple_files=True,
                                   type=["png", "jpg", "jpeg"], key="images_question")
if st.button("Soumettre la question", key="submit_question"):
    if nouvelle_question.strip() != "":
        images_paths = ajouter_images(images_question, "question", len(data["questions"]))  # Enregistrer les images
        ajouter_question(nouvelle_question.strip(), images_paths)
        st.success("Votre question a été soumise de manière anonyme !")
    else:
        st.error("Veuillez entrer une question avant de soumettre.")

