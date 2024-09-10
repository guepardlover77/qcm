import streamlit as st
import mysql.connector
from mysql.connector import Error
import os

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='qcm_db',
            user='root',
            password='HXRR$6iUiexw4Eg'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        st.error(f"Erreur de connexion à MySQL: {e}")
        return None

def init_db():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS qcmv2 (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question TEXT NOT NULL,
                choices TEXT NOT NULL,
                correct_options TEXT NOT NULL,
                category VARCHAR(255) NOT NULL
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question TEXT NOT NULL,
                images TEXT
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reponses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question_id INT,
                texte TEXT NOT NULL,
                like_count INT DEFAULT 0,
                dislike_count INT DEFAULT 0,
                images TEXT,
                FOREIGN KEY (question_id) REFERENCES questions(id)
            );
        """)
        connection.commit()
        cursor.close()
        connection.close()


def load_qcm(category=None):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        if category and category.lower() != 'toutes':
            query = "SELECT * FROM qcmv2 WHERE category = %s"
            cursor.execute(query, (category,))
        else:
            cursor.execute("SELECT * FROM qcmv2")

        qcm_data = cursor.fetchall()
        for qcm in qcm_data:
            qcm['choices'] = [
                qcm['choices/0'], qcm['choices/1'], qcm['choices/2'],
                qcm.get('choices/3', ''), qcm.get('choices/4', '')
            ]
            qcm['choices'] = [choice for choice in qcm['choices'] if choice]

            qcm['correct_options'] = [
                qcm['correct_options/0'], qcm.get('correct_options/1', ''),
                qcm.get('correct_options/2', ''), qcm.get('correct_options/3', ''),
                qcm.get('correct_options/4', '')
            ]
            qcm['correct_options'] = [option for option in qcm['correct_options'] if
                                      option]

        cursor.close()
        connection.close()
        return qcm_data
    return []


def save_qcm(qcm_data):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        for qcm in qcm_data:
            cursor.execute("""
                INSERT INTO qcm (question, choices, correct_options, category) 
                VALUES (%s, %s, %s, %s)
            """, (qcm['question'], ','.join(qcm['choices']), ','.join(qcm['correct_options']), qcm['category']))
        connection.commit()
        cursor.close()
        connection.close()

def delete_qcm(qcm_id):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM qcm WHERE id = %s", (qcm_id,))
        connection.commit()
        cursor.close()
        connection.close()

def admin_interface(qcm_data):
    st.title("🛠️ Interface d'Administration des QCM")
    st.markdown("### Ajouter ou modifier les QCM ici 👇")

    categories = ["physique", "Chimie Orga", "maths", "Glucides"]
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
        save_qcm([new_qcm])
        st.success("QCM ajouté avec succès!")
        st.experimental_set_query_params()

    st.markdown("---")
    st.markdown("### Liste des QCM existants :")
    for idx, qcm in enumerate(qcm_data):
        st.markdown(f"#### {idx + 1}. {qcm['question']} (Catégorie: {qcm['category']})")
        for choice in qcm['choices']:
            st.markdown(f"- {choice}")
        st.markdown(f"**Réponses correctes:** {', '.join(qcm['correct_options'])}")
        if st.button(f"❌ Supprimer QCM {idx + 1}", key=f"delete_{idx}"):
            delete_qcm(qcm['id'])
            st.experimental_set_query_params()
        st.markdown("---")


def get_db_connection_forum():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='forum_db',
            user='root',
            password='HXRR$6iUiexw4Eg'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        st.error(f"Erreur de connexion à MySQL: {e}")
        return None

def ajouter_question(question, images_paths):
    connection = get_db_connection_forum()
    if connection:
        cursor = connection.cursor()
        images = ",".join(images_paths) if images_paths else ""
        cursor.execute("INSERT INTO questions (question, images) VALUES (%s, %s)", (question, images))
        connection.commit()
        cursor.close()
        connection.close()


def ajouter_reponse(index_question, reponse, images_paths):
    connection = get_db_connection_forum()
    if connection:
        cursor = connection.cursor()
        images = ",".join(images_paths) if images_paths else ""
        cursor.execute("INSERT INTO reponses (question_id, texte, images) VALUES (%s, %s, %s)", (index_question, reponse, images))
        connection.commit()
        cursor.close()
        connection.close()


def mettre_a_jour_score(index_question, index_reponse, action):
    connection = get_db_connection_forum()
    if connection:
        cursor = connection.cursor()
        if action == "like":
            cursor.execute("UPDATE reponses SET like_count = like_count + 1 WHERE id = %s", (index_reponse,))
        elif action == "dislike":
            cursor.execute("UPDATE reponses SET dislike_count = dislike_count + 1 WHERE id = %s", (index_reponse,))
        connection.commit()
        cursor.close()
        connection.close()


def charger_donnees():
    connection = get_db_connection_forum()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM questions")
        questions = cursor.fetchall()
        for question in questions:
            cursor.execute("SELECT * FROM reponses WHERE question_id = %s", (question['id'],))
            question['reponses'] = cursor.fetchall()
        cursor.close()
        connection.close()
        return {"questions": questions}
    return {"questions": []}


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
            image_path = f"images/{prefix}_{idx}_{image_index}.jpg"
            sauvegarder_image(image, image_path)
            image_paths.append(image_path)
    return image_paths


def faq_interface():
    st.title("🩺 Foire Aux Questions Anonyme")
    st.markdown("""
    Oyé oyé preux chevaliers. Vous avez ici de quoi parler entre vous anonymement donc posez vos questions bêtes !!!! L'idée c'est, d'une part que les tuteurs vous répondent mais aussi que vous parliez entre vous parce qu'on commence pas à jouer au foot avec Messi... Et à part cette FAQ (totalement anonyme, c'est important), vous pouvez toujours venir poser des questions aux @les_perdrisotopes sur insta !!! Allez kissou kissou et bon courage <3
    """)

    data = charger_donnees()
    if data["questions"]:
        for idx, q in enumerate(data["questions"]):
            with st.expander(f"**❓ Question** : {q['question']}"):
                if "images" in q and q["images"]:
                    for image_url in q["images"].split(","):
                        st.image(image_url, use_column_width=True)
                if q["reponses"]:
                    reponses_tries = sorted(q["reponses"], key=lambda rep: rep.get("like_count", 0), reverse=True)
                    for rep_idx, rep in enumerate(reponses_tries):
                        if isinstance(rep, dict) and "texte" in rep:
                            texte_rep = rep["texte"]
                            like = rep["like_count"]
                            dislike = rep["dislike_count"]
                            st.write(f"**💬 Réponse** : {texte_rep} (👍 {like}, 👎 {dislike})")
                            if "images" in rep and rep["images"]:
                                for image_url in rep["images"].split(","):
                                    st.image(image_url, use_column_width=True)
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button(f"👍 J'aime ({like})", key=f"like_{idx}_{rep_idx}"):
                                    mettre_a_jour_score(q['id'], rep['id'], "like")
                                    st.rerun()
                            with col2:
                                if st.button(f"👎 Je n'aime pas ({dislike})", key=f"dislike_{idx}_{rep_idx}"):
                                    mettre_a_jour_score(q['id'], rep['id'], "dislike")
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
                        images_paths = ajouter_images(images_reponse, "reponse", idx)
                        ajouter_reponse(q['id'], nouvelle_reponse.strip(), images_paths)
                        st.success("Votre réponse a été soumise avec succès !")
                    else:
                        st.error("Veuillez entrer une réponse avant de soumettre.")
    st.subheader("Poser une nouvelle question (Anonyme)")
    nouvelle_question = st.text_area("Tapez votre question ici :", "", key="nouvelle_question")
    images_question = st.file_uploader("Joindre des images à la question (facultatif)", accept_multiple_files=True,
                                       type=["png", "jpg", "jpeg"], key="images_question")
    if st.button("Soumettre la question", key="submit_question"):
        if nouvelle_question.strip() != "":
            images_paths = ajouter_images(images_question, "question", len(data["questions"]))
            ajouter_question(nouvelle_question.strip(), images_paths)
            st.success("Votre question a été soumise de manière anonyme !")
        else:
            st.error("Veuillez entrer une question avant de soumettre.")


def user_qcm_interface(qcm_data):
    st.title("📋 QCM")
    categories = ["Toutes", "physique", "Chimie Orga", "maths", "Glucides"]
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

def main():
    init_db()
    qcm_data = load_qcm()
    page = st.sidebar.radio("Aller à :", ("Utilisateur", "Administration", "FAQ"))

    if page == "Administration":
        admin_interface(qcm_data)
    elif page == "FAQ":
        faq_interface()
    else:
        user_qcm_interface(qcm_data)

if __name__ == "__main__":
    main()
