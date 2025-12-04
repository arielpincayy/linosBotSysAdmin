from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_classic.retrievers import EnsembleRetriever


def rag_configuration():
    print(" Cargando embeddings y vector store...")
    
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    # DB 1 – Sysadmin general
    vectordb1 = Chroma(
        persist_directory="./vectors/vectores_sysadmin",
        embedding_function=embeddings
    )

    # DB 2 – Redes Linux
    vectordb2 = Chroma(
        persist_directory="./vectors/vectores_sysadmin_network",
        embedding_function=embeddings
    )

    # DB 3 – Bash Script
    vectordb3 = Chroma(
        persist_directory="./vectors/vectores_sysadmin_bashscript",
        embedding_function=embeddings
    )

    retriever1 = vectordb1.as_retriever(search_kwargs={"k": 3})
    retriever2 = vectordb2.as_retriever(search_kwargs={"k": 3})
    retriever3 = vectordb3.as_retriever(search_kwargs={"k": 3})

    # COMBINAR AMBOS
    retriever = EnsembleRetriever(
        retrievers=[retriever1, retriever2, retriever3],
        weights=[1/3, 1/3, 1/3]   # Puedes ajustar importancia
    )
    
    return retriever