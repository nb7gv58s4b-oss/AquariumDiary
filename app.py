import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import os

# Configurazione della pagina
st.set_page_config(page_title="Acquario Dolce Monitor", page_icon="🐠", layout="wide")
st.title("🐠 Monitoraggio Acquario d'Acqua Dolce")

# File per salvare i dati
DB_FILE = "acquario_dolce_dati.csv"

# Inizializzazione file dati se non esiste
if not os.path.exists(DB_FILE):
    df_init = pd.DataFrame(columns=["Data", "Temperatura", "pH", "NO2", "NO3", "Note"])
    df_init.to_csv(DB_FILE, index=False)

def carica_dati():
    df = pd.read_csv(DB_FILE)
    df["Data"] = pd.to_datetime(df["Data"])
    return df.sort_values(by="Data")

def salva_dati(data, temp, ph, no2, no3, note):
    df = pd.read_csv(DB_FILE)
    nuovo_dato = pd.DataFrame([[data, temp, ph, no2, no3, note]], columns=df.columns)
    df = pd.concat([df, nuovo_dato], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

df_acquario = carica_dati()

# --- SIDEBAR PER INSERIMENTO MANUALE (COSTO 0) ---
sidebar = st.sidebar
sidebar.header("📝 Inserisci i test manuali")
sidebar.write("Esegui i test a gocce o a strisce e inserisci qui i valori riscontrati:")

with sidebar.form(key="registro_valori"):
    data_ins = sidebar.date_input("Data del Test", datetime.date.today())
    temp_ins = sidebar.number_input("Temperatura (°C)", min_value=15.0, max_value=35.0, value=24.5, step=0.5)
    ph_ins = sidebar.number_input("Valore pH", min_value=5.5, max_value=8.5, value=7.0, step=0.1)
    no2_ins = sidebar.number_input("Nitriti NO2 (mg/l)", min_value=0.0, max_value=2.0, value=0.0, step=0.05)
    no3_ins = sidebar.number_input("Nitrati NO3 (mg/l)", min_value=0.0, max_value=100.0, value=10.0, step=5.0)
    note_ins = sidebar.text_input("Interventi (es. Cambio d'acqua 20L, potatura)", "")
    
    submit = sidebar.form_submit_button("Registra nel Database")

if submit:
    salva_dati(data_ins, temp_ins, ph_ins, no2_ins, no3_ins, note_ins)
    st.success("Test registrato con successo!")
    df_acquario = carica_dati()

# --- CRUSCOTTO VALORI ---
if not df_acquario.empty:
    ultimo = df_acquario.iloc[-1]
    
    st.subheader("📌 Ultimo controllo effettuato")
    col1, col2, col3, col4 = st.columns(4)
    
    # 1. Temperatura (Range ideale dolce tropicale: 23-26 °C)
    if 23 <= ultimo['Temperatura'] <= 26:
        st_temp = "Ottimale (23-26°C)"
    else:
        st_temp = "⚠️ Troppo fredda o calda!"
    col1.metric("Temperatura", f"{ultimo['Temperatura']} °C", delta=st_temp)
    
    # 2. pH (Range generale comunità: 6.5 - 7.5)
    if 6.5 <= ultimo['pH'] <= 7.5:
        st_ph = "Perfetto per comunità"
    else:
        st_ph = "⚠️ pH fuori range"
    col2.metric("pH", f"{ultimo['pH']}", delta=st_ph)
    
    # 3. Nitriti (NO2 devono essere a 0 nelle vasche mature)
    if ultimo['NO2'] == 0:
        st_no2 = "Eccellente (Vasca sicura)"
    elif ultimo['NO2'] < 0.2:
        st_no2 = "⚠️ Attenzione, traccia rilevata"
    else:
        st_no2 = "🚨 PERICOLO TOSSICITÀ!"
    col3.metric("Nitriti (NO2)", f"{ultimo['NO2']} mg/l", delta=st_no2, delta_color="inverse")
    
    # 4. Nitrati (NO3 sotto i 25 mg/l per evitare alghe e stress)
    if ultimo['NO3'] <= 20:
        st_no3 = "Buono"
    elif ultimo['NO3'] <= 40:
        st_no3 = "⚠️ Accettabile (Consigliato cambio)"
    else:
        st_no3 = "🚨 Troppo alti! Cambiare acqua"
    col4.metric("Nitrati (NO3)", f"{ultimo['NO3']} mg/l", delta=st_no3, delta_color="inverse")

    st.markdown("---")

    # --- GRAFICI DI ANDAMENTO ---
    st.subheader("📈 Storico dei parametri")
    parametro_scelto = st.selectbox("Scegli cosa visualizzare sul grafico:", ["Temperatura", "pH", "NO2", "NO3"])
    
    fig = px.line(df_acquario, x="Data", y=parametro_scelto, markers=True,
                  title=f"Andamento nel tempo: {parametro_scelto}",
                  labels={"Data": "Data del test", parametro_scelto: parametro_scelto})
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # --- DIARIO DI BORDO ---
    st.subheader("📋 Registro storico dei test e interventi")
    st.dataframe(df_acquario, use_container_width=True)
else:
    st.info("Benvenuto! Fai il tuo primo test chimico dell'acqua e inserisci i dati nella barra laterale sinistra per iniziare il monitoraggio.")

