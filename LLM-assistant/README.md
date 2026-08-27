# Personal LLM Assistant

A personal assistant built on retrieval-augmented generation (RAG), with its
own memory.

## Concept

- A personal LLM-backed assistant — this account's own version of "an
  assistant that remembers things about you," built from scratch as a
  learning project rather than relying on an existing product.
- Confirmed to be **RAG-based**: rather than fine-tuning a model, it retrieves
  relevant stored information and feeds it into the prompt at query time.

## Suggested tech stack

- **Language:** Python
- **LLM access:** Anthropic API (`anthropic` Python SDK) for the actual
  completions
- **Embeddings/retrieval:** a lightweight vector store to start —
  `chromadb` or even a flat file + `numpy` cosine similarity for a v1
- **Memory storage:** SQLite or flat JSON files for structured facts,
  vector store for semantic/document recall
- **Interface:** start as a CLI, same pattern as the disc golf tracker —
  fastest way to get something usable before investing in a web UI

## Suggested starting scope

1. **Ingest** — a way to add documents/notes/facts into the store
   (chunk + embed + save).
2. **Retrieve** — given a query, pull the most relevant chunks.
3. **Generate** — pass retrieved context + query to the Claude API, return
   the answer.
4. **Memory** — a separate, smaller store for durable facts (name,
   preferences, ongoing projects) that always gets included, independent of
   retrieval relevance — this is what makes it feel like it "remembers you"
   rather than just searching documents.

## Getting started

```bash
pip install anthropic chromadb
```

```python
# skeleton sketch
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

def ask(query, context_chunks):
    context = "\n\n".join(context_chunks)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {query}"
        }]
    )
    return response.content[0].text
```

## Open questions to resolve when picking this back up

- What's the primary use case — general Q&A over personal notes, or
  something narrower (e.g. just tracking project status)?
- Local-only, or does it need to run somewhere accessible from multiple
  devices?
- How much of the "memory" layer should be structured (explicit facts) vs.
  freeform (just embed everything and retrieve)?
