"""Search the existing A8 activity corpus with a local sentence encoder."""

import csv
from functools import lru_cache
from pathlib import Path

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
EMBEDDING_REVISION = "5c38ec7c405ec4b44b94cc5a9bb96e735b38267a"
CHUNKS_FILE = Path(__file__).resolve().parents[1] / "llm-test" / "chunks_all.csv"
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "
MIN_SIMILARITY = 0.60
TOP_K = 3


def _encode(tokenizer, model, texts):
    import torch

    tokens = tokenizer(texts, padding=True, truncation=True, max_length=512, return_tensors="pt")
    with torch.inference_mode():
        embeddings = model(**tokens).last_hidden_state[:, 0]
        return torch.nn.functional.normalize(embeddings, dim=1)


@lru_cache(maxsize=1)
def _load_index():
    import torch
    from transformers import AutoModel, AutoTokenizer

    with CHUNKS_FILE.open(encoding="utf-8-sig", newline="") as source:
        chunks = tuple(
            row for row in csv.DictReader(source)
            if row["strategy"] == "hybrid" and row["text"].strip()
        )
    if not chunks:
        raise ValueError("The A8 activity corpus has no hybrid chunks.")

    tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL, revision=EMBEDDING_REVISION)
    model = AutoModel.from_pretrained(
        EMBEDDING_MODEL, revision=EMBEDDING_REVISION, use_safetensors=True,
    ).eval()
    batches = [
        _encode(tokenizer, model, [row["text"] for row in chunks[start:start + 16]])
        for start in range(0, len(chunks), 16)
    ]
    return tokenizer, model, chunks, torch.cat(batches)


def retrieve_activity_context(query):
    tokenizer, model, chunks, embeddings = _load_index()
    query_vector = _encode(tokenizer, model, [QUERY_PREFIX + query])[0]
    scores = (embeddings @ query_vector).tolist()
    ranked = sorted(range(len(chunks)), key=scores.__getitem__, reverse=True)
    return [
        {**chunks[index], "topic_label": chunks[index]["topic"].replace("_", " ").capitalize()}
        for index in ranked[:TOP_K]
        if scores[index] >= MIN_SIMILARITY
    ]
