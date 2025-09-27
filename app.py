import argparse
from providers.chatgpt import ChatGPTProvider
from providers.deepseek import DeepSeekProvider
from rag.retrieve import Retriever
from rag.pipeline import rag_pipeline
from dotenv import load_dotenv

load_dotenv()

def get_provider(name: str):
    if name == "chatgpt":
        return ChatGPTProvider()
    elif name == "deepseek":
        return DeepSeekProvider()
    else:
        raise ValueError(f"Proveedor no soportado: {name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", type=str, default="chatgpt")
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--mode", type=str, default="rag")
    parser.add_argument("query", type=str, help="Pregunta a responder")
    args = parser.parse_args()

    provider = get_provider(args.provider)
    retriever = Retriever("data/index.faiss", "data/processed/chunks.parquet")

    if args.mode == "rag":
        answer = rag_pipeline(args.query, provider, retriever, k=args.k)
    else:
        answer = provider.chat([
            {"role": "system", "content": "Eres un asistente útil."},
            {"role": "user", "content": args.query}
        ])

    print(f"\n[{provider.name}] → {answer}")
