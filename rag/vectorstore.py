import chromadb
from chromadb.config import Settings

def get_chroma_client():
    return chromadb.Client(
        Settings(
            persist_directory="./chroma_db",
            anonymized_telemetry=False
        )
    )


def create_collection(client, name="askbuddy_docs"):
    return client.get_or_create_collection(name=name)
