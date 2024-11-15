import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from utilities import conta_occorrenze, carica_stile, estrai_testo, mostra_grafico_occorrente

# Carica il CSS all'inizio dell'app
carica_stile()

st.title("Conteggio Occorrenze delle Parole")

# Casella di testo per inserire il testo manualmente
testo_utente = st.text_area("Inserisci il tuo testo qui:")

# Caricamento di un file di testo, PDF o Word
file_caricato = st.file_uploader("Carica un file (.txt, .pdf, .docx)", type=["txt", "pdf", "docx"])

# Pulsante per avviare il conteggio delle occorrenze delle parole
if st.button("Conta occorrenze delle parole"):
    # Percorso del file JSON con le parole da escludere
    percorso_json = "C:/Users/giuse/OneDrive/Desktop/Project Work Python AI/parole_da_escludere.json"

    # Determina il testo da analizzare
    if file_caricato:
        testo_utente = estrai_testo(file_caricato)

    if testo_utente:
        # Calcola le occorrenze delle parole
        conteggio_parole = conta_occorrenze([testo_utente], percorso_json)

        # Grafico
        st.write("Occorrenza di ogni parola:")
        chart = mostra_grafico_occorrente(conteggio_parole)
        st.altair_chart(chart, use_container_width=True)

        # Visualizza i risultati in text area
        risultato = "\n".join([f"{parola}: {occorrenza}" for parola, occorrenza in conteggio_parole.items()])
        st.text_area("Risultati", risultato, height=300)
        
        # Crea il testo filtrato per il WordCloud
        # Usa solo la lista delle parole uniche senza moltiplicare per occorrenza
        testo_filtrato = " ".join(conteggio_parole.keys())

        # Crea e visualizza il WordCloud
        wordcloud = WordCloud().generate(testo_filtrato)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.warning("Inserisci del testo o carica un file per contare le occorrenze.")

