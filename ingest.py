from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()


def ingest_documents():
    print("Loading PDFs from documents folder...")

    documents = []
    for filename in os.listdir("documents"):
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(f"documents/{filename}")
            documents.extend(loader.load())
            print(f"   Loaded: {filename}")

    if not documents:
        print("No PDFs found in documents folder!")
        return

    print("Splitting documents into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)
    print(f"   Created {len(chunks)} chunks")

    print("Creating embeddings and saving to FAISS...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local("faiss_index")
    print("   Saved to faiss_index folder!")
    print("Ingestion complete! Your documents are ready.")


if __name__ == "__main__":
    ingest_documents()