import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import os
import io

# 1. Configurazione della pagina
st.set_page_config(page_title="Acquario Pro Monitor", page_icon="🐠", layout="wide")
st.title("🐠 Monitoraggio Acquario Avanzato")

# Nome dei file di salvataggio locali (cache server)
DB_FILE = "acquario_dolce_dati.csv"
BIO_FILE = "acquario_biodiversita.csv"

# Colonne precise per evitare crash
COLONNE_VALORI = ["Data", "Temperatura", "pH", "KH", "GH", "Cl", "NO2", "NO3", "Note"]
COLONNE_BIO = ["Tipologia", "Nome", "Quantità", "Data Inserimento"]

# 2. Creazione automatica e sicura dei file se non esistono
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=COLONNE_VALORI).to_csv(DB_FILE, index=False)

if not os.path.exists(BIO_FILE):
    pd.DataFrame(columns=COLONNE_BIO).to_csv(BIO_FILE, index=False)

# 3. Funzioni per caricare i dati senza errori
def carica_parametri():
    try:
        df = pd.read_csv(DB_FILE)
        if len(df) > 0:
            df["Data"] = pd.to_datetime(df["Data"])
            return df.sort_values(by="Data").reset_index(drop=True)
    except:
        pass
    return pd.DataFrame(columns=COLONNE_VALORI)

def carica_biodiversita():
    try:
        df = pd.read_csv(BIO_FILE)
        if len(df) > 0:
            return df.reset_index(drop=True)
    except:
        pass
    return pd.DataFrame(columns=COLONNE_BIO)

df_acquario = carica_parametri()
df_bio = carica_biodiversita()

# ==================== BARRA LATERALE PER LA SICUREZZA DEI DATI ====================
st.sidebar.markdown("---")
st.sidebar.header("💾 Salva / Ripristina Database")
st.sidebar.write("Usa questa sezione se il server si resetta per non perdere i dati.")

# Esportazione Parametri
if not df_acquario.empty:
    csv_parametri = df_acquario.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="📥 Scarica Backup Parametri",
        data=csv_parametri,
        file_name="backup_parametri_acquario.csv",
        mime="text/csv",
    )

# Esportazione Biodiversità
if not df_bio.empty:
    csv_bio = df_bio.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="📥 Scarica Backup Abitanti",
        data=csv_bio,
        file_name="backup_abitanti_acquario.csv",
        mime="text/csv",
    )

st.sidebar.markdown("---")
st.sidebar.write("🔄 **Ripristina file salvato:**")
file_parametri_caricato = st.sidebar.file_uploader("Carica file parametri (.csv)", type=["csv"], key="restore_param")
if file_parametri_caricato is not None:
    try:
        df_caricato = pd.read_csv(file_parametri_caricato)
        df_caricato.to_csv(DB_FILE, index=False)
        st.sidebar.success("Parametri caricati nel database!")
        st.rerun()
    except:
        st.sidebar.error("Errore nel caricamento del file.")

file_bio_caricato = st.sidebar.file_uploader("Carica file abitanti (.csv)", type=["csv"], key="restore_bio")
if file_bio_caricato is not None:
    try:
        df_bio_caricato = pd.read_csv(file_bio_caricato)
        df_bio_caricato.to_csv(BIO_FILE, index=False)
        st.sidebar.success("Abitanti caricati nel database!")
        st.rerun()
    except:
        st.sidebar.error("Errore nel caricamento del file.")


# 4. Creazione dei Tab dell'interfaccia
tab_cruscotto, tab_abitanti, tab_galleria = st.tabs(["📊 Parametri & Storico", "🌿 Pesci e Piante", "📸 Galleria Foto"])

# ==================== TAB 1: PARAMETRI & STORICO ====================
with tab_cruscotto:
    # Modulo di inserimento dati a sinistra nella barra laterale
    st.sidebar.header("📝 Inserisci i test manuali")
    with st.sidebar.form(key="registro_valori"):
        data_ins = st.date_input("Data del Test", datetime.date.today())
        temp_ins = st.number_input("Temperatura (°C)", min_value=15.0, max_value=35.0, value=24.5, step=0.5)
        ph_ins = st.number_input("Valore pH", min_value=5.5, max_value=8.5, value=7.0, step=0.1)
        kh_ins = st.number_input("Carbonati KH (°dKH)", min_value=0.0, max_value=30.0, value=6.0, step=1.0)
        gh_ins = st.number_input("Durezza Totale GH (°dGH)", min_value=0.0, max_value=40.0, value=10.0, step=1.0)
        cl_ins = st.number_input("Cloro Cl2 (mg/l)", min_value=0.0, max_value=3.0, value=0.0, step=0.1)
        no2_ins = st.number_input("Nitriti NO2 (mg/l)", min_value=0.0, max_value=2.0, value=0.0, step=0.05)
        no3_ins = st.number_input("Nitrati NO3 (mg/l)", min_value=0.0, max_value=100.0, value=10.0, step=5.0)
        note_ins = st.text_input("Interventi (es. Cambio d'acqua)", "")
        submit = st.form_submit_button("Registra nel Database")

    if submit:
        df_nuovo = pd.DataFrame([[data_ins, temp_ins, ph_ins, kh_ins, gh_ins, cl_ins, no2_ins, no3_ins, note_ins]], columns=COLONNE_VALORI)
        df_aggiornato = pd.concat([pd.read_csv(DB_FILE), df_nuovo], ignore_index=True)
        df_aggiornato.to_csv(DB_FILE, index=False)
        st.success("Test salvato correttamente!")
        st.rerun()

    # Mostra i dati solo se la tabella contiene registrazioni
    if not df_acquario.empty:
        ultimo = df_acquario.iloc[-1]
        st.subheader("📌 Ultimo controllo effettuato")
        
        c1, c2, c3, c4 = st.columns(4)
        c5, c6, c7, c8 = st.columns(4)
        
        c1.metric("Temperatura", f"{ultimo['Temperatura']} °C")
        c2.metric("pH", f"{ultimo['pH']}")
        c3.metric("KH (Carbonati)", f"{ultimo['KH']} °dKH")
        c4.metric("GH (Durezza)", f"{ultimo['GH']} °dGH")
        c5.metric("Cloro (Cl2)", f"{ultimo['Cl']} mg/l")
        c6.metric("Nitriti (NO2)", f"{ultimo['NO2']} mg/l")
        c7.metric("Nitrati (NO3)", f"{ultimo['NO3']} mg/l")

        st.markdown("---")
        st.subheader("📈 Storico dei parametri")
        parametro_scelto = st.selectbox("Scegli cosa visualizzare sul grafico:", ["Temperatura", "pH", "KH", "GH", "Cl", "NO2", "NO3"])
        fig = px.line(df_acquario, x="Data", y=parametro_scelto, markers=True, title=f"Andamento nel tempo: {parametro_scelto}")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("📋 Registro storico dei test")
        df_visivo = df_acquario.copy()
        df_visivo["Data"] = df_visivo["Data"].dt.strftime('%Y-%m-%d')
        st.dataframe(df_visivo, use_container_width=True)
        
        st.write("### 🗑️ Elimina una misurazione specifica")
        col_del_id, col_del_btn = st.columns(2)
        with col_del_id:
            riga_da_eliminare = st.number_input("Inserisci l'ID della riga da eliminare (numero a sinistra):", min_value=0, max_value=len(df_acquario)-1, step=1)
        with col_del_btn:
            st.write(" ")
            st.write(" ")
            if st.button("🗑️ Elimina Test Selezionato", type="primary"):
                df_mod = pd.read_csv(DB_FILE).drop(index=riga_da_eliminare).reset_index(drop=True)
                df_mod.to_csv(DB_FILE, index=False)
                st.success("Test eliminato!")
                st.rerun()
    else:
        st.info("Benvenuto! Il database è vuoto o il server è stato riavviato. Se hai un file di backup, caricalo dalla barra laterale a sinistra, oppure inserisci un nuovo test manuale.")

    st.markdown("---")
    if st.button("🚨 Svuota/Reset completo database parametri"):
        pd.DataFrame(columns=COLONNE_VALORI).to_csv(DB_FILE, index=False)
        st.rerun()

# ==================== TAB 2: PESCI E PIANTE ====================
with tab_abitanti:
    st.subheader("🌿 Censimento della Biodiversità")
    col_form, col_lista = st.columns(2)
    
    with col_form:
        st.write("### ➕ Aggiungi Ospite")
        with st.form(key="registro_bio"):
            tipo_ins = st.selectbox("Tipologia", ["Pesce", "Pianta", "Invertebrato"])
            nome_ins = st.text_input("Nome Specie (es. Neon, Anubias)", "")
            qta_ins = st.number_input("Quantità", min_value=1, value=1, step=1)
            data_bio_ins = st.date_input("Data di inserimento", datetime.date.today())
            submit_bio = st.form_submit_button("Aggiungi all'Acquario")
            
        if submit_bio and nome_ins:
            df_nuovo_bio = pd.DataFrame([[tipo_ins, nome_ins, qta_ins, data_bio_ins]], columns=COLONNE_BIO)
            df_agg_bio = pd.concat([pd.read_csv(BIO_FILE), df_nuovo_bio], ignore_index=True)
            df_agg_bio.to_csv(BIO_FILE, index=False)
            st.success(f"{nome_ins} aggiunto!")
            st.rerun()

    with col_lista:
        st.write("### 📋 Abitanti censiti attualmente")
        if not df_bio.empty:
            st.dataframe(df_bio, use_container_width=True)
            
            st.write("### 🗑️ Elimina un ospite specifico")
            col_del_bio_id, col_del_bio_btn = st.columns(2)
            with col_del_bio_id:
                riga_bio_da_eliminare = st.number_input("ID ospite da eliminare:", min_value=0, max_value=len(df_bio)-1, step=1)
            with col_del_bio_btn:
                st.write(" ")
                st.write(" ")
                if st.button("🗑️ Elimina Ospite Selezionato"):
                    df_bio_mod = pd.read_csv(BIO_FILE).drop(index=riga_bio_da_eliminare).reset_index(drop=True)
                    df_bio_mod.to_csv(BIO_FILE, index=False)
                    st.success("Ospite rimosso!")
                    st.rerun()
        else:
            st.info("Nessun abitante inserito.")

# ==================== TAB 3: GALLERIA FOTO ====================
with tab_galleria:
    st.subheader("📸 Diario Fotografico")
    foto_caricata = st.file_uploader("Scegli una foto", type=["jpg", "jpeg", "png"])
    if foto_caricata is not None:
        st.image(foto_caricata, use_container_width=True)
