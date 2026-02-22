import streamlit as st
import pandas as pd
import base64
import folium
from streamlit_folium import st_folium

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Peta Bukber Bandung", layout="wide", page_icon="🌙")

# --- BACA FOTO KELAS JADI BASE64 ---
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        return "" # Jika foto tidak ditemukan, biarkan kosong

# Pastikan nama filenya sudah benar ya!
img_base64 = get_base64_image("foto_kelas.jpg")

# --- BACA FOTO KELAS JADI BASE64 ---
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        return "" 

img_base64 = get_base64_image("foto_kelas.jpg")

# --- CUSTOM CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #FDF6E3; }}
    html, body, [class*="css"] {{ color: #2C3E50 !important; }}
    h1, h2, h3, h4, h5, h6, p, div, span {{ color: #2C3E50 !important; }}
    
    /* 1. CONTAINER FOTO KELAS TRANSPARAN (Lebih jelas fotonya) */
    .kelas-container-transparan {{
        border: 3px solid #D35400;
        border-radius: 15px;
        padding: 30px;
        margin: 20px auto 30px auto;
        max-width: 800px;
        text-align: center;
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        /* Angka 0.70 ini membuat foto lebih tembus pandang/terlihat jelas */
        background-image: 
            linear-gradient(rgba(253, 246, 227, 0.70), rgba(253, 246, 227, 0.70)),
            url("data:image/jpeg;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    .kelas-judul {{ font-family: 'Trebuchet MS', sans-serif; font-weight: bold; font-size: 22px; margin-bottom: 15px; color: #D35400 !important; text-shadow: 1px 1px 1px rgba(255,255,255,0.8); }}
    .kelas-isi {{ font-size: 16px; line-height: 1.6; color: #2C3E50 !important; font-weight: 600; text-shadow: 1px 1px 1px rgba(255,255,255,0.8); }}
    
    /* 2. BORDER BIASA UNTUK BAGIAN BAWAH */
    .kotak-pengumuman {{
        border: 3px solid #2C3E50; /* Border warna Navy */
        border-radius: 15px;
        padding: 20px 30px;
        background-color: #FFFFFF; /* Putih polos tanpa foto */
        margin: 20px auto;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}
    
    /* Memaksa form streamlit memiliki border senada secara otomatis */
    [data-testid="stForm"] {{
        border: 3px solid #2C3E50 !important;
        border-radius: 15px;
        padding: 25px;
        background-color: #FFFFFF;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}

    /* 3. PERBAIKAN WARNA KOTAK INPUT & DROPDOWN AGAR RAPI */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {{
        background-color: #2C3E50 !important; 
        border-radius: 8px;
    }}
    div[data-baseweb="select"] *, div[data-baseweb="input"] input {{ color: white !important; }}
    div[role="listbox"] [role="option"] {{ color: white !important; font-weight: 500; }}
    .stSelectbox label, .stTextInput label {{ color: #2C3E50 !important; font-weight: bold; }}
    
    /* Style lainnya */
    h1 {{ color: #D35400 !important; font-family: 'Trebuchet MS', sans-serif; text-align: center; text-shadow: 1px 1px 2px rgba(0,0,0,0.1); }}
    .rekomendasi-card {{ background-color: #FFFFFF; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.15); text-align: center; border-top: 4px solid #D35400; margin-bottom: 10px; transition: transform 0.2s; }}
    .rekomendasi-card:hover {{ transform: scale(1.05); }}
    .rating-bintang {{ color: #F39C12 !important; font-size: 18px; font-weight: bold; }}
    .harga-tag {{ color: #27AE60 !important; font-weight: 600; font-size: 14px; }}
    .area-badge {{ background-color: #E67E22; color: white !important; padding: 2px 8px; border-radius: 12px; font-size: 11px; display: inline-block; margin-bottom: 5px; }}
    </style>
""", unsafe_allow_html=True)

st.title("🌙 Peta Rekomendasi Tempat Bukber di Bandung")

# --- CONTAINER PENGUMUMAN DENGAN BACKGROUND FOTO KELAS ---
# Kita bungkus teksnya dalam div yang menggunakan class CSS baru tadi
st.markdown("""
    <div class="kelas-container-transparan">
        <div class="kelas-judul">
            Rekomendasi tempat bukber untuk Jumat 6 Maret 2026
        </div>
        <div class="kelas-isi">
            <p>📢 <b>Perhatian Teman-teman!</b></p>
            <p>Pilih tempatnya yang sesuai ya. Nanti diadakan lagi polling Top 5 tempat bukber setelah didiskusikan. Jangan lupa list nama di grup yaa! ✨</p>
        </div>
    </div>
""", unsafe_allow_html=True)
# ---------------------------------------------------------

st.write("---")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data_bukber_bandung.csv")
    except FileNotFoundError:
        st.error("File data_bukber_bandung.csv belum ada. Tolong jalankan scraper.py.")
        df = pd.DataFrame(columns=["Nama Tempat", "Kategori", "Area", "Rating", "Harga", "Latitude", "Longitude", "Google Maps Link"])
    
    # Jika file CSV lama belum ada kolom 'Area', kita amankan agar tidak error
    if "Area" not in df.columns:
        df["Area"] = "Tidak Diketahui"
        
    return df

df = load_data()

if not df.empty:
    # --- BAGIAN FILTER (WILAYAH & KATEGORI) ---
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        # Filter Wilayah
        daftar_area = ["Semua Wilayah"] + sorted(df[df["Area"] != "Tidak Diketahui"]["Area"].unique().tolist())
        pilihan_area = st.selectbox("📍 Pilih Wilayah:", daftar_area)
        
    with col_filter2:
        # Tambahan bonus: Filter Kategori!
        daftar_kategori = ["Semua Kategori", "Rumah Makan", "Cafe"]
        pilihan_kategori = st.selectbox("🍽️ Pilih Kategori Tempat:", daftar_kategori)

    # Proses filtering dataframe
    df_filtered = df.copy()
    if pilihan_area != "Semua Wilayah":
        df_filtered = df_filtered[df_filtered["Area"] == pilihan_area]
    if pilihan_kategori != "Semua Kategori":
        df_filtered = df_filtered[df_filtered["Kategori"] == pilihan_kategori]

    st.write("---")

    # --- FITUR TOP 5 REKOMENDASI (Sesuai Filter) ---
    if not df_filtered.empty:
        st.subheader(f"🏆 Top Rekomendasi di {pilihan_area if pilihan_area != 'Semua Wilayah' else 'Bandung'}")
        top_5_df = df_filtered.sort_values(by="Rating", ascending=False).head(5)
        
        cols = st.columns(len(top_5_df))
        for i, (index, row) in enumerate(top_5_df.iterrows()):
            with cols[i]:
                st.markdown(f"""
                    <div class="rekomendasi-card">
                        <div class="area-badge">{row.get('Area', '-')}</div>
                        <h5 style="color:#2C3E50; margin-bottom:5px; font-size:15px;">{row['Nama Tempat']}</h5>
                        <div class="rating-bintang">⭐ {row['Rating']}</div>
                        <div class="harga-tag">💰 {row['Harga']}</div>
                        <p style="font-size:12px; color:#95A5A6; margin-top:5px;">{row['Kategori']}</p>
                        <a href="{row['Google Maps Link']}" target="_blank" style="text-decoration:none; font-size:12px; background-color:#3498DB; color:white; padding:4px 8px; border-radius:4px;">Buka Map</a>
                    </div>
                """, unsafe_allow_html=True)

        st.write("---")

        # --- TATA LETAK DAFTAR & PETA ---
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("📋 Daftar Tempat")
            # Tampilkan tabel daftar tempat
            st.dataframe(
                df_filtered[["Nama Tempat", "Kategori", "Area", "Rating"]], 
                use_container_width=True,
                hide_index=True
            )

        with col2:
            st.subheader("🗺️ Peta Lokasi")
            # Pusatkan peta. Jika pilih area tertentu, ambil kordinat rata-rata dari area tersebut
            start_lat = df_filtered["Latitude"].mean()
            start_lng = df_filtered["Longitude"].mean()
            zoom_level = 14 if pilihan_area != "Semua Wilayah" else 12

            m = folium.Map(location=[start_lat, start_lng], zoom_start=zoom_level)

            for index, row in df_filtered.iterrows():
                marker_color = "blue" if row["Kategori"] == "Cafe" else "red"
                marker_icon = "coffee" if row["Kategori"] == "Cafe" else "cutlery"
                
                popup_html = f"""
                <div style="width:220px; font-family:sans-serif;">
                    <div style="background-color:#E67E22; color:white; padding:2px 5px; border-radius:3px; font-size:10px; display:inline-block;">{row.get('Area', '-')}</div>
                    <h4 style="margin-bottom:5px; margin-top:5px; color:#D35400;">{row['Nama Tempat']}</h4>
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

            st_data = st_folium(m, width=800, height=550)
    else:
        st.warning("Tidak ada data tempat untuk filter yang dipilih.")
        
        
# ... (kode peta folium sebelumnya di atas) ...
    
    # --- PESAN PENUTUP & FORM ---
    st.write("---")
    
   # Membungkus teks peringatan dengan border biasa
    st.markdown("""
        <div class="kotak-pengumuman">
            <h4 style="color: #D35400 !important; margin-bottom: 10px;">📢 Perhatian Teman-teman!</h4>
            <p>Pilih tempatnya yang sesuai ya teman-teman. Nanti diadakan lagi polling Top 5 tempat bukber setelah didiskusikan.</p>
            <p>Jika teman-teman punya saran tempat lain, boleh tambahkan saja di grup yaa! 😉</p>
            <p style="font-weight: bold;">Jangan lupa list nama di grup yaa! ✨</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='text-align: center; color: #2C3E50 !important; margin-top: 20px;'>🗳️ Form Pilihan Tempat Bukber</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #7F8C8D !important;'>Isi nama kamu dan pilih tempat favoritmu dari tabel di atas!</p>", unsafe_allow_html=True)

    # ... (lanjut ke kodingan form pilihan_bukber kamu yang sudah ada) ...
    # Form-nya otomatis akan punya border juga karena efek CSS [data-testid="stForm"] di atas!

    # Mengambil daftar nama tempat dari data yang sedang difilter
    daftar_pilihan_tempat = df_filtered["Nama Tempat"].tolist()

    # Membuat Form
    with st.form("form_pilihan_bukber"):
        nama_peserta = st.text_input("Nama Lengkap / Panggilan:")
        tempat_pilihan = st.selectbox("Pilih Tempat Favoritmu:", ["-- Pilih Tempat --"] + daftar_pilihan_tempat)
        
        # Tombol Submit Form
        submit_button = st.form_submit_button("Siapkan Pesan WhatsApp 🚀")

    # Jika tombol ditekan
    if submit_button:
        if nama_peserta.strip() == "":
            st.error("Eh, namanya jangan lupa diisi dong! 😅")
        elif tempat_pilihan == "-- Pilih Tempat --":
            st.error("Pilih tempatnya dulu ya dari menu dropdown!")
        else:
            # Membuat template pesan untuk dikirim ke grup
            pesan = f"Halo teman-teman! 👋%0A%0AAku udah milih nih:%0ANama: *{nama_peserta}*%0APilihan Bukber: *{tempat_pilihan}*%0A%0ASiap ikut bukber 6 Maret 2026! 🔥"
            
            # Trik: Menggunakan api.whatsapp tanpa nomor tujuan agar user bisa memilih grup sendiri
            link_wa = f"https://api.whatsapp.com/send?text={pesan}"
            
            st.success(f"Mantap, {nama_peserta}! Pesan otomatis sudah siap.")
            
            # Menampilkan tombol hijau WhatsApp
            st.markdown(f"""
                <div style="text-align: center; margin-top: 15px;">
                    <a href="{link_wa}" target="_blank" style="background-color: #25D366; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        💬 Kirim Pilihan ke WA Panitia
                    </a>
                </div>
            """, unsafe_allow_html=True)
            
            st.info("💡 Klik tombol hijau di atas untuk mengirimkan otomatis ke WhatsApp Panitia, atau bisa juga kamu ketik manual di Grup WA kita!")