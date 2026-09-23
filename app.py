import streamlit as st
import pandas as pd
from datetime import datetime

# Konfigurasi Halaman
st.set_page_config(page_title="Kalkulator ASTM 53", layout="centered")

@st.cache_data
def load_database():
    data = {}
    try:
        df = pd.read_excel("Tabel ASTM.xlsx", header=None)
        density_row_idx = -1
        
        # Cari baris header density
        for idx, row in df.iterrows():
            try:
                v1 = float(str(row[1]).replace(',', '.'))
                if v1 > 0.5:
                    density_row_idx = idx
                    break
            except: pass
            
        if density_row_idx == -1: return None
        
        # Ambil daftar density
        densities = []
        for c in range(1, len(df.columns)):
            try:
                densities.append(float(str(df.iloc[density_row_idx, c]).replace(',', '.')))
            except:
                densities.append(None)
                
        # Pasangkan suhu dan density
        for row_idx in range(density_row_idx + 1, len(df)):
            row = df.iloc[row_idx]
            try:
                temp = float(str(row[0]).replace(',', '.'))
                for col_idx, d_key in enumerate(densities):
                    if d_key is not None and pd.notna(row[col_idx+1]):
                        val = float(str(row[col_idx+1]).replace(',', '.'))
                        data[(round(temp, 1), round(d_key, 3))] = val
            except: continue
        return data
    except Exception as e:
        return None

# Muat database
db = load_database()

# Inisialisasi Session State
if "log" not in st.session_state:
    st.session_state.log = []
    if db:
        waktu = datetime.now().strftime("%H:%M:%S")
        st.session_state.log.append(f"[{waktu}] Sistem siap. Data Tabel ASTM.xlsx berhasil dimuat.")
    else:
        waktu = datetime.now().strftime("%H:%M:%S")
        st.session_state.log.append(f"[{waktu}] [ERROR] File Tabel ASTM.xlsx tidak ditemukan/format salah.")

def tulis_log(pesan):
    waktu = datetime.now().strftime("%H:%M:%S")
    st.session_state.log.append(f"[{waktu}] {pesan}")

def clear_data():
    st.session_state.log = []
    tulis_log("Form dan log berhasil dikosongkan.")

# Antarmuka UI
st.title("Kalkulator Corresponding Density 15°C")
st.write("Berdasarkan Table 53 ASTM-IP.")

col1, col2 = st.columns(2)
with col1:
    density_input = st.number_input("Observed Density", value=0.705, step=0.001, format="%.3f")
with col2:
    temp_input = st.number_input("Observed Temperature (°C)", value=7.5, step=0.5, format="%.1f")

col3, col4 = st.columns([1, 1])
with col3:
    if st.button("Mulai Hitung", type="primary", use_container_width=True):
        if db is None:
            st.error("Database tidak termuat. Cek file Excel.")
        else:
            t_round = round(temp_input, 1)
            d_round = round(density_input, 3)
            hasil = db.get((t_round, d_round))
            
            tulis_log(f"Mencari data -> Suhu: {temp_input}°C, Density: {density_input}")
            
            if hasil is not None:
                hasil_str = f"{hasil:.4f}".replace('.', ',')
                st.success(f"Corresponding Density @ 15°C = {hasil_str}")
                tulis_log(f">>> [HASIL] Corresponding Density @ 15°C = {hasil_str} <<<")
            else:
                st.error("Nilai tidak ditemukan di database.")
                tulis_log(f"[ERROR] Nilai (T={temp_input}, D={density_input}) tidak ditemukan di database.")

with col4:
    if st.button("Clear Data", use_container_width=True):
        clear_data()
        st.rerun()

st.markdown("### Log Proses & Hasil")
log_text = "\n".join(st.session_state.log)
st.text_area("Log Output", value=log_text, height=250, disabled=True, label_visibility="collapsed")
