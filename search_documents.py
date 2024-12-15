from db_connector import DatabaseConnector
from search_engine import SearchEngine, SearchResult
from tqdm import tqdm  # Fortschrittsbalken

def print_result(result: SearchResult, rank: int) -> None:
    """Print a single search result."""
    print(f"\n{rank}. {result.file_path}")  # Verwenden Sie direkte Attribute
    print(f"Module: {result.module or 'N/A'}")
    print(f"Topic: {result.topic or 'N/A'}")
    print(f"Relevance Score: {result.relevance_score:.2f}")
    print("-" * 80)

def load_documents_into_search_engine(db: DatabaseConnector, search_engine: SearchEngine):
    """Load all documents from the database into the search engine."""
    print("Loading search index...")
    rows = db.fetch_all_content()

    for row in tqdm(rows, desc="Indexing Documents", unit="doc"):
        file_path, content, file_type, module, topic, subtopic, chapter, instructor, page_number = row[1:10]

        # Create document with metadata
        doc = {
            'file_path': file_path,
            'content': content,
            'file_type': file_type,
            'module': module if module else None,
            'topic': topic if topic else None,
            'subtopic': subtopic if subtopic else None,
            'chapter': chapter if chapter else None,
            'instructor': instructor if instructor else None,
            'page_number': page_number
        }

        # Add document to search engine
        search_engine.add_document(doc)
    print("\nSearch index loaded successfully!")

def interactive_search(search_engine: SearchEngine):
    """Interactive search interface."""
    print("\nSearch system ready! Enter search queries (Ctrl+C to exit)")
    print("Available fields: module, topic, subtopic, chapter, instructor, content")

    while True:
        try:
            query = input("\nEnter search query: ").strip()
            if not query:
                continue

            field = input("Enter field to search (press Enter for full text): ").strip() or None

            print("\nSearching...")
            results = search_engine.search_with_progress(query, field)
            print(f"\nFound {len(results)} results:")

            for i, result in enumerate(results[:5], 1):
                print_result(result, i)

        except KeyboardInterrupt:
            print("\nExiting search system...")
            break
        except Exception as e:
            print(f"Error during search: {str(e)}")
            continue

def main():
    """Main function for the search system."""
    db = DatabaseConnector()
    search_engine = SearchEngine()

    try:
        # Load documents into the search engine
        load_documents_into_search_engine(db, search_engine)

        # Start interactive search
        interactive_search(search_engine)
    finally:
        db.close()

if __name__ == "__main__":
    main()
