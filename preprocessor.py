
import sys

import os
import json

from tqdm import tqdm
from pypdf import PdfReader

from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import JSONLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

import re

class Preprocessor():
    def __init__(self) -> None:
        self.raw_data_dir = "texts"  # Folder teks
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/multi-qa-mpnet-base-dot-v1",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': False}
        )
        self.database_save_dir = "datasets/json_datasets/database_{db_name}"

    def clean_text(self, text):
        """
        Membersihkan teks dari noise berdasarkan pola yang diberikan.
        """

        # Noise 1: Kata tidak relevan
        irrelevant_words = [
            r'\bMenimbang\b', r'\bAs\b', r'\bMengingat\b', r'\bMenetapkan\b', r'\bMEMUTUSKAN\b',
            r'\bLoy\b', r'\bKf\b', r'\b"fh\b', r'\bvf\b', r'\bAX hy\b', r'\bPlt\.\b', r'\bu\.b\.\b',
            r'\bf\b', r'\bG\b', r'\bttd\.\b'
        ]
        for pattern in irrelevant_words:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        # Noise 2: Simbol
        text = re.sub(r'[�_\-]', '', text)

        # Noise 3: Nomor Halaman
        text = re.sub(r'-\d+-', '', text)

        # Noise 4: Tabel
        text = re.sub(r'\d+\.\s?\|?.*?(\n|\|)', '', text)

        # Noise 5: Tanda Tangan (TTD)
        text = re.sub(
            r'Diundangkan.*?DIREKTUR JENDERAL.*?BERITA NEGARA.*?NOMOR.*?(\n|$)',
            '',
            text,
            flags=re.DOTALL | re.IGNORECASE
        )

        # Menghapus spasi berlebih
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def load_data(self):
        list_file_raw = os.listdir(self.raw_data_dir)
        for fl_raw in tqdm(list_file_raw, desc="txt to json"):
            # Memproses hanya file teks
            if not fl_raw.endswith('.txt'):
                continue
            
            fl_dir = f"{self.raw_data_dir}/{fl_raw}"

            # Membaca isi file teks
            with open(fl_dir, 'r', encoding='utf-8', errors='ignore') as txt_file:
                page_contents = txt_file.read()

            # Bersihkan teks menggunakan clean_text
            cleaned_text = self.clean_text(page_contents)

            # Menyimpan data hanya jika teks tidak kosong
            datasets = []
            if cleaned_text.strip():
                datasets.append({
                    "file": fl_raw,
                    "contents": cleaned_text
                })

            # Simpan ke file JSON
            json_file_name = f"datasets/json_datasets/{fl_raw.lower().replace('-', '_')}.json"
            with open(json_file_name, "w", encoding='utf-8') as json_w:
                json.dump(datasets, json_w, indent=4)

    def load_data_json_lib(self, source):
        """
        Memuat data JSON menggunakan JSONLoader dan memisahkannya menjadi chunk.
        """
        loader = JSONLoader(
            file_path=source,
            jq_schema='.[]',
            text_content=False,
            json_lines=False,
            content_key="contents"
        )

        data = loader.load()
        text_splitter = CharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=0
        )
        data = text_splitter.split_documents(data)
        return data

    def create_faiss_db(self, source, db_name):
        """
        Membuat FAISS database dari data JSON yang telah diproses.
        """
        data = self.load_data_json_lib(source=source)

        db = FAISS.from_documents(data, self.embeddings)

        db.save_local(self.database_save_dir.format(
            db_name=db_name
        ))

    def search_db(self, query, db_name):
        """
        Melakukan pencarian di FAISS database berdasarkan query.
        """
        database_provider = FAISS.load_local(
            self.database_save_dir.format(db_name=db_name),
            self.embeddings,
            allow_dangerous_deserialization=True
        )

        search_results = database_provider.similarity_search(query, k=10, fetch_k=20)
        print(search_results[0])


if __name__ == '__main__':
    prep = Preprocessor()
    prep.load_data()  # Proses file teks menjadi JSON

    # Contoh membuat FAISS database
    # prep.create_faiss_db(
    #     source="datasets/pp_no_76_thn_2020_ttg_tarif_pnbp_polri.pdf.json",
    #     db_name="pp_no_76"
    # )

    # Contoh pencarian di FAISS database
    # prep.search_db(query="apa pengelompokan wilayah pendidikan", db_name="pp_no_76")
