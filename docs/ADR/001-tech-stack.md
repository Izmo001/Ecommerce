# ADR 001: Local-first AI Stack

## Context
We are building an e-commerce AI assistant as a learning project. We want zero cloud costs, fast iteration, and a migration path to enterprise infrastructure later.

## Decision
- Use **Ollama** for local LLM hosting (embeddings + chat).
- Use **Postgres + pgvector** for vector storage instead of a dedicated vector DB (like Pinecone).
- Use **Docker Compose** to orchestrate the local environment.

## Consequences
- **Positive:** Zero cost, complete data privacy, easy debugging, and the `LLMClient` adapter pattern makes migrating to Azure OpenAI trivial later.
- **Negative:** Local hardware limits model size (capped at ~8B parameters for acceptable latency). Requires local GPU/Apple Silicon for fast responses.