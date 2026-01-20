import os
import shutil
import time
from typing import List

# Loaders
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.documents import Document

# --- CONFIGURATION ---
# Base directory is the folder containing 'app' and 'resources'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "resources")
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Allowed Departments (Must match folder names exactly)
VALID_DEPARTMENTS = {"Finance", "HR", "Engineering", "Marketing", "General"}

def load_documents() -> List[Document]:
    """
    Recursively scans the 'resources' folder for PDF, CSV, TXT, and MD files.
    Tags them with the correct Department metadata.
    """
    print(f"🔍 SEARCHING FOR DATA IN: {DATA_PATH}")
    if not os.path.exists(DATA_PATH):
        print(f"❌ CRITICAL ERROR: '{DATA_PATH}' not found.")
        return []

    documents = []
    
    # Walk through ALL directories (Recursive Search)
    for root, dirs, files in os.walk(DATA_PATH):
        # Check if we are inside a valid Department folder
        path_parts = os.path.normpath(root).split(os.sep)
        
        current_dept = None
        for dept in VALID_DEPARTMENTS:
            if dept in path_parts:
                current_dept = dept
                break
        
        # Only process files if they belong to a valid Department
        if current_dept:
            print(f"   📂 Scanning folder in '{current_dept}': {root}")
            for file in files:
                if file.startswith("."): continue 
                
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                try:
                    loader = None
                    if file_ext == ".pdf":
                        loader = PyPDFLoader(file_path)
                    elif file_ext == ".csv":
                        loader = CSVLoader(file_path) 
                    elif file_ext in [".txt", ".md"]:
                        loader = TextLoader(file_path, encoding="utf-8")
                    
                    if loader:
                        print(f"      📄 Loading: {file}")
                        loaded_docs = loader.load()
                        
                        # TAGGING: The Critical Security Step
                        for doc in loaded_docs:
                            doc.metadata["department"] = current_dept
                            doc.metadata["source"] = file
                        
                        documents.extend(loaded_docs)
                except Exception as e:
                    print(f"      ⚠️ Error loading {file}: {e}")

    return documents

def add_to_chroma(chunks: List[Document]):
    """
    Deletes the old database and creates a new one with the fresh data.
    """
    # 1. Clear old DB (With Error Handling for Windows)
    if os.path.exists(CHROMA_PATH):
        try:
            shutil.rmtree(CHROMA_PATH)
            print(f"   🗑️  Deleted old database at {CHROMA_PATH}")
            time.sleep(1) # Wait for Windows to release the lock
        except PermissionError:
            print(f"   ⚠️  COULD NOT DELETE '{CHROMA_PATH}' AUTOMATICALLY.")
            print("   🔒 The folder is locked by another process (likely the server).")
            print("   👉 ACTION: Please manually delete the 'chroma_db' folder and run this script again.")
            return

    # 2. Create new DB
    print("   🚀 Generating Embeddings... (This may take 1-2 minutes)")
    embedding_function = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL)
    
    db = Chroma.from_documents(
        chunks, 
        embedding_function, 
        persist_directory=CHROMA_PATH
    )
    print(f"   💾 Saved {len(chunks)} chunks to ChromaDB.")

if __name__ == "__main__":
    print("--- STARTING INGESTION ---")
    docs = load_documents()
    if docs:
        print(f"   ✅ Found {len(docs)} documents.")
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(docs)
        
        add_to_chroma(chunks)
        print("--- INGESTION COMPLETE ---")
    else:
        print("❌ FAILURE: No documents found. Check your 'resources' folder structure!")
        