from rag.embeddings import get_embedding_model

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def add_documents(collection, text: str):
    model = get_embedding_model()
    chunks = chunk_text(text)

    embeddings = model.encode(chunks).tolist()

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=[f"doc_{i}" for i in range(len(chunks))]
    )


def retrieve_context(collection, query: str, k=3):
    model = get_embedding_model()
    query_embedding = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k
    )

    documents = results["documents"][0]  # list of chunks
    context = "\n\n".join(documents)

    return context, documents

