import streamlit as st
import json
import os


QCM_FILE = "qcm.json"
USERS = {"admin": "password123"}  # Ajoutez d'autres utilisateurs ici


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
    st.title("Interface d'Administration des QCM")

    categories = ["physique", "chimie", "maths"]
    category = st.selectbox("Choisissez la catégorie du QCM", categories)

    question = st.text_input("Question")
    choices = st.text_area("Choix (séparés par des virgules)").split(",")
    correct_options = st.multiselect("Réponses correctes", choices)

    if st.button("Ajouter QCM"):
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

    st.write("Liste des QCM:")
    for idx, qcm in enumerate(qcm_data):
        st.write(f"{idx + 1}. {qcm['question']} ({qcm['category']})")

        if st.button(f"Modifier {idx + 1}", key=f"edit_{idx}"):
            new_question = st.text_input("Nouvelle Question", qcm['question'], key=f"new_question_{idx}")
            new_choices = st.text_area("Nouveaux Choix (séparés par des virgules)", ", ".join(qcm['choices']),
                                       key=f"new_choices_{idx}").split(",")
            new_correct_options = st.multiselect("Nouvelles Réponses correctes", new_choices,
                                                 default=qcm['correct_options'], key=f"new_correct_{idx}")

            if st.button(f"Confirmer les modifications {idx + 1}", key=f"confirm_edit_{idx}"):
                edit_qcm(idx, new_question, new_choices, new_correct_options)
                st.success(f"QCM {idx + 1} modifié avec succès!")
                st.experimental_set_query_params()  # Réexécute le script

        if st.button(f"Supprimer {idx + 1}", key=f"delete_{idx}"):
            delete_qcm(idx)
            st.success(f"QCM {idx + 1} supprimé avec succès!")
            st.experimental_set_query_params()  # Réexécute le script


def display_qcm(qcm_data):
    st.title("QCM pour Étudiants")

    if not qcm_data:
        st.write("Aucun QCM disponible.")
        return

    categories = list(set([qcm["category"] for qcm in qcm_data]))
    selected_category = st.selectbox("Choisissez une catégorie", categories)

    filtered_qcm_data = [qcm for qcm in qcm_data if qcm["category"] == selected_category]

    if not filtered_qcm_data:
        st.write(f"Aucun QCM disponible pour la catégorie {selected_category}.")
        return

    score = 0
    total_questions = len(filtered_qcm_data)

    for idx, qcm in enumerate(filtered_qcm_data):
        st.write(f"Question {idx + 1}: {qcm['question']}")
        answers = st.multiselect(f"Choisissez une ou plusieurs réponses pour la question {idx + 1}:", qcm["choices"], key=f"question_{idx}")

        if st.button(f"Soumettre", key=f"submit_{idx}"):
            if set(answers) == set(qcm["correct_options"]):
                score += 1
            st.write(f"Réponse correcte: {', '.join(qcm['correct_options'])}")

    if st.button("Terminer le QCM"):
        st.write(f"Vous avez terminé le QCM! Score: {score}/{total_questions}")


def main():
    st.sidebar.title("Menu")
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
            if st.button("Connexion"):
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
