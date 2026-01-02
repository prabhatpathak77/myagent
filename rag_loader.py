import os
from pypdf import PdfReader

class DocumentLoader:
    def load_pdfs(self, folder_path):
        """Load all PDFs from folder"""
        documents = []
        for file in os.listdir(folder_path):
            if file.endswith('.pdf'):
                path = os.path.join(folder_path, file)
                reader = PdfReader(path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                documents.append({
                    'text': text,
                    'metadata': {'id': file, 'source': file, 'type': 'pdf'}
                })
        return documents
    
    def load_markdown(self, folder_path):
        """Load all markdown files"""
        documents = []
        for file in os.listdir(folder_path):
            if file.endswith('.md'):
                path = os.path.join(folder_path, file)
                with open(path, 'r', encoding='utf-8') as f:
                    text = f.read()
                documents.append({
                    'text': text,
                    'metadata': {'id': file, 'source': file, 'type': 'markdown'}
                })
        return documents