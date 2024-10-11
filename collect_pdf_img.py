import os
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

def pdf_to_images_with_ocr(pdf_path, output_folder):
  
    images = convert_from_path(pdf_path)
    
    for page_number, image in enumerate(images):
     
        image_path = os.path.join(output_folder, f"{os.path.basename(pdf_path)[:-4]}_page_{page_number + 1}.png")
        image.save(image_path, 'PNG')
   
        text = pytesseract.image_to_string(image)
        text_file_path = os.path.join(output_folder, f"{os.path.basename(pdf_path)[:-4]}_page_{page_number + 1}.txt")
        
        with open(text_file_path, 'w') as text_file:
            text_file.write(text)
        
        print(f"Page {page_number + 1} of {os.path.basename(pdf_path)} converted, saved as {image_path}, and OCR saved as {text_file_path}")

def process_pdf_folder(pdf_folder, output_folder):

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    

    for filename in os.listdir(pdf_folder):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(pdf_folder, filename)
            print(f"Processing {pdf_path}...")
            pdf_to_images_with_ocr(pdf_path, output_folder)

if __name__ == "__main__":
    pdf_folder = "datasets-pdf"
    output_folder = "output-image" 
    
    process_pdf_folder(pdf_folder, output_folder)
