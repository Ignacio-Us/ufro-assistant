import json
import pandas as pd
from pathlib import Path
from sentence_transformers import SentenceTransformer, util
from providers.chatgpt import ChatGPTProvider
from providers.deepseek import DeepSeekProvider
from rag.retrieve import Retriever
from rag.pipeline import rag_pipeline
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "all-MiniLM-L6-v2"

def load_gold(path="eval/gold_set.jsonl"):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def exact_match(pred: str, gold: str) -> int:
    return int(pred.strip().lower() == gold.strip().lower())

def cosine_sim(pred: str, gold: str, model) -> float:
    emb_pred = model.encode(pred, convert_to_tensor=True)
    emb_gold = model.encode(gold, convert_to_tensor=True)
    return float(util.pytorch_cos_sim(emb_pred, emb_gold).item())

def evaluate(provider, retriever, gold_set, k=3):
    model = SentenceTransformer(MODEL_NAME)
    results = []

    for item in gold_set:
        qid = item["id"]
        question = item["question"]
        gold_answer = item.get("answer", "")
        gold_refs = item.get("refs", [])

        # Ejecutar RAG
        pred_answer = rag_pipeline(question, provider, retriever, k=k)

        # Métricas
        em = exact_match(pred_answer, gold_answer) if gold_answer else 0
        sim = cosine_sim(pred_answer, gold_answer, model) if gold_answer else 0.0

        # TODO: check citas y prec@k → necesitas parsear retriever.retrieve()

        results.append({
            "id": qid,
            "question": question,
            "pred": pred_answer,
            "gold": gold_answer,
            "em": em,
            "sim": sim,
        })

    return pd.DataFrame(results)

if __name__ == "__main__":
    retriever = Retriever("data/index.faiss", "data/processed/chunks.parquet")

    gold_set = load_gold()

    for provider_cls in [ChatGPTProvider, DeepSeekProvider]:
        provider = provider_cls()
        print(f"=== Evaluando con {provider.name} ===")
        df = evaluate(provider, retriever, gold_set, k=3)
        out_path = f"eval/results_{provider.name}.csv"
        df.to_csv(out_path, index=False)
        print(f"[OK] Resultados guardados en {out_path}")
