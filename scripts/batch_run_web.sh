#!/bin/bash
set -e  # Detener en caso de error

# === CONFIGURACIÓN ===
PROJECT_DIR="$(pwd)"
VENV_DIR="$PROJECT_DIR/venv"
PYTHON_BIN="python3"

echo "[INFO] Iniciando Web GUI del RAG..."

# === CREAR VENV SI NO EXISTE ===
if [ ! -d "$VENV_DIR" ]; then
    echo "[INFO] Creando entorno virtual en $VENV_DIR..."
    $PYTHON_BIN -m venv "$VENV_DIR"
fi

# === ACTIVAR VENV ===
echo "[INFO] Activando entorno virtual..."
source "$VENV_DIR/bin/activate"

# === INSTALAR DEPENDENCIAS ===
if [ -f "requirements.txt" ]; then
    echo "[INFO] Instalando dependencias..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "[WARN] No se encontró requirements.txt, instalando dependencias mínimas..."
    pip install flask sentence-transformers faiss-cpu openai python-dotenv pandas
fi

# === VERIFICAR ARCHIVOS DE RAG ===
if [ ! -f "data/index.faiss" ] || [ ! -f "data/processed/chunks.parquet" ]; then
    echo "[ERROR] No se encontraron los datos procesados. Ejecuta primero el pipeline (ingest + embed)."
    exit 1

else
    # === INGESTA DE DOCUMENTOS ===
    echo "[INFO] Ejecutando ingesta de documentos..."
    mkdir -p data/processed
    python -m rag.ingest

    # === EMBEDDINGS Y FAISS ===
    echo "[INFO] Generando embeddings e índice FAISS..."
    python -m rag.embed
fi

# === OPCIONAL: EJEMPLO DE CONSULTA ===
echo "[INFO] Comprobando funcionamiento del RAG..."
echo "[INFO] Ejecutando ejemplo de consulta al chatbot..."
echo "[INFO] Pregunta: ¿Cuál es el procedimiento para solicitar la suspensión temporal de estudios?"
python app.py --provider chatgpt --k 3 "¿Cuál es el procedimiento para solicitar la suspensión temporal de estudios?"

echo "[OK] Pipeline RAG completado correctamente."

# === EJECUTAR WEB GUI ===
echo "[INFO] Levantando servidor Flask..."
python -m web.web_app