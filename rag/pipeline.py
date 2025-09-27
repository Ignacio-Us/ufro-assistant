from typing import List, Dict
from providers.base import Provider
from rag.retrieve import Retriever
from rag import prompts

def rewrite_query(query: str, provider: Provider) -> str:
    messages = [
        {"role": "system", "content": prompts.REWRITE_PROMPT},
        {"role": "user", "content": query}
    ]
    return provider.chat(messages)

def retrieve_contexts(query: str, retriever: Retriever, k: int = 5) -> List[Dict]:
    return retriever.search(query, top_k=k)

def synthesize_answer(query: str, contexts: List[Dict], provider: Provider) -> str:
    context_texts = []
    for c in contexts:
        citation = f"[{c['doc_id']}:{c['page']}]"
        context_texts.append(f"{citation} {c['text']}")
    
    messages = [
        {"role": "system", "content": prompts.SYSTEM_PROMPT},
        {"role": "user", "content": query},
        {"role": "assistant", "content": "\n".join(context_texts)}
    ]
    
    return provider.chat(messages)

def postprocess(answer: str) -> str:
    return answer.strip()

def rag_pipeline(query: str, provider: Provider, retriever: Retriever, k: int = 5) -> str:
    refined_query = rewrite_query(query, provider)
    contexts = retrieve_contexts(refined_query, retriever, k=k)
    raw_answer = synthesize_answer(refined_query, contexts, provider)
    return postprocess(raw_answer)
