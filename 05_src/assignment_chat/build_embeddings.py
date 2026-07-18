from pathlib import Path

import chromadb
import pandas as pd
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from chromadb.errors import NotFoundError


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "destinations.csv"
CHROMA_PATH = BASE_DIR / "chroma_db"
COLLECTION_NAME = "travel_destinations"


def create_document(row: pd.Series) -> str:
    """Combine destination fields into one searchable document."""
    return (
        f"{row['destination']} is located in {row['country']}. "
        f"{row['description']} "
        f"Popular activities include {row['activities']}. "
        f"The best season is {row['best_season']}. "
        f"It has a {row['budget_level']} budget level and is suitable for "
        f"{row['travel_style']} travel."
    )


def build_database() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    destinations = pd.read_csv(DATA_PATH).fillna("")

    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    embedding_function = DefaultEmbeddingFunction()

    # Delete the old collection to avoid duplicates.
    try:
        client.delete_collection(COLLECTION_NAME)
    except NotFoundError:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
        metadata={"description": "Travel destination recommendations"},
    )

    documents = []
    metadata = []
    ids = []

    for index, row in destinations.iterrows():
        documents.append(create_document(row))
        metadata.append(
            {
                "destination": str(row["destination"]),
                "country": str(row["country"]),
                "activities": str(row["activities"]),
                "best_season": str(row["best_season"]),
                "budget_level": str(row["budget_level"]),
                "travel_style": str(row["travel_style"]),
            }
        )
        ids.append(f"destination-{index}")

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadata,
    )

    print(f"Stored {collection.count()} destinations in ChromaDB.")
    print(f"Database location: {CHROMA_PATH}")


if __name__ == "__main__":
    build_database()