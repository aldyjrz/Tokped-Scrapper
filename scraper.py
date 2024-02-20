import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd 
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import undetected_chromedriver as uc


# Metode untuk mendapatkan data dari Tokopedia
def get_data(keyword, total_pages):
    # Setup ChromeDriver using WebDriverManager
    options = webdriver.ChromeOptions()

    webdriver_service = Service(ChromeDriverManager().install())
    webdriver_service.start()
    driver = uc.Chrome(service=webdriver_service, options=options, version_main=121)
    # URL dasar pencarian Tokopedia dengan kata kunci
    base_url = f'https://www.tokopedia.com/search?q={keyword}'
    
    # Inisialisasi list kosong untuk menyimpan data hasil scraping
    data = []

    # Looping melalui setiap halaman pencarian
    for page in range(1, total_pages + 1):
        # URL halaman pencarian saat ini
        page_url = f'{base_url}&page={page}'
        
        # Buka halaman pencarian menggunakan WebDriver
        driver.get(page_url)
        
        # Tunggu hingga elemen dengan CSS selector '#zeus-root' muncul
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#zeus-root')))
        
        # Tunggu 2 detik untuk memastikan halaman sepenuhnya dimuat
        time.sleep(2)

        # Parse halaman menggunakan BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Scrap data produk dari halaman web
        for item in soup.find_all('div', class_='css-54k5sq'):
            try:
                # Scrap nama produk
                product_name_element = item.find('div', class_='prd_link-product-name css-3um8ox')
                product_name = product_name_element.text.strip() if product_name_element else ''
                if not product_name:
                    continue  # Lewati iterasi ini jika tidak ada nama produk

                # Scrap URL Gambar
                image_element = item.find('div', class_='pcv3_img_container css-1mygogd')
                image_url = image_element.find('img')['src'] if image_element else ''

                # Scrap Harga Normal
                price_normal_element = item.find('div', class_='prd_label-product-slash-price css-xfl72w')
                price_normal = price_normal_element.text.strip() if price_normal_element else ''

                # Scrap Diskon
                discount_element = item.find('div', class_='prd_badge-product-discount css-1xelcdh')
                discount = discount_element.text.strip() if discount_element else ''

                # Scrap Harga Diskon
                price_element = item.find('div', class_='prd_link-product-price css-h66vau')
                price_discount = price_element.text.strip() if price_element else ''

                # Jika tidak ada diskon, pindahkan data dari kolom Harga Diskon ke kolom Harga Normal
                if not discount:
                    price_normal = price_discount
                    price_discount = ''

                # Cek apakah ada rating atau tidak
                rate_element = item.find('span', class_='prd_rating-average-text css-t70v7i')
                rate = rate_element.text.strip() if rate_element else ''

                # Cek apakah ada item terjual atau tidak
                sold_element = item.find('span', class_='prd_label-integrity css-1sgek4h')
                sold = sold_element.text.strip() if sold_element else '0'

                # Scrap detail alamat
                location_element = item.find('span', class_='prd_link-shop-loc css-1kdc32b flip')
                location = location_element.text.strip() if location_element else ''
                
                seller_element = item.find('span', class_='prd_link-shop-name css-1kdc32b flip')
                seller = seller_element.text.strip() if seller_element else ''

                # Menambahkan data produk ke dalam list 'data'
                data.append(
                    {
                        'Produk': product_name,
                        'URL Gambar': image_url,
                        'Penjual' : seller,
                        'Lokasi': location,
                        'Harga Normal': price_normal or '0',  # Jika tidak ada, isi dengan '0'
                        'Diskon': discount or '',  # Jika tidak ada diskon, nilai default adalah string kosong
                        'Harga Diskon': price_discount or '0',  # Jika tidak ada, isi dengan '0'
                        'Rate': rate or '0',  # Jika tidak ada, isi dengan '0'
                        'Terjual': sold or '0'  # Jika tidak ada, isi dengan '0'
                    }
                )
            except AttributeError as e:  # Tangani AttributeError yang mungkin terjadi saat menemukan elemen yang tidak diharapkan
                print(f"Error: {e}")  # Cetak pesan kesalahan
                continue  # Lanjutkan ke iterasi berikutnya jika terjadi AttributeError

        # Tunggu 1 detik sebelum melanjutkan ke halaman berikutnya
        time.sleep(1)

    # Tutup WebDriver setelah selesai scraping
    driver.close()

    # Kembalikan data hasil scraping
    return data

# Jalankan kode jika file ini dieksekusi langsung (bukan diimpor sebagai modul)
if __name__ == "__main__":
    # Masukkan keyword produk dari pengguna
    keyword = input("Masukkan keyword produk yang ingin Anda cari di Tokopedia: ")
    # Masukkan jumlah halaman yang ingin di-scrape
    total_pages = int(input("Masukkan jumlah halaman yang ingin Anda scraping: "))

    # Panggil method get_data untuk melakukan scraping
    data = get_data(keyword, total_pages)
    
    # Konversi data menjadi DataFrame menggunakan pandas
    df = pd.DataFrame(data)
    # Simpan DataFrame sebagai file CSV dengan nama 'dataset.csv'
    df.to_excel('dataset.xlsx', index=False)
