import os
from pdf2image import convert_from_path
import pytesseract
from tqdm import tqdm  # Import tqdm untuk progress bar

def pdf_to_images_with_ocr(pdf_path, image_folder, text_folder):
    try:
        images = convert_from_path(pdf_path)
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return  # Skip this PDF if there's an error


    # Menggunakan tqdm untuk progress bar dalam memproses halaman PDF
    for page_number, image in tqdm(enumerate(images), desc=f"Processing {os.path.basename(pdf_path)}", total=len(images)):
        # Tentukan path untuk gambar dan teks
        image_path = os.path.join(image_folder, f"{os.path.basename(pdf_path)[:-4]}_page_{page_number + 1}.png")
        text_file_path = os.path.join(text_folder, f"{os.path.basename(pdf_path)[:-4]}_page_{page_number + 1}.txt")

        # Simpan gambar
        image.save(image_path, 'PNG')
        
        # Lakukan OCR untuk mendapatkan teks dari gambar
        text = pytesseract.image_to_string(image)
        
        # Simpan teks hasil OCR
        with open(text_file_path, 'w') as text_file:
            text_file.write(text)

def process_pdf_folder(pdf_folder, image_folder, text_folder):
    # Membuat folder tujuan jika belum ada
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)

    if not os.path.exists(text_folder):
        os.makedirs(text_folder)

    # Menggunakan tqdm untuk progress bar saat memproses setiap file PDF
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
    for filename in tqdm(pdf_files, desc="Processing PDFs", unit="file"):
        pdf_path = os.path.join(pdf_folder, filename)
        pdf_to_images_with_ocr(pdf_path, image_folder, text_folder)

if __name__ == "__main__":
    pdf_folder = "pdf_files"  # Folder PDF yang akan diproses
    image_folder = "datasets/dataset_images"  # Folder untuk menyimpan gambar
    text_folder = "datasets/dataset_texts"    # Folder untuk menyimpan teks hasil OCR
    
    process_pdf_folder(pdf_folder, image_folder, text_folder)
