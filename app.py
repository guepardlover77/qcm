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
        st.markdown(f"#### {idx + 1}. {qcm['question']} (Catégorie: {qcm['category']})")
        for choice in qcm['choices']:
            st.markdown(f"- {choice}")
        st.markdown(f"**Réponses correctes:** {', '.join(qcm['correct_options'])}")
        if st.button(f"❌ Supprimer QCM {idx + 1}", key=f"delete_{idx}"):
            delete_qcm(idx)
            st.experimental_set_query_params()  # Re-run to refresh after deletion
        st.markdown("---")

def main():
    qcm_data = load_qcm()

    st.sidebar.title("Bienvenue dans l'application QCM")
    
    # Set default page to "Utilisateur" instead of "Administration"
    page = st.sidebar.selectbox("Navigation", ["Utilisateur", "Administration"])

    if page == "Administration":
        admin_interface(qcm_data)
    else:
        st.title("📋 QCM")
        st.markdown("### Répondez aux QCM suivants :")

        categories = ["Toutes", "physique", "chimie", "maths"]
        selected_category = st.selectbox("Choisissez une catégorie de QCM", categories)

        if selected_category != "Toutes":
            filtered_qcm_data = [qcm for qcm in qcm_data if qcm['category'] == selected_category]
        else:
            filtered_qcm_data = qcm_data

        for idx, qcm in enumerate(filtered_qcm_data):
            st.markdown(f"#### {idx + 1}. {qcm['question']} (Catégorie: {qcm['category']})")
            selected_option = st.radio(
                f"Veuillez choisir une réponse pour la question {idx + 1}:", 
                qcm['choices'], 
                key=f"qcm_{idx}"
            )

            if st.button(f"Soumettre réponse pour la question {idx + 1}", key=f"submit_{idx}"):
                if selected_option in qcm['correct_options']:
                    st.success("Bonne réponse!")
                else:
                    st.error("Mauvaise réponse!")
            st.markdown("---")

if __name__ == "__main__":
    main()
