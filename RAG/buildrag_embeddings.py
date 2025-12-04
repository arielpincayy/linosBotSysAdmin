from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

# --- 1. Cargar PDF ---
loader = PyPDFLoader("RAG/Bash Script.pdf")
docs = loader.load_and_split()

# --- 2. Crear embeddings ---
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# --- 3. Crear vector store ---
vectordb = Chroma.from_documents(docs, embedding=embeddings, persist_directory="./vectors/vectores_sysadmin_bashscript")
vectordb.persist()

print("Vector store creado y guardado.")