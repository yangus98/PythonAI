import streamlit as st
import pandas as pd
import docx  # python-docx per DOCX
import os
from pandasai import SmartDataframe


# Titolo dell'applicazione
st.title("Caricamento di un file e Interazione con i Dati")

# Barra laterale per la navigazione tra le pagine
pagina = st.sidebar.selectbox("Scegli una pagina", ["Caricamento file", "Chatbot sui dati"])

# Inizializzo session_state per il file caricato, il DataFrame, il contesto e il contatore delle domande solo se non esistono
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "df" not in st.session_state:
    st.session_state.df = None
if "question_count" not in st.session_state:
    st.session_state.question_count = 0  # Contatore per le domande
if "responses" not in st.session_state:
    st.session_state.responses = []  # Cache per risposte
if "chatbot_context" not in st.session_state:
    st.session_state.chatbot_context = ""  # Contesto per il chatbot

# Caricamento file e visualizzazione
if pagina == "Caricamento file":
    # Text area per inserire il contesto per la chat
    st.session_state.chatbot_context = st.text_area("Inserisci il contesto per la chatbox", height=100)

    # Carico il file
    uploaded_file = st.file_uploader("Carica un file", type=["csv", "xlsx", "xls", "json", "txt", "docx"])

    # Salvo il file in session_state se caricato
    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        try:
            # Determino il tipo di file e carica i dati di conseguenza
            if uploaded_file.name.endswith(".csv"):
                st.session_state.df = pd.read_csv(uploaded_file, encoding="ISO-8859-1")
            elif uploaded_file.name.endswith((".xlsx", ".xls")):
                st.session_state.df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith(".json"):
                st.session_state.df = pd.read_json(uploaded_file)
            elif uploaded_file.name.endswith(".txt"):
                st.session_state.df = pd.read_csv(uploaded_file, delimiter="\t", encoding="ISO-8859-1")
            elif uploaded_file.name.endswith(".docx"):
                doc = docx.Document(uploaded_file)
                text = "\n".join([para.text for para in doc.paragraphs])
                st.text_area("Contenuto del DOCX", text, height=300)
                st.session_state.df = None

            # Visualizzo i dati solo se il file è in formato compatibile
            if st.session_state.df is not None:
                col1, col2 = st.columns(2)
                with col1:
                    st.write("Ecco un'anteprima dei dati caricati:")
                    st.dataframe(st.session_state.df.head())
                with col2:
                    file_info = f"Numero di righe: {st.session_state.df.shape[0]}\n"
                    file_info += f"Numero di colonne: {st.session_state.df.shape[1]}\n\n"
                    file_info += "Informazioni sulle colonne:\n"
                    file_info += "\n".join([f"{col}: {dtype}" for col, dtype in zip(st.session_state.df.columns, st.session_state.df.dtypes)])
                    st.text_area("Informazioni sul file", file_info, height=300)
            else:
                st.warning("Non sono stati trovati dati validi nel file caricato.")

        except Exception as e:
            st.error(f"Errore durante la lettura del file: {e}")

# Chatbot sui dati caricati
elif pagina == "Chatbot sui dati":
    if st.session_state.df is not None:
        os.environ["PANDASAI_API_KEY"] = "$2a$10$SRFkre3pNVAjUlwSa5z2du6EPZ8y.aEg2/HYPUsF83QiowizlUkzq"
        smart_df = SmartDataframe(st.session_state.df)

        st.write("Inserisci una domanda riguardo ai dati caricati:")
        user_input = st.text_area("La tua domanda", "", height=100)

        if st.button("Invia"):
            if user_input:
                # Unisco il contesto del chatbot alla domanda dell'utente
                full_input = f"{st.session_state.chatbot_context}\n\n{user_input}"

                try:
                    response_text = smart_df.chat(full_input)
                    st.subheader("Risposta del chatbot:")
                    st.text_area("Risposta", response_text, height=150, disabled=True)

                    # Incremento il contatore delle domande e aggiungi la risposta alla cache
                    st.session_state.question_count += 1
                    st.session_state.responses.append(response_text)

                    # Svuoto tutte le cache e resetta il contatore e il file caricato dopo 3 domande
                    if st.session_state.question_count >= 3:
                        st.write("Ti sono stato utile?")
                        thumbs_up = st.button("👍 Parere positivo")
                        thumbs_down = st.button("👎 Parere negativo")
                        st.session_state.uploaded_file = None
                        st.session_state.df = None
                        st.session_state.responses = []
                        st.session_state.question_count = 0
                        st.warning("Cache delle domande, risposte e file caricato svuotata dopo 3 domande.")
                        
                except Exception as e:
                    st.error(f"Errore nella generazione della risposta: {e}")
            else:
                st.warning("Per favore, inserisci una domanda.")
    else:
        st.warning("Carica un file nella pagina precedente per interagire con il chatbot.")
