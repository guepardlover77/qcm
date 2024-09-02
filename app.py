import streamlit as st
import json
import os

QCM_FILE = "qcm.json"
USERS = {"admin": "password123"}

def load_qcm():
    if os.path.exists(QCM_FILE):
        with open(QCM_FILE, "r", encoding="utf-8") as f:
            qcm_data = json.load(f)
            for qcm in qcm_data:
                if "category" not in qcm:
                    qcm["category"] = "maths"
            return qcm_data
    return []


def save_qcm(qcm_data):
    with open(QCM_FILE, "w", encoding="utf-8") as f:
        json.dump(qcm_data, f, indent=4)


def delete_qcm(qcm_index):
    qcm_data = load_qcm()
    if 0 <= qcm_index < len(qcm_data):
        qcm_data.pop(qcm_index)
        save_qcm(qcm_data)


def edit_qcm(qcm_index, question, options, correct_options):
    qcm_data = load_qcm()
    if 0 <= qcm_index < len(qcm_data):
        qcm_data[qcm_index]['question'] = question
        qcm_data[qcm_index]['choices'] = options
        qcm_data[qcm_index]['correct_options'] = correct_options
        save_qcm(qcm_data)


def admin_interface(qcm_data):
    st.title("🛠️ Interface d'Administration des QCM")
    st.markdown("### Ajouter ou modifier les QCM ici 👇")

    categories = ["physique", "chimie", "maths"]
    category = st.selectbox("Choisissez la catégorie du QCM", categories)
    question = st.text_input("Question")
    choices = st.text_area("Choix (séparés par des virgules)").split(",")
    correct_options = st.multiselect("Réponses correctes", choices)

    if st.button("➕ Ajouter QCM"):
        new_qcm = {
            "question": question,
            "choices": choices,
            "correct_options": correct_options,
            "category": category,
        }
        qcm_data.append(new_qcm)
        save_qcm(qcm_data)
        st.success("QCM ajouté avec succès!")
        st.experimental_set_query_params()  # Réexécute le script

    st.markdown("---")
    st.markdown("### Liste des QCM existants :")

    for idx, qcm in enumerate(qcm_data):
        st.markdown(f"#### {idx + 1}. {qcm['question']} ({qcm['category']})")

        if st.button(f"✏️ Modifier", key=f"edit_{idx}"):
            new_question = st.text_input("Nouvelle Question", qcm['question'], key=f"new_question_{idx}")
            new_choices = st.text_area("Nouveaux Choix (séparés par des virgules)", ", ".join(qcm['choices']),
                                       key=f"new_choices_{idx}").split(",")
            new_correct_options = st.multiselect("Nouvelles Réponses correctes", new_choices,
                                                 default=qcm['correct_options'], key=f"new_correct_{idx}")

            if st.button(f"✅ Confirmer", key=f"confirm_edit_{idx}"):
                edit_qcm(idx, new_question, new_choices, new_correct_options)
                st.success(f"QCM {idx + 1} modifié avec succès!")
                st.experimental_set_query_params()

        if st.button(f"🗑️ Supprimer", key=f"delete_{idx}"):
            delete_qcm(idx)
            st.success(f"QCM {idx + 1} supprimé avec succès!")
            st.experimental_set_query_params()

    if st.button("🔓 Déconnexion"):
        st.session_state.logged_in = False
        st.experimental_set_query_params()


def display_qcm(qcm_data):
    st.title("📚 QCM")
    st.markdown("### Choisissez un quiz pour commencer 🚀")

    if not qcm_data:
        st.warning("Aucun QCM disponible pour le moment.")
        return

    categories = list(set([qcm["category"] for qcm in qcm_data]))
    st.markdown("#### Sélectionnez une catégorie :")

    if "selected_category" not in st.session_state:
        st.session_state.selected_category = None

    if st.session_state.selected_category is None:
        col1, col2, col3 = st.columns([1, 1, 1])

        if "physique" in categories:
            with col1:
                if st.button("⚛️ Physique", key="physique_button"):
                    st.session_state.selected_category = "physique"
        if "chimie" in categories:
            with col2:
                if st.button("🧪 Chimie", key="chimie_button"):
                    st.session_state.selected_category = "chimie"
        if "maths" in categories:
            with col3:
                if st.button("📐 Maths", key="maths_button"):
                    st.session_state.selected_category = "maths"

        if st.session_state.selected_category is None:
            st.info("Veuillez sélectionner une catégorie pour continuer.")
            return

    filtered_qcm_data = [qcm for qcm in qcm_data if qcm["category"] == st.session_state.selected_category]

    if not filtered_qcm_data:
        st.warning(f"Aucun QCM disponible pour la catégorie {st.session_state.selected_category}.")
        return

    if "score" not in st.session_state:
        st.session_state.score = 0
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0

    qcm = filtered_qcm_data[st.session_state.current_question_index]
    st.subheader(f"Question {st.session_state.current_question_index + 1}: {qcm['question']}")
    answers = st.multiselect(f"Choisissez une ou plusieurs réponses :", qcm["choices"],
                             key=f"question_{st.session_state.current_question_index}")

    if st.button("🚀 Soumettre"):
        if set(answers) == set(qcm["correct_options"]):
            st.session_state.score += 1
            st.success("Bonne réponse ! ✅")
        else:
            st.error("Mauvaise réponse ! ❌")
        st.info(f"Réponse correcte: {', '.join(qcm['correct_options'])}")

        if st.session_state.current_question_index < len(filtered_qcm_data) - 1:
            st.session_state.current_question_index += 1
        else:
            st.session_state.current_question_index = 0
            st.session_state.selected_category = None
            st.balloons()
            st.subheader(f"Vous avez terminé le QCM! 🎯 Score: {st.session_state.score}/{len(filtered_qcm_data)}")
            st.session_state.score = 0

    st.markdown(
        "[Je veux vérifier cela en posant une question à mes tuteurs d'amour 💌](https://www.instagram.com/les_glycerhums)")


def theme_selector():
    st.sidebar.markdown("### 🎨 Choisissez votre thème")
    theme = st.sidebar.selectbox("Sélectionner un thème", ["Clair", "Sombre"])
    if theme == "Sombre":
        st.markdown("<style>body{background-color: #1a1a1a; color: #e6e6e6;}</style>", unsafe_allow_html=True)
    else:
        st.markdown("<style>body{background-color: #ffffff; color: #000000;}</style>", unsafe_allow_html=True)


def main():
    theme_selector()  # Ajout du sélecteur de thème

    st.sidebar.title("🧭 Menu")
    menu = st.sidebar.radio("Navigation", ["Étudiants", "Admin"])

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if menu == "Étudiants":
        qcm_data = load_qcm()
        display_qcm(qcm_data)

    elif menu == "Admin":
        if not st.session_state.logged_in:
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")
            if st.button("🔑 Connexion"):
                if USERS.get(username) == password:
                    st.session_state.logged_in = True
                    st.experimental_set_query_params()
                else:
                    st.error("Nom d'utilisateur ou mot de passe incorrect.")
        else:
            qcm_data = load_qcm()
            admin_interface(qcm_data)


if __name__ == "__main__":
    main()
    
