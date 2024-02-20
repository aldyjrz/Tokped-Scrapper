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
    base_url = f'https://shopee.co.id/search?keyword={keyword}&sortBy=sales'
    
    # Inisialisasi list kosong untuk menyimpan data hasil scraping
    data = []

    # Looping melalui setiap halaman pencarian
    for page in range(1, total_pages + 1):
        # URL halaman pencarian saat ini
        page_url = f'{base_url}&page={page}'
        
        # Buka halaman pencarian menggunakan WebDriver
        driver.get(page_url)
        
        # Tunggu hingga elemen dengan CSS selector '#zeus-root' muncul
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.shopee-search-item-result__items')))
        
        # Tunggu 2 detik untuk memastikan halaman sepenuhnya dimuat
        time.sleep(5)

        # Parse halaman menggunakan BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Scrap data produk dari halaman web
        for item in soup.find_all('section', class_='shopee-search-item-result'):
            try:
                # Scrap nama produk
                product_name_element = item.find('div', class_='xA2DZd tYvyWM wupGTj')
                product_name = product_name_element.text.strip() if product_name_element else ''
                if not product_name:
                    continue  # Lewati iterasi ini jika tidak ada nama produk

                

                # Scrap Harga Normal
                price_normal_element = item.find('span', class_='_0av2Hk Eo28A7 iyLZ96')
                price_normal = price_normal_element.text.strip() if price_normal_element else ''

                # Scrap Diskon
                discount_element = item.find('span', class_='_0av2Hk Eo28A7 iyLZ96')
                discount = discount_element.text.strip() if discount_element else ''

                # Scrap Harga Diskon
                price_element = item.find('div', class_='_7s1MaR')
                price_discount = price_element.text.strip() if price_element else ''

                # Jika tidak ada diskon, pindahkan data dari kolom Harga Diskon ke kolom Harga Normal
                if not discount:
                    price_normal = price_discount
                    price_discount = ''

              
                # Cek apakah ada item terjual atau tidak
                sold_element = item.find('div', class_='L68Ib9 s3wNiK')
                sold = sold_element.text.strip() if sold_element else '0'

                
                location_element = item.find('div', class_='wZEyNc')
                location = location_element.text.strip() if location_element else ''

                # Menambahkan data produk ke dalam list 'data'
                data.append(
                    {
                        'Produk': product_name, 
                        'Lokasi': location,
                        'Harga Normal': price_normal or '0',  # Jika tidak ada, isi dengan '0'
                        'Diskon': discount or '',  # Jika tidak ada diskon, nilai default adalah string kosong
                        'Harga Diskon': price_discount or '0',  # Jika tidak ada, isi dengan '0'
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
    keyword = input("Masukkan keyword produk yang ingin Anda cari di Shopee: ")
    # Masukkan jumlah halaman yang ingin di-scrape
    total_pages = int(input("Masukkan jumlah halaman yang ingin Anda scraping: "))

    # Panggil method get_data untuk melakukan scraping
    data = get_data(keyword, total_pages)
    
    # Konversi data menjadi DataFrame menggunakan pandas
    df = pd.DataFrame(data)
    # Simpan DataFrame sebagai file CSV dengan nama 'dataset.csv'
    df.to_excel('shopee-'+keyword+'-dataset.xlsx', index=False)
