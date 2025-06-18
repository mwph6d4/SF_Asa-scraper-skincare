# scrape.py
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import csv  # <-- Penting untuk quoting

def scrape_main_banner_sociolla(driver):
    # (Tidak ada perubahan di fungsi ini)
    pass  # kamu bisa isi ulang bagian ini jika ingin digunakan

def scrape_sociolla(driver, search_keyword):
    print(f"Starting Sociolla scraping for keyword: {search_keyword}...")
    all_products_from_listing = []
    final_products_with_rating = []

    base_url = f'https://www.sociolla.com/search?q={search_keyword}'
    driver.get(base_url)

    try:
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.product__name'))
        )
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
    except Exception as e:
        print(f"  FAILED TO LOAD PRODUCTS: {type(e).__name__} - {e}")
        return []

    html = driver.execute_script("return document.documentElement.innerHTML")
    soup = BeautifulSoup(html, 'html.parser')

    product_items = soup.find_all('div', class_='product--v3')
    if not product_items:
        print("  No products found.")
        return []

    for item in product_items:
        name_tag = item.select_one('p.product__name a.product__name')
        brand_tag = item.select_one('a.product__brand')
        image_tag = item.select_one('img.product__img')

        if not name_tag:
            continue

        product_name = name_tag.get_text(strip=True)
        detail_url = name_tag.get('href')
        if detail_url and not detail_url.startswith(('http://', 'https://')):
            detail_url = "https://www.sociolla.com" + detail_url

        image_url = image_tag.get('data-src') or image_tag.get('src') if image_tag else None
        if image_url and not image_url.startswith(('http://', 'https://')):
            image_url = "https://s3-ap-southeast-1.amazonaws.com" + image_url

        all_products_from_listing.append({
            'product_name': product_name,
            'product_price': None,
            'source_website': 'Sociolla',
            'brand': brand_tag.get_text(strip=True) if brand_tag else None,
            'image_url': image_url,
            'rating': None,
            'detail_page_url': detail_url,
            'original_price': None,
            'saved_amount': None
        })

    print(f"Collected {len(all_products_from_listing)} products. Visiting detail pages...")

    for idx, product in enumerate(all_products_from_listing):
        detail_url = product['detail_page_url']
        if not detail_url or "/e-gift-card/" in detail_url:
            continue

        print(f"  [{idx+1}/{len(all_products_from_listing)}] Visiting {detail_url}")
        driver.get(detail_url)

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.title'))
            )
            # Menunggu elemen konten detail dimuat
            WebDriverWait(driver, 20).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'span.after')),
                    EC.presence_of_element_located((By.ID, 'product-descriptions')), # Ini mungkin tab deskripsi default
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.tabs-content div.tabs-item[style*="display: block"]')) # Menunggu tab aktif
                )
            )
            time.sleep(2) # Beri sedikit waktu ekstra untuk rendering JS
        except Exception as e:
            print(f"  Detail page failed to load or content not found: {type(e).__name__} - {e}")
            continue

        detail_html = driver.execute_script("return document.documentElement.innerHTML")
        detail_soup = BeautifulSoup(detail_html, 'html.parser')

        price_tag = detail_soup.select_one('span.after') or detail_soup.select_one('span.after-no-save')
        ori_price_tag = detail_soup.select_one('span.ori')
        save_tag = detail_soup.select_one('span.save')
        rating_tag = detail_soup.select_one('li.rating')

        product['product_price'] = price_tag.get_text(strip=True) if price_tag else None
        product['original_price'] = ori_price_tag.get_text(strip=True) if ori_price_tag else None
        product['saved_amount'] = save_tag.get_text(strip=True) if save_tag else None

        try:
            product['rating'] = float(rating_tag.get_text(strip=True)) if rating_tag else None
        except ValueError:
            product['rating'] = None

        # --- Deskripsi, Cara Pakai, Ingredients ---
        description = None
        how_to_use = None
        ingredients = None

        tab_titles = detail_soup.select('div.description.tabbedproducts ul.tabs li a')
        tab_contents = detail_soup.select('div.description.tabbedproducts div.tabs-content div.tabs-item')

        print(f"\n--- DEBUGGING DETAIL PAGE FOR: {product['product_name']} ({detail_url}) ---")
        print(f"  Found {len(tab_titles)} tabs in total.")

        for i, tab in enumerate(tab_titles):
            title = tab.get('title', '').strip().lower()
            content = tab_contents[i] if i < len(tab_contents) else None
            
            content_text = ""
            if content:
                content_text = content.get_text(separator=' ', strip=True)
                print(f"    Tab '{title}': Content Length = {len(content_text)} chars. Start: '{content_text[:100]}...'")
            else:
                print(f"    WARNING: Content element for tab '{title}' not found (index {i}).")


            if not content:
                print(f"    WARNING: Content for tab '{title}' is empty or not found.")
                continue
            text = content.get_text(separator=' ', strip=True)
            if title == 'description':
                description = text
            elif title == 'how to use':
                how_to_use = text
            elif title == 'ingredients':
                ingredients = text
        
        # --- DEBUGGING BARU: Tambahkan ini setelah ekstraksi ---
        print(f"  Extracted Description: {description[:100] if description else 'NONE'}")
        print(f"  Extracted How To Use: {how_to_use[:100] if how_to_use else 'NONE'}")
        print(f"  Extracted Ingredients: {ingredients[:100] if ingredients else 'NONE'}")
        print("--------------------------------------------------\n")
        # --- Akhir DEBUGGING BARU ---

        product['description'] = description
        product['how_to_use'] = how_to_use
        product['ingredients'] = ingredients

        del product['detail_page_url']
        final_products_with_rating.append(product)

    print(f"Scraping finished. Total: {len(final_products_with_rating)}")
    return final_products_with_rating

# --- Main Execution ---
if __name__ == '__main__':
    if not os.path.exists('scraped_data'):
        os.makedirs('scraped_data')

    chromedriver_path = r'C:\Users\DELL\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe'

    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    # chrome_options.add_argument('--headless') # Tidak perlu dikomentari di sini jika tidak ada sebelumnya

    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    search_keywords_for_sociolla = ['wardah', 'somethinc', 'azarine', 'loreal paris', 'maybelline']
    all_combined = []

    for keyword in search_keywords_for_sociolla:
        products = scrape_sociolla(driver, keyword)
        all_combined.extend(products)
        if products:
            df = pd.DataFrame(products)
            csv_file = f'scraped_data/sociolla_{keyword.replace(" ", "_")}_products.csv'
            df.to_csv(csv_file, index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
            print(f"Saved: {csv_file}")

    driver.quit()
    print("Driver closed.")

    if all_combined:
        df_all = pd.DataFrame(all_combined)
        df_all.to_csv('scraped_data/sociolla_all_products.csv', index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
        print("Saved combined data to sociolla_all_products.csv")