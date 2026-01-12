from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Any
from data_pipeline.scrapers import ScrapedArticle
import re


class MedicalTextProcessor:
    """Processes and chunks medical text"""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        print(f"📝 Text processor ready! Chunk size: {chunk_size}, overlap: {chunk_overlap}")
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep medical terms
        text = re.sub(r'[^\w\s\.\,\-\(\)\%\/]', '', text)
        return text.strip()
    
    def chunk_document(self, article: ScrapedArticle) -> List[Dict[str, Any]]:
        """Split document into chunks with metadata"""
        # Clean content
        clean_content = self.clean_text(article.content)
        
        # Split into chunks
        chunks = self.text_splitter.split_text(clean_content)
        
        # Create chunk documents
        chunked_docs = []
        for idx, chunk in enumerate(chunks):
            chunk_data = {
                'id': f"{hash(article.url)}_{idx}",
                'text': chunk,
                'metadata': {
                    'source_url': article.url,
                    'title': article.title,
                    'category': article.category,
                    'chunk_index': idx,
                    'total_chunks': len(chunks)
                }
            }
            chunked_docs.append(chunk_data)
        
        print(f"   ✂️  Created {len(chunks)} chunks from '{article.title}'")
        return chunked_docs