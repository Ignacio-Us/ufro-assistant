# RAG Chatbot

Este proyecto implementa un asistente conversacional RAG (Retrieval-Augmented Generation), que permite responder preguntas usando un conjunto de documentos locales (PDF, TXT) como base de conocimiento.

El flujo del proyecto incluye:

1. Ingesta y chunking de documentos.

2. Generación de embeddings y construcción de un índice vectorial FAISS.

3. Consulta vía chatbot con modelos LLM (ChatGPT, DeepSeek) mediante adaptadores (providers).

4. Evaluación automática con un gold set de preguntas y métricas.

## Requisitos

- Python 3.9+
- Git
- Claves API válidas (OpenRouter / DeepSeek)

## Instalación

1. Clonar el repositorio:

```
git clone https://github.com/Ignacio-Us/ufro-assistant.git
```

```
git switch master
```

```
cd ufro-assistant
```
2. Dar permisos al script de ejecución (de ser posible):

```
chmod 700 scripts/batch_demo.sh
```

3. Configurar variables de entorno (.env):

```
cp .env.example .env
```

Luego se agregan las API KEY con nano, vim u otro editor de texto.

## Ejecución

Ejecutar el pipeline completo (venv -> instalación -> ingesta -> embeddings -> evaluación -> demo):

```
./scripts/batch_demo.sh
```

**O**

```
bash scripts/batch_demo.sh
```
## Consultas manuales

El chatbot se puede ejecutar directamente con parámetros en la línea de comandos:

```
python app.py --provider <PROVEEDOR> --k <N> "Pregunta aquí"
```

| Parámetro       | Descripción                                                                | Valores posibles                                                           |
| --------------- | --------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `--provider`    | Define qué modelo LLM usar.                                                | `chatgpt`, `deepseek`                                                      |
| `--k`           | Número de fragmentos recuperados desde FAISS para enriquecer la respuesta. | Entero (ej: `3`, `5`). Default: `3`                                        |                               |
| `query`         | Pregunta del usuario (último argumento entre comillas).                    | Texto libre                                                                |

## Evaluación

El sistema se evalúa con el archivo eval/gold_set.jsonl, que contiene 20 Q&A de referencia.

Para ejecutar la evaluación:

```
python eval/evaluate.py
```

Esto genera archivos CSV con los resultados de cada proveedor:

`
eval/results_chatgpt.csv
eval/results_deepseek.csv
`

Cada archivo incluye métricas como:

- EM (Exact Match)
- Similitud coseno
- Citas presentes (%)
- Latencia end-to-end y por etapa (retriever / LLM).
- Costo estimado por consulta (tokens × tarifa).