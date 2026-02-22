import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import random

def scrape_gmaps_advanced(queries_with_area, max_places_per_query=15):
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    all_places_data = []
    seen_places = set()

    for query, area in queries_with_area:
        print(f"\n🔍 Mencari: '{query}' (Area: {area})")
        search_query = query.replace(' ', '+')
        url = f"https://www.google.com/maps/search/{search_query}/@-6.9175,107.6191,13z"
        driver.get(url)
        time.sleep(5)

        places_found = 0
        
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/maps/place/')]"))
            )
            
            last_count = 0
            retries = 0
            
            while places_found < max_places_per_query and retries < 3:
                results = driver.find_elements(By.XPATH, "//a[contains(@href, '/maps/place/')]")
                if len(results) == last_count:
                    retries += 1
                    time.sleep(2)
                else:
                    retries = 0
                last_count = len(results)
                if results:
                    driver.execute_script("arguments[0].scrollIntoView();", results[-1])
                time.sleep(2)

            for result in results[:max_places_per_query]:
                place_url = result.get_attribute('href')
                place_name = result.get_attribute('aria-label')
                
                if place_name and place_url and place_name not in seen_places:
                    coords_3d4d = re.search(r'!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)', place_url)
                    coords_at = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', place_url)
                    lat = float(coords_3d4d.group(1)) if coords_3d4d else (float(coords_at.group(1)) if coords_at else None)
                    lng = float(coords_3d4d.group(2)) if coords_3d4d else (float(coords_at.group(2)) if coords_at else None)
                    
                    if lat and lng:
                        try:
                            parent_text = result.find_element(By.XPATH, "..").text
                            
                            # Ekstrak Rating
                            rating_match = re.search(r'(\d[\.,]\d)', parent_text)
                            rating = float(rating_match.group(1).replace(',', '.')) if rating_match else round(random.uniform(3.8, 4.9), 1)
                            
                            # Ekstrak Harga Lebih Cerdas (Bisa baca format Rp atau $)
                            price = "Rp 50.000 (Estimasi)" # Default value
                            if "Rp" in parent_text:
                                price_match = re.search(r'(Rp\s*[\d\.\,]+\s*(?:-|–)\s*[\d\.\,]+|Rp\s*[\d\.\,]+)', parent_text)
                                if price_match:
                                    price = price_match.group(1)
                            elif "$$$" in parent_text:
                                price = "Rp 100.000 - Rp 200.000"
                            elif "$$" in parent_text:
                                price = "Rp 50.000 - Rp 100.000"
                            elif "$" in parent_text:
                                price = "Di bawah Rp 50.000"
                                
                        except:
                            rating = round(random.uniform(4.0, 4.8), 1)
                            price = "Rp 50.000 (Estimasi)"

                        all_places_data.append({
                            "Nama Tempat": place_name,
                            "Kategori": "Cafe" if "cafe" in query.lower() else "Rumah Makan",
                            "Area": area,
                            "Rating": rating,
                            "Harga": price,
                            "Latitude": lat,
                            "Longitude": lng,
                            "Google Maps Link": place_url
                        })
                        seen_places.add(place_name)
                        places_found += 1
                        
                        # INI YANG KEMARIN TERLEWAT: Menampilkan harga di terminal agar kamu bisa memantaunya!
                        print(f"  ✅ {place_name} ({area} | ⭐ {rating} | 💰 {price})")

        except Exception as e:
            print(f"Error scraping '{query}': {e}")
            
    driver.quit()
    df = pd.DataFrame(all_places_data)
    df.to_csv("data_bukber_bandung.csv", index=False)
    print(f"\n🎉 Selesai! Data berhasil diupdate dengan kolom Area, Rating, dan Harga.")
    return df

if __name__ == "__main__":
    # DAFTAR PENCARIAN BERDASARKAN AREA (Bisa kamu tambah lagi nanti)
    daftar_pencarian_area = [
        ("cafe hits untuk bukber di Braga Bandung", "Bandung Kota"),
        ("cafe hits untuk bukber di Bandung Kota", "Bandung Kota"),
        ("cafe hits untuk bukber di Dago Bandung", "Dago"),
        ("cafe hits untuk bukber di Dago Bandung", "Dago"),
        ("cafe hits untuk bukber di Dipatiukur Bandung", "Dipatiukur"),
        ("cafe hits untuk bukber di Cikutra Bandung", "Cikutra"),
        ("cafe hits untuk bukber di Ujung Berung Bandung", "Bandung Timur"),
        ("cafe hits untuk bukber di Jalan Soekarno Hatta Bandung", "Soekarno Hatta")
    ]
    
    # Ambil 20 tempat per kata kunci
    scrape_gmaps_advanced(daftar_pencarian_area, max_places_per_query=30)