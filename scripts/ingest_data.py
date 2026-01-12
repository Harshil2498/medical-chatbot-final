import sys
sys.path.insert(0, '.')

from data_pipeline.scrapers import MedicalWebScraper
from data_pipeline.text_processor import MedicalTextProcessor
from data_pipeline.embedder import DocumentEmbedder
from app.services.vector_db_service import VectorDBService
from app.config import get_settings


def ingest_medical_knowledge():
    """Main ingestion pipeline"""
    print("\n" + "="*70)
    print("🏥 MEDICAL KNOWLEDGE INGESTION PIPELINE")
    print("="*70 + "\n")
    
    # Load settings
    settings = get_settings()
    
    # Initialize components
    print("📦 Step 1: Initializing components...")
    scraper = MedicalWebScraper()
    processor = MedicalTextProcessor(
        chunk_size=settings.RAG_CHUNK_SIZE,
        chunk_overlap=settings.RAG_CHUNK_OVERLAP
    )
    embedder = DocumentEmbedder(model_name=settings.EMBEDDING_MODEL_NAME)
    vector_db = VectorDBService(
        persist_dir=settings.CHROMA_PERSIST_DIR,
        collection_name=settings.CHROMA_COLLECTION_NAME
    )
    
    # URLs to scrape
    print("\n🌐 Step 2: Scraping medical articles...")
    urls = [
        "https://medlineplus.gov/diabetestype2.html",
        "https://medlineplus.gov/highbloodpressure.html",
        "https://medlineplus.gov/heartdiseases.html",
        "https://medlineplus.gov/depression.html",
        "https://medlineplus.gov/anxiety.html",
        "https://medlineplus.gov/asthma.html",
        "https://medlineplus.gov/obesity.html",
        "https://medlineplus.gov/stroke.html",
        "https://medlineplus.gov/cholesterol.html",
        "https://medlineplus.gov/arthritis.html",
    ]
    
    articles = scraper.scrape_batch(urls)
    
    if not articles:
        print("❌ No articles scraped! Check your internet connection.")
        return
    
    # Process and chunk
    print("\n✂️  Step 3: Chunking documents...")
    all_chunks = []
    for article in articles:
        chunks = processor.chunk_document(article)
        all_chunks.extend(chunks)
    
    print(f"\n✅ Generated {len(all_chunks)} total chunks from {len(articles)} articles")
    
    # Generate embeddings
    print("\n🔢 Step 4: Generating embeddings...")
    embedded_chunks = embedder.embed_chunks(all_chunks)
    
    # Store in vector database
    print("\n💾 Step 5: Storing in vector database...")
    vector_db.add_documents(
        documents=[c['text'] for c in embedded_chunks],
        embeddings=[c['embedding'] for c in embedded_chunks],
        metadatas=[c['metadata'] for c in embedded_chunks],
        ids=[c['id'] for c in embedded_chunks]
    )
    
    # Final summary
    total_docs = vector_db.get_collection_count()
    print("\n" + "="*70)
    print("✅ INGESTION COMPLETE!")
    print(f"   📊 Total documents in database: {total_docs}")
    print(f"   📝 Articles scraped: {len(articles)}")
    print(f"   ✂️  Chunks created: {len(all_chunks)}")
    print("="*70 + "\n")


if __name__ == "__main__":
    ingest_medical_knowledge()