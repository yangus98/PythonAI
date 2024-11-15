import streamlit as st
import json
import os
import PyPDF2
import docx
import altair as alt
import pandas as pd

# Funzione per caricare e applicare il CSS
def carica_stile():
    current_dir = os.path.dirname(__file__)
    css_file_path = os.path.join(current_dir, "stile.css")

    try:
        with open(css_file_path) as file_css:
            st.markdown(f"<style>{file_css.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("Il file stile.css non è stato trovato. Verifica il percorso.")

# Funzione per estrarre testo da diversi tipi di file
def estrai_testo(file):
    if file.type == "text/plain":
        # Per file txt
        return file.read().decode("utf-8")
    elif file.type == "application/pdf":
        # Per file PDF
        pdf_reader = PyPDF2.PdfReader(file)
        testo_pdf = ""
        for pagina in pdf_reader.pages:
            testo_pdf += pagina.extract_text()
        return testo_pdf
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        # Per file Word
        doc = docx.Document(file)
        testo_word = ""
        for paragrafo in doc.paragraphs:
            testo_word += paragrafo.text + " "
        return testo_word
    return ""

# Funzione per contare le occorrenze delle parole in un testo, escludendo le parole da un file JSON
def conta_occorrenze(testo, percorso_json):
    # Carica il file JSON contenente le parole da escludere
    try:
        with open(percorso_json, 'r', encoding='utf-8') as file_json:
            data = json.load(file_json)
            parole_da_escludere = set(data.get("parole_da_escludere", []))
    except FileNotFoundError:
        raise FileNotFoundError(f"Il file {percorso_json} non è stato trovato.")
    except json.JSONDecodeError:
        raise ValueError("Errore nella lettura del file JSON.")

    # Unisce tutte le righe in un singolo testo e converte in minuscolo
    testo_unito = " ".join(testo).lower()

    # Sostituisce le interruzioni di riga con uno spazio
    testo_unito = testo_unito.replace("\n", " ")

    # Mantiene solo i caratteri validi e lo spazio
    caratteri_validi = "abcdefghijklmnopqrstuvwxyzàèéìòùç"
    testo_unito = ''.join([char for char in testo_unito if char in caratteri_validi + " "])

    # Divide il testo in parole
    parole = testo_unito.split()

    # Conta le occorrenze delle parole, escludendo parole da parole_da_escludere
    occorrenze = {}
    for parola in set(parole):
        if parola not in parole_da_escludere:
            occorrenze[parola] = parole.count(parola)

    # Ordina le parole per numero di occorrenze in ordine decrescente
    occorrenze_ordinate = dict(sorted(occorrenze.items(), key=lambda item: item[1], reverse=True))

    return occorrenze_ordinate  # Restituisce il dizionario ordinato delle occorrenze

# Funzione per visualizzare un grafico con le 10 parole più usate
def mostra_grafico_occorrente(conteggio_parole):
    # Creazione di un DataFrame con le parole e le loro occorrenze
    df = pd.DataFrame(conteggio_parole.items(), columns=["Parola", "Occorrenze"])

    # Ordina per occorrenza in modo decrescente e seleziona le prime 10 parole
    df = df.sort_values(by="Occorrenze", ascending=False).head(10)

    # Crea il grafico
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("Parola:N", sort='-y', axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Occorrenze:Q")
    ).properties(
        title="Top 10 parole per occorrenza"
    )

    return chart

