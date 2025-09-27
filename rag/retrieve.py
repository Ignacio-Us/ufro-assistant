import faiss
import numpy as np
import pandas as pd
from pathlib import Path
from sentence_transformers import SentenceTransformer
from typing import List, Dict


class Retriever:
    def __init__(self, index_path: str, chunks_path: str,
                 model_name: str = "all-MiniLM-L6-v2"):
        
        if not Path(index_path).exists():
            raise FileNotFoundError(f"[ERROR] No se encontró el índice FAISS en {index_path}")
        else:
            self.index = faiss.read_index(index_path)
        
        self.df = pd.read_parquet(chunks_path)
        
        self.model = SentenceTransformer(model_name)

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Busca los top_k chunks más relevantes para la query"""
        query_vec = self.model.encode([query])
        query_vec = np.array(query_vec).astype("float32")

        distances, indices = self.index.search(query_vec, top_k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1:
                continue
            row = self.df.iloc[idx].to_dict()
            row["score"] = float(distances[0][i])
            results.append(row)
        return results