import re
import pypdf
from pathlib import Path
import pandas as pd

def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    try:
        reader = pypdf.PdfReader(pdf_path)
    except Exception as e:
        print(f"[ERROR] No se pudo leer {pdf_path}: {e}")
        return []

    pages = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
            text = clean_text(text)
        except Exception as e:
            print(f"[WARN] Error procesando página {i} en {pdf_path}: {e}")
            text = ""
        pages.append({
            "doc_id": Path(pdf_path).stem,
            "title": Path(pdf_path).name,
            "page": i,
            "text": text
        })
    return pages


def extract_text_from_txt(txt_path: str) -> list[dict]:
    with open(txt_path, "r", encoding="utf-8") as f:
        text = clean_text(f.read())
    return [{
        "doc_id": Path(txt_path).stem,
        "title": Path(txt_path).name,
        "page": 1,
        "text": text
    }]

def clean_text(text: str) -> str:
    text = re.sub(r"Página \d+ de \d+", "", text)
    text = re.sub(r"\n+", "\n", text)
    return text.strip()

def chunk_text(text: str, doc_id: str, title: str, page: int,
               chunk_size=450, overlap=50) -> list[dict]:
    # chunk_size ~ tokens, aproximado usando palabras
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)
        chunks.append({
            "doc_id": doc_id,
            "title": title,
            "page": page,
            "chunk_id": f"{doc_id}_{page}_{start}",
            "text": chunk_text
        })
        start += chunk_size - overlap
    return chunks

def ingest_documents(raw_dir="data/raw", output="data/processed/chunks.parquet"):
    all_chunks = []
    for file in Path(raw_dir).glob("*"):
        if file.suffix.lower() == ".pdf":
            pages = extract_text_from_pdf(file)
        elif file.suffix.lower() == ".txt":
            pages = extract_text_from_txt(file)
        else:
            continue
        
        for page in pages:
            chunks = chunk_text(page["text"], page["doc_id"], page["title"], page["page"])
            all_chunks.extend(chunks)
    
    df = pd.DataFrame(all_chunks)
    df.to_parquet(output, index=False)
    print(f"[OK] Guardados {len(df)} chunks en {output}")

if __name__ == "__main__":
    ingest_documents()