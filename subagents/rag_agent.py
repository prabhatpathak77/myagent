import chromadb
from sentence_transformers import SentenceTransformer

class RAGAgent:
    def __init__(self):
        # Use sentence-transformers for local embeddings (no API quota limits)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.client = chromadb.PersistentClient(path="./rag_db")
        self.collection = self.client.get_or_create_collection("resume_kb")
    
    def add_document(self, text, metadata):
        """Add document to RAG"""
        embedding = self._embed(text)
        self.collection.add(
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata],
            ids=[metadata['id']]
        )
    
    def query(self, query_text, n_results=3):
        """Query RAG for relevant info"""
        query_embedding = self._embed(query_text)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results['documents'][0] if results['documents'] else []
    
    def _embed(self, text):
        """Generate embedding using sentence-transformers (local, no API calls)"""
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()