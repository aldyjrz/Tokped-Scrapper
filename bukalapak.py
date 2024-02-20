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
    driver = uc.Chrome(service=webdriver_service, options=options, version_main=109)
    # URL dasar pencarian Tokopedia dengan kata kunci
    base_url = f'https://www.bukalapak.com/products?from=omnisearch&search[keywords]={keyword}'
    
    # Inisialisasi list kosong untuk menyimpan data hasil scraping
    data = []

    # Looping melalui setiap halaman pencarian
    for page in range(1, total_pages + 1):
        # URL halaman pencarian saat ini
        page_url = f'{base_url}&page={page}'
        
        # Buka halaman pencarian menggunakan WebDriver
        driver.get(page_url)
        
        # Tunggu hingga elemen dengan CSS selector container bukalapak
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.bl-flex-container')))
        
        # Tunggu 2 detik untuk memastikan halaman sepenuhnya dimuat
        time.sleep(5)

        # Parse halaman menggunakan BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Scrap data produk dari halaman web
        for item in soup.find_all('div', class_='bl-flex-container'):
            try:
                # Scrap nama produk
                product_name_element = item.find('p', class_='bl-text bl-text--body-14 bl-text--secondary bl-text--ellipsis__2')
                product_name = product_name_element.text.strip() if product_name_element else ''
                if not product_name:
                    continue  # Lewati iterasi ini jika tidak ada nama produk

              
                # Scrap Harga Normal
                price_normal_element = item.find('p', class_='bl-text bl-text--semi-bold bl-text--ellipsis__1 bl-product-card-new__price')
                price_normal = price_normal_element.text.strip() if price_normal_element else ''

                # Scrap Diskon
               
                # Scrap jumlah tejrual
                sold_element = item.find('p', class_='bl-text bl-text--caption-12 bl-text--secondary bl-product-card-new__sold-count')
                sold = sold_element.text.strip() if sold_element else ''

             
                # Cek apakah ada rating atau tidak
                rate_element = item.find('p', class_='bl-text bl-text--caption-12 bl-text--bold')
                rate = rate_element.text.strip() if rate_element else ''

             
                # Scrap detail alamat
                location_element = item.find('p', class_='bl-text bl-text--caption-12 bl-text--secondary bl-text--ellipsis__1 bl-product-card-new__store-location')
                location = location_element.text.strip() if location_element else ''
                
                seller_element = item.find('p', class_='bl-text bl-text--caption-12 bl-text--secondary bl-text--ellipsis__1 bl-product-card-new__store-name')
                seller = seller_element.text.strip() if seller_element else ''

                # Menambahkan data produk ke dalam list 'data'
                data.append(
                    {
                        'Produk': product_name,
                        'Penjual' : seller,
                        'Lokasi': location,
                        'Harga Normal': price_normal or '0',  # Jika tidak ada, isi dengan '0'
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
    keyword = input("Masukkan keyword produk yang ingin Anda cari di Bukalapak: ")
    # Masukkan jumlah halaman yang ingin di-scrape
    total_pages = int(input("Masukkan jumlah halaman yang ingin Anda scraping: "))

    # Panggil method get_data untuk melakukan scraping
    data = get_data(keyword, total_pages)
    
    # Konversi data menjadi DataFrame menggunakan pandas
    df = pd.DataFrame(data)
    # Simpan DataFrame sebagai file CSV dengan nama 'dataset.csv'
    df.to_excel('bukalapak-'+keyword+'dataset.xlsx', index=False)
