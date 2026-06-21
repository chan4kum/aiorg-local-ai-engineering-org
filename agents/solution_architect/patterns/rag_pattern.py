RAG_ARCHITECTURE_PATTERN = {
    "name": "Retrieval-Augmented Generation (RAG)",
    "components": [
        "Vector Database (e.g., Qdrant, Pinecone)",
        "Embedding Model",
        "LLM Inference Engine",
        "Document Parser/Chunker",
        "Orchestrator (e.g., LangChain, LlamaIndex)"
    ],
    "description": "Standard pattern for injecting external knowledge into LLM prompts."
}
