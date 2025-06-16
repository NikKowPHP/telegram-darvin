import qdrant_client
from pathlib import Path

# --- Configuration ---
# This script manually sets the config to find the right collection to delete.
# It assumes your project folder name is the same as your current working directory.
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME_PREFIX = "cct"
project_folder_name = Path.cwd().name.lower().replace(" ", "_")
collection_to_delete = f"{COLLECTION_NAME_PREFIX}_{project_folder_name}"

def main():
    """Connects to Qdrant and deletes the specified collection."""
    try:
        client = qdrant_client.QdrantClient(url=QDRANT_URL)
        print(f"Attempting to delete Qdrant collection: '{collection_to_delete}'...")
        
        # This is the command that deletes the collection
        result = client.delete_collection(collection_name=collection_to_delete)
        
        if result:
            print(f"✅ Successfully deleted the collection.")
        else:
            print(f"⚠️ Collection might not have existed or was already deleted.")
            
    except Exception as e:
        # This will handle cases where the collection doesn't exist, which is fine.
        if "not found" in str(e).lower():
             print(f"✅ Collection '{collection_to_delete}' does not exist, which is the desired state. No action needed.")
        else:
            print(f"❌ An unexpected error occurred: {e}")
            print("Please ensure your Qdrant Docker container is running.")

if __name__ == "__main__":
    main()