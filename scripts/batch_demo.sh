#!/bin/bash
set -e  # Detener en caso de error

# === CONFIGURACIÓN ===
PROJECT_DIR="$(pwd)"
VENV_DIR="$PROJECT_DIR/venv"
PYTHON_BIN="python3"

echo "[INFO] Iniciando pipeline RAG..."

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
    pip install pypdf pdfminer.six sentence-transformers faiss-cpu openai python-dotenv pandas
fi

# === INGESTA DE DOCUMENTOS ===
echo "[INFO] Ejecutando ingesta de documentos..."
mkdir -p data/processed
python -m rag.ingest

# === EMBEDDINGS Y FAISS ===
echo "[INFO] Generando embeddings e índice FAISS..."
python -m rag.embed

# === EVALUACIÓN ===
echo "[INFO] Ejecutando evaluación con gold_set..."
python eval/evaluate.py

# === OPCIONAL: EJEMPLO DE CONSULTA ===
echo "[INFO] Ejecutando ejemplo de consulta al chatbot..."
echo "[INFO] Pregunta: ¿Cuál es el procedimiento para solicitar la suspensión temporal de estudios?"
python app.py --provider chatgpt --k 3 "¿Cuál es el procedimiento para solicitar la suspensión temporal de estudios?"

echo "[OK] Pipeline RAG completado correctamente."
