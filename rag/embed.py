import os
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer

def main():
    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    data_dir = "data"
    parquet_path = os.path.join(data_dir, "processed", "chunks.parquet")
    index_path = os.path.join(data_dir, "index.faiss")

    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"No se encontró {parquet_path}. Ejecuta primero ingest.py")

    print(f"Cargando {parquet_path} ...")
    try:
        df = pd.read_parquet(parquet_path)
    except FileNotFoundError:
        raise RuntimeError(f"[ERROR] No se encontró {parquet_path}. Ejecuta primero ingest.py")
    except Exception as e:
        raise RuntimeError(f"[ERROR] Error leyendo {parquet_path}: {e}")

    if df.empty:
        raise ValueError("[ERROR] El DataFrame de chunks está vacío.")


    if "text" not in df.columns:
        raise ValueError("El archivo parquet debe contener la columna 'text'.")

    texts = df["text"].tolist()

    # Modelo de embeddings
    
    try:
        model = SentenceTransformer(MODEL_NAME)
    except Exception as e:
        raise RuntimeError(f"[ERROR] No se pudo cargar el modelo {MODEL_NAME}: {e}")

    # Generar embeddings
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    # Normalización para IndexFlatIP (cosine similarity)
    normalize = True
    if normalize:
        faiss.normalize_L2(embeddings)

    # Crear índice FAISS
    dim = embeddings.shape[1]
    print(f"Dimensión de los embeddings: {dim}")

    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    # Guardar índice FAISS
    faiss.write_index(index, index_path)

    # Guardar también el parquet con los textos originales (ya estaba en processed)
    df.to_parquet(parquet_path, index=False)

if __name__ == "__main__":
    main()