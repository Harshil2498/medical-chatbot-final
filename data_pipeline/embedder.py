from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any


class DocumentEmbedder:
    """Generates embeddings for document chunks"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        print(f"🧮 Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print(f"   ✅ Model loaded! Dimension: {self.model.get_sentence_embedding_dimension()}")
    
    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add embeddings to chunks"""
        texts = [chunk['text'] for chunk in chunks]
        
        print(f"🔢 Generating embeddings for {len(texts)} chunks...")
        embeddings = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            normalize_embeddings=True
        )
        
        # Add embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk['embedding'] = embedding.tolist()
        
        print("   ✅ Embeddings generated!")
        return chunks