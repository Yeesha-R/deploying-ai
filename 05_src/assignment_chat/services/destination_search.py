from pathlib import Path
from typing import Any

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction


BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_PATH = BASE_DIR / "chroma_db"
COLLECTION_NAME = "travel_destinations"


class DestinationSearchService:
    """Searches for destinations using semantic similarity."""

    def __init__(self) -> None:
        self.client = chromadb.PersistentClient(path=str(CHROMA_PATH))
        self.collection = self.client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=DefaultEmbeddingFunction(),
        )

    def search(self, query: str, number_of_results: int = 3) -> list[dict[str, Any]]:
        if not query.strip():
            return []

        result = self.collection.query(
            query_texts=[query],
            n_results=number_of_results,
            include=["documents", "metadatas", "distances"],
        )

        matches = []

        for document, metadata, distance in zip(
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        ):
            matches.append(
                {
                    "destination": metadata["destination"],
                    "country": metadata["country"],
                    "best_season": metadata["best_season"],
                    "budget_level": metadata["budget_level"],
                    "activities": metadata["activities"],
                    "description": document,
                    "distance": distance,
                }
            )

        return matches

    def format_response(self, query: str, matches: list[dict[str, Any]]) -> str:
        """Turn database results into a natural-language response."""
        if not matches:
            return "I could not find a suitable destination for that request."

        lines = [f"Based on your interest in “{query},” here are my suggestions:"]

        for position, match in enumerate(matches, start=1):
            activities = match["activities"].replace(";", ",")
            lines.append(
                f"\n{position}. {match['destination']}, {match['country']} — "
                f"This is a {match['budget_level']}-budget destination. "
                f"Popular activities include {activities}. "
                f"The recommended travel period is {match['best_season']}."
            )

        return "".join(lines)


def main() -> None:
    service = DestinationSearchService()

    print("Atlas Destination Search")
    print("Enter 'quit' to stop.\n")

    while True:
        query = input("What kind of trip are you looking for? ").strip()

        if query.lower() == "quit":
            break

        matches = service.search(query)
        print(service.format_response(query, matches))
        print()


if __name__ == "__main__":
    main()