import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Peta Bukber Bandung", layout="wide", page_icon="🌙")

# --- CUSTOM CSS (PEMANIS TAMPILAN) ---
st.markdown("""
    <style>
    /* Memaksa background menjadi warna krem hangat/pastel khas Ramadan */
    .stApp {
        background-color: #FDF6E3;
    }
    
    /* Memaksa SEMUA teks menjadi warna gelap (Navy Tua) agar kontras dan terbaca */
    html, body, [class*="css"] {
        color: #2C3E50 !important;
    }
    
    /* Memperbaiki warna khusus untuk semua level Judul */
    h1, h2, h3, h4, h5, h6, p, div, span {
        color: #2C3E50 !important;
    }
    
    /* Khusus untuk Judul Utama agar lebih mencolok (Warna Oranye Bata) */
    h1 {
        color: #D35400 !important;
        font-family: 'Trebuchet MS', sans-serif;
        text-align: center;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    /* Deskripsi di bawah judul */
    .deskripsi {
        text-align: center;
        color: #7F8C8D !important;
        font-size: 16px;
        margin-bottom: 20px;
    }

    /* Style card rekomendasi Top 5 */
    .rekomendasi-card {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        text-align: center;
        border-top: 4px solid #D35400;
        margin-bottom: 10px;
        transition: transform 0.2s; /* Animasi saat dihover */
    }
    .rekomendasi-card:hover {
        transform: scale(1.05);
    }
    
    .rating-bintang {
        color: #F39C12 !important;
        font-size: 18px;
        font-weight: bold;
    }
    
    .harga-tag {
        color: #27AE60 !important;
        font-weight: 600;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# Pastikan bagian judul di app.py kamu diperbarui menjadi seperti ini:
st.title("🌙 Peta Rekomendasi Tempat Bukber di Bandung")
st.markdown("<p class='deskripsi'>Cari tempat berbuka puasa, lihat harga, rating, dan rute langsung ke Google Maps!</p>", unsafe_allow_html=True)
st.write("---")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data_bukber_bandung.csv")
    except FileNotFoundError:
        st.error("File data_bukber_bandung.csv tidak ditemukan. Tolong jalankan scraper.py terlebih dahulu.")
        df = pd.DataFrame(columns=["Nama Tempat", "Kategori", "Rating", "Harga", "Latitude", "Longitude", "Google Maps Link"])
    return df

df = load_data()

if not df.empty:
    # --- FITUR TOP 5 REKOMENDASI ---
    st.subheader("🏆 Top 5 Rekomendasi Tempat Bukber")
    # Urutkan berdasarkan rating tertinggi
    top_5_df = df.sort_values(by="Rating", ascending=False).head(5)
    
    # Buat 5 kolom sejajar
    cols = st.columns(5)
    for i, (index, row) in enumerate(top_5_df.iterrows()):
        with cols[i]:
            st.markdown(f"""
                <div class="rekomendasi-card">
                    <h5 style="color:#2C3E50; margin-bottom:5px;">{row['Nama Tempat']}</h5>
                    <div class="rating-bintang">⭐ {row['Rating']}</div>
                    <div class="harga-tag">💰 {row['Harga']}</div>
                    <p style="font-size:12px; color:#95A5A6; margin-top:5px;">{row['Kategori']}</p>
                    <a href="{row['Google Maps Link']}" target="_blank" style="text-decoration:none; font-size:12px; background-color:#3498DB; color:white; padding:4px 8px; border-radius:4px;">Buka Map</a>
                </div>
            """, unsafe_allow_html=True)

    st.write("---")

    # --- TATA LETAK PENCARIAN & PETA ---
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("🔍 Cari Tempat Spesifik")
        # Fitur pencarian/filter
        daftar_tempat = ["Tampilkan Semua"] + df["Nama Tempat"].tolist()
        pilihan_user = st.selectbox("Pilih tempat yang ingin dituju:", daftar_tempat)
        
        # Filter Data berdasarkan pencarian
        if pilihan_user != "Tampilkan Semua":
            df_tampil = df[df["Nama Tempat"] == pilihan_user]
            # Pusatkan peta ke tempat yang dicari
            start_lat = df_tampil.iloc[0]["Latitude"]
            start_lng = df_tampil.iloc[0]["Longitude"]
            zoom_level = 17 # Zoom in lebih dekat
        else:
            df_tampil = df
            start_lat, start_lng = -6.9175, 107.6191 # Tengah Bandung
            zoom_level = 13

        st.subheader("📋 Daftar Lengkap")
        # Tampilkan tabel yang lebih cantik
        st.dataframe(
            df_tampil[["Nama Tempat", "Kategori", "Rating", "Harga"]], 
            use_container_width=True,
            hide_index=True
        )

    with col2:
        st.subheader("🗺️ Peta Lokasi (Klik Marker)")
        # Inisialisasi Peta
        m = folium.Map(location=[start_lat, start_lng], zoom_start=zoom_level)

        # Tambahkan marker
        for index, row in df_tampil.iterrows():
            # Bedakan warna marker (Cafe = Biru, Resto = Merah)
            marker_color = "blue" if row["Kategori"] == "Cafe" else "red"
            marker_icon = "coffee" if row["Kategori"] == "Cafe" else "cutlery"
            
            # HTML Popup yang elegan
            popup_html = f"""
            <div style="width:220px; font-family:sans-serif;">
                <h4 style="margin-bottom:5px; color:#D35400;">{row['Nama Tempat']}</h4>
                <p style="margin:2px 0;"><b>Kategori:</b> {row['Kategori']}</p>
                <p style="margin:2px 0;"><b>Rating:</b> ⭐ {row['Rating']}</p>
                <p style="margin:2px 0;"><b>Harga:</b> {row['Harga']}</p>
                <hr style="margin:10px 0;">
                <a href="{row['Google Maps Link']}" target="_blank" 
                   style="background-color:#27AE60; color:white; padding:8px 10px; text-decoration:none; border-radius:5px; display:block; text-align:center; font-weight:bold;">
                   📍 Arahkan ke Google Maps
                </a>
            </div>
            """
            
            folium.Marker(
                location=[row["Latitude"], row["Longitude"]],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"Klik untuk info {row['Nama Tempat']}",
                icon=folium.Icon(color=marker_color, icon=marker_icon, prefix='fa')
            ).add_to(m)

        # Tampilkan peta
        st_data = st_folium(m, width=800, height=550)