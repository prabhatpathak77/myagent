#!/usr/bin/env python3
"""
Setup script to load all documents into RAG database
Run this once to initialize the RAG system with your data
"""

from subagents.rag_agent import RAGAgent
from rag_loader import DocumentLoader
import os

def setup_rag():
    print("=" * 60)
    print("Setting up RAG Database")
    print("=" * 60)
    
    # Initialize RAG agent and loader
    rag_agent = RAGAgent()
    loader = DocumentLoader()
    
    # Load documents from different folders
    folders = {
        'projects': 'rag_data/projects',
        'certifications': 'rag_data/certifications',
        'resumes': 'rag_data/resumes',
        'blog_posts': 'rag_data/blog_posts'
    }
    
    total_docs = 0
    
    for category, folder_path in folders.items():
        if not os.path.exists(folder_path):
            print(f"⚠ Folder not found: {folder_path}")
            continue
        
        print(f"\n📁 Loading {category}...")
        
        # Load PDFs
        pdf_docs = loader.load_pdfs(folder_path)
        for doc in pdf_docs:
            doc['metadata']['category'] = category
            rag_agent.add_document(doc['text'], doc['metadata'])
            print(f"  ✓ Added PDF: {doc['metadata']['source']}")
            total_docs += 1
        
        # Load Markdown files
        md_docs = loader.load_markdown(folder_path)
        for doc in md_docs:
            doc['metadata']['category'] = category
            rag_agent.add_document(doc['text'], doc['metadata'])
            print(f"  ✓ Added Markdown: {doc['metadata']['source']}")
            total_docs += 1
    
    print("\n" + "=" * 60)
    print(f"✓ RAG Database Setup Complete!")
    print(f"✓ Total documents loaded: {total_docs}")
    print("=" * 60)
    
    # Test query
    print("\n🔍 Testing RAG query...")
    results = rag_agent.query("projects and experience", n_results=2)
    if results:
        print(f"✓ Query successful! Found {len(results)} results")
        print(f"  Sample: {results[0][:100]}...")
    else:
        print("⚠ No results found")

if __name__ == "__main__":
    setup_rag()
