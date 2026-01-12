import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional

class VectorDBService:
    """Manages vector database operations using ChromaDB"""
    
    def __init__(self, persist_dir: str, collection_name: str):
        print(f"📚 Initializing ChromaDB at {persist_dir}...")
        
        # FIX: Using PersistentClient for disk storage (v0.4.x+)
        # This ensures data is saved in your 'data/chroma_db' folder
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        self.collection_name = collection_name
        self.collection = self._get_or_create_collection()
        print(f"✅ ChromaDB ready! Collection: {collection_name}")
    
    def _get_or_create_collection(self):
        """Get existing collection or create new one"""
        # In modern Chroma, get_or_create_collection handles the logic internally
        return self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Medical knowledge base"}
        )
    
    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ):
        """Add documents to the collection and persist them"""
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        # Note: self.client.persist() is no longer needed in v0.4+ 
        # as PersistentClient handles it automatically.
        print(f"✅ Added {len(documents)} documents to vector database")
    
    def similarity_search(
        self,
        query_embedding: List[float],
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=filter_dict if filter_dict else None
        )
        
        # Format results
        formatted_results = []
        if results['ids']:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i]
                })
        
        return formatted_results
    
    def get_collection_count(self) -> int:
        """Get total number of documents"""
        return self.collection.count()
    
    def delete_collection(self):
        """Delete the entire collection"""
        self.client.delete_collection(name=self.collection_name)