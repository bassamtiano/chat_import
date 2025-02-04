import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from tqdm import tqdm  # Import tqdm for progress tracking

# Folder for saving PDF files
download_dir = "pdf_files"
os.makedirs(download_dir, exist_ok=True)

# Function to download PDFs with progress bar
def download_pdf(url, save_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get the total file size to show progress
        total_size = int(response.headers.get('content-length', 0))
        
        with open(save_path, 'wb') as pdf_file:
            # Progress bar for downloading PDF
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=save_path) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        pdf_file.write(chunk)
                        pbar.update(len(chunk))  # Update progress bar with the chunk size
        print(f"Downloaded: {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")

# Setup Selenium WebDriver
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run headlessly (without opening the browser)
    driver = webdriver.Chrome(options=options)
    return driver

# Function to search and download PDFs from peraturan.go.id
def search_and_download_pdfs(query, start_page=2, end_page=38, num_results_per_page=20):
    driver = get_driver()
    driver.get(query)  # Open the search URL
    time.sleep(3)  # Wait for the page to load
    
    pdf_urls = []
    try:
        print(f"Starting to fetch PDF URLs from page {start_page} to page {end_page}...")

        # Progress bar for result pages
        with tqdm(total=(end_page - start_page + 1), desc="Fetching Pages", unit="page") as page_pbar:
            for page_num in range(start_page, end_page + 1):
                # Navigate to the correct page
                page_url = f"{query}&page={page_num}"
                driver.get(page_url)
                time.sleep(3)  # Wait for the page to load

                # Find all links to PDFs on the page
                search_results = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
                
                # Extract PDF URLs
                for result in search_results:
                    pdf_url = result.get_attribute("href")
                    if pdf_url.endswith(".pdf") and pdf_url not in pdf_urls:
                        pdf_urls.append(pdf_url)
                
                # Update progress bar for each page
                page_pbar.update(1)

                

        print(f"\nTotal {len(pdf_urls)} PDFs found.")

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        driver.quit()

    # Download PDFs
    print(f"Starting download of {len(pdf_urls)} PDFs...\n")
    with tqdm(total=len(pdf_urls), desc="Downloading PDFs", unit="file") as download_pbar:
        for i, url in enumerate(pdf_urls, start=1):
            filename = os.path.basename(url)
            save_path = os.path.join(download_dir, filename)
            download_pdf(url, save_path)
            download_pbar.update(1)  # Update progress bar for each downloaded file

# Example search URL
search_url = 'https://peraturan.go.id/cari?PeraturanSearch%5Btentang%5D=impor&PeraturanSearch%5Bnomor%5D=&PeraturanSearch%5Btahun%5D=&PeraturanSearch%5Bjenis_peraturan_id%5D=&PeraturanSearch%5Bpemrakarsa_id%5D=&PeraturanSearch%5Bstatus%5D=Berlaku'

# Search and download PDFs (page 1 to page 38, maximum 20 PDFs per page)
search_and_download_pdfs(search_url, start_page=1, end_page=38, num_results_per_page=30)
