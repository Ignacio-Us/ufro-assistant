import argparse
from providers.chatgpt import ChatGPTProvider
from providers.deepseek import DeepSeekProvider
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
    parser.add_argument("--provider", type=str, default="chatgpt", help="Proveedor a usar (chatgpt o deepseek)")
    args = parser.parse_args()

    provider = get_provider(args.provider)

    messages = [
        {"role": "system", "content": "Eres un asistente útil."},
        {"role": "user", "content": "Explícame qué es RAG en pocas palabras."}
    ]

    print(f"[{provider.name}] →", provider.chat(messages))
