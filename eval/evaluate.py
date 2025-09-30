import os
import time
import json
import pandas as pd
from pathlib import Path
from sentence_transformers import SentenceTransformer, util

from rag.retrieve import Retriever
from providers.chatgpt import ChatGPTProvider
from providers.deepseek import DeepSeekProvider
from dotenv import load_dotenv

load_dotenv()

# Tarifas públicas aproximadas (USD por 1M tokens)
PRICES = {
    "chatgpt": {"input": 0.50, "output": 1.50},
    "deepseek": {"input": 0.27, "output": 1.10}
}

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


def estimate_cost(response, provider_name: str):
    """Calcula costo basado en tokens si la respuesta lo incluye."""
    try:
        usage = response.usage
        in_cost = (usage.prompt_tokens / 1e6) * PRICES[provider_name]["input"]
        out_cost = (usage.completion_tokens / 1e6) * PRICES[provider_name]["output"]
        return in_cost + out_cost
    except Exception:
        return None


def evaluate(provider, retriever, gold_set, k=3):
    model = SentenceTransformer(MODEL_NAME)
    results = []

    for item in gold_set:
        qid = item["id"]
        question = item["question"]
        gold_answer = item.get("answer", "")
        gold_refs = item.get("refs", [])

        #  Medir tiempo de recuperación
        t0 = time.perf_counter()
        retrieved = retriever.search(question, top_k=k)
        t1 = time.perf_counter()

        # Construir contexto (concatenar chunks recuperados)
        context = "\n".join(r["text"] for r in retrieved)

        # Medir tiempo del modelo
        messages = [
            {"role": "system", "content": "Eres un asistente útil."},
            {"role": "user", "content": f"Pregunta: {question}\n\nContexto:\n{context}"}
        ]

        t2 = time.perf_counter()
        response = provider.client.chat.completions.create(
            model=provider.model,
            messages=messages,
            temperature=0
        )
        t3 = time.perf_counter()

        pred_answer = response.choices[0].message.content or ""

        # Latencias
        latency_retrieve = t1 - t0
        latency_llm = t3 - t2
        latency_total = t3 - t0

        # Métricas
        em = exact_match(pred_answer, gold_answer) if gold_answer else 0
        sim = cosine_sim(pred_answer, gold_answer, model) if gold_answer else 0.0
        cost = estimate_cost(response, provider.name)

        results.append({
            "id": qid,
            "question": question,
            "pred": pred_answer,
            "gold": gold_answer,
            "em": em,
            "sim": sim,
            "latency_total": latency_total,
            "latency_retrieve": latency_retrieve,
            "latency_llm": latency_llm,
            "cost_usd": cost,
            "refs": gold_refs
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
        Path("eval").mkdir(exist_ok=True)
        df.to_csv(out_path, index=False)
        print(f"[OK] Resultados guardados en {out_path}")
