# web_app.py
from flask import Flask, render_template, request
from providers.chatgpt import ChatGPTProvider
from providers.deepseek import DeepSeekProvider
from rag.retrieve import Retriever
from rag.pipeline import rag_pipeline
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# --- Inicialización de componentes ---
# Se asume que el índice ya está creado en data/index.faiss
retriever = Retriever("data/index.faiss", "data/processed/chunks.parquet")

# Mapeo de proveedores disponibles
PROVIDERS = {
    "chatgpt": ChatGPTProvider(),
    "deepseek": DeepSeekProvider()
}

@app.route("/", methods=["GET", "POST"])
def index():
    answer, query, provider_name, k = None, "", "chatgpt", 5
    
    if request.method == "POST":
        query = request.form.get("query")
        provider_name = request.form.get("provider", "chatgpt")
        k = int(request.form.get("k", 5))
        
        provider = PROVIDERS[provider_name]
        answer = rag_pipeline(query, provider, retriever, k=k)

    return render_template(
        "index.html",
        answer=answer,
        query=query,
        provider_name=provider_name,
        k=k,
        providers=list(PROVIDERS.keys())
    )

if __name__ == "__main__":
    app.run(debug=True, port=5813)
