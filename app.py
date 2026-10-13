import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import os

# Configurazione della pagina
st.set_page_config(page_title="Acquario Dolce Monitor Pro", page_icon="🐠", layout="wide")
st.title("🐠 Monitoraggio Acquario, Censimento e Galleria")

# File per salvare i parametri
DB_FILE = "acquario_dolce_dati.csv"
# File per salvare pesci e piante
BIO_FILE = "acquario_biodiversita.csv"

# Inizializzazione file dati se non esistono
if not os.path.exists(DB_FILE):
    df_init = pd.DataFrame(columns=["Data", "Temperatura", "pH", "NO2", "NO3", "Note"])
    df_init.to_csv(DB_FILE, index=False)

if not os.path.exists(BIO_FILE):
    df_bio_init = pd.DataFrame(columns=["Tipologia", "Nome", "Quantità", "Data Inserimento"])
    df_bio_init.to_csv(BIO_FILE, index=False)

def carica_dati(file):
    df = pd.read_csv(file)
    if "Data" in df.columns:
        df["Data"] = pd.to_datetime(df["Data"])
        df = df.sort_values(by="Data")
    return df.reset_index(drop=True)

def salva_valori(data, temp, ph, no2, no3, note):
    df = pd.read_csv(DB_FILE)
    nuovo_dato = pd.DataFrame([[data, temp, ph, no2, no3, note]], columns=df.columns)
    df = pd.concat([df, nuovo_dato], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

def salva_bio(tipologia, nome, quantita, data_ins):
    df = pd.read_csv(BIO_FILE)
    nuovo_dato = pd.DataFrame([[tipologia, nome, quantita, data_ins]], columns=df.columns)
    df = pd.concat([df, nuovo_dato], ignore_index=True)
    df.to_csv(BIO_FILE, index=False)

df_acquario = carica_dati(DB_FILE)
df_bio = carica_dati(BIO_FILE)

# Creazione dei Tab principali
tab_cruscotto, tab_abitanti, tab_galleria = st.tabs(["📊 Parametri & Storico", "🌿 Pesci e Piante", "📸 Galleria Foto"])

# ==================== TAB 1: PARAMETRI & STORICO ====================
with tab_cruscotto:
    st.sidebar.header("📝 Inserisci i test manuali")
    with st.sidebar.form(key="registro_valori"):
        data_ins = st.date_input("Data del Test", datetime.date.today(), key="data_valore")
        temp_ins = st.number_input("Temperatura (°C)", min_value=15.0, max_value=35.0, value=24.5, step=0.5)
        ph_ins = st.number_input("Valore pH", min_value=5.5, max_value=8.5, value=7.0, step=0.1)
        no2_ins = st.number_input("Nitriti NO2 (mg/l)", min_value=0.0, max_value=2.0, value=0.0, step=0.05)
        no3_ins = st.number_input("Nitrati NO3 (mg/l)", min_value=0.0, max_value=100.0, value=10.0, step=5.0)
        note_ins = st.text_input("Interventi (es. Cambio d'acqua 20L, potatura)", "")
        submit = st.form_submit_button("Registra nel Database")

    if submit:
        salva_valori(data_ins, temp_ins, ph_ins, no2_ins, no3_ins, note_ins)
        st.success("Test registrato con successo!")
        st.rerun()

    if not df_acquario.empty:
        ultimo = df_acquario.iloc[-1]
        st.subheader("📌 Ultimo controllo effettuato")
        col1, col2, col3, col4 = st.columns(4)
        
        st_temp = "Ottimale (23-26°C)" if 23 <= ultimo['Temperatura'] <= 26 else "⚠️ Fuori range ideale!"
        col1.metric("Temperatura", f"{ultimo['Temperatura']} °C", delta=st_temp)
        
        st_ph = "Perfetto per comunità" if 6.5 <= ultimo['pH'] <= 7.5 else "⚠️ pH fuori range"
        col2.metric("pH", f"{ultimo['pH']}", delta=st_ph)
        
        if ultimo['NO2'] == 0: st_no2 = "Eccellente (Vasca sicura)"
        elif ultimo['NO2'] < 0.2: st_no2 = "⚠️ Traccia rilevata"
        else: st_no2 = "🚨 PERICOLO TOSSICITÀ!"
        col3.metric("Nitriti (NO2)", f"{ultimo['NO2']} mg/l", delta=st_no2, delta_color="inverse")
        
        if ultimo['NO3'] <= 20: st_no3 = "Buono"
        elif ultimo['NO3'] <= 40: st_no3 = "⚠️ Accettabile"
        else: st_no3 = "🚨 Troppo alti!"
        col4.metric("Nitrati (NO3)", f"{ultimo['NO3']} mg/l", delta=st_no3, delta_color="inverse")

        st.markdown("---")
        st.subheader("📈 Storico dei parametri")
        parametro_scelto = st.selectbox("Scegli cosa visualizzare sul grafico:", ["Temperatura", "pH", "NO2", "NO3"])
        fig = px.line(df_acquario, x="Data", y=parametro_scelto, markers=True, title=f"Andamento nel tempo: {parametro_scelto}")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("📋 Registro storico dei test")
        df_visivo = df_acquario.copy()
        df_visivo["Data"] = df_visivo["Data"].dt.strftime('%Y-%m-%d')
        st.dataframe(df_visivo, use_container_width=True)
    else:
        st.info("Nessun parametro inserito. Usa la barra laterale per registrare il primo test.")

# ==================== TAB 2: PESCI E PIANTE ====================
with tab_abitanti:
    st.subheader("🌿 Censimento della Biodiversità")
    
    col_form, col_lista = st.columns([1, 2])
    
    with col_form:
        st.write("### ➕ Aggiungi Ospite")
        with st.form(key="registro_bio"):
            tipo_ins = st.selectbox("Tipologia", ["Pesce", "Pianta", "Invertebrato (Lumaca/Gamberetto)"])
            nome_ins = st.text_input("Nome Specie (es. Neon, Anubias)", "")
            qta_ins = st.number_input("Quantità inserita", min_value=1, value=1, step=1)
            data_bio_ins = st.date_input("Data di inserimento", datetime.date.today(), key="data_bio")
            submit_bio = st.form_submit_button("Aggiungi all'Acquario")
            
        if submit_bio and nome_ins:
            salva_bio(tipo_ins, nome_ins, qta_ins, data_bio_ins)
            st.success(f"{nome_ins} aggiunto con successo!")
            st.rerun()

    with col_lista:
        st.write("### 📋 Abitanti censiti attualmente")
        if not df_bio.empty:
            st.dataframe(df_bio, use_container_width=True)
            
            if st.button("❌ Svuota intero registro abitanti"):
                df_svuota = pd.DataFrame(columns=["Tipologia", "Nome", "Quantità", "Data Inserimento"])
                df_svuota.to_csv(BIO_FILE, index=False)
                st.rerun()
        else:
            st.info("Nessun abitante inserito. Compila il modulo a sinistra per aggiungere la tua fauna e flora.")

# ==================== TAB 3: GALLERIA FOTO ====================
with tab_galleria:
    st.subheader("📸 Diario Fotografico dell'Acquario")
    st.write("Carica un'immagine per vederla riprodotta nella sessione corrente. *(Nota: Streamlit Cloud azzera i file caricati al riavvio del server)*")
    
    foto_caricata = st.file_uploader("Scegli una foto dal tuo Mac o Smartphone", type=["jpg", "jpeg", "png"])
    
    if foto_caricata is not None:
        st.image(foto_caricata, caption=f"Foto caricata il {datetime.date.today().strftime('%Y-%m-%d')}", use_container_width=True)
    else:
        st.info("Trascina qui uno screenshot o una foto per visualizzarla al centro dello schermo.")

# --- GESTIONE ERRORI E BACKUP IN FONDO ALLA SIDEBAR ---
if not df_acquario.empty:
    st.sidebar.markdown("---")
    st.sidebar.header("🛠️ Gestione Errori")
    if st.sidebar.button("❌ Cancella l'ultima riga test"):
        df_modificabile = pd.read_csv(DB_FILE)
        if len(df_modificabile) > 0:
            df_modificabile = df_modificabile.drop(df_modificabile.index[-1])
            df_modificabile.to_csv(DB_FILE, index=False)
            st.sidebar.success("Ultima misurazione eliminata!")
            st.rerun()
