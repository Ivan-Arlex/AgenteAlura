import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
RUTA_FAISS = BASE_DIR / "faiss_index"
MODELO_EMBEDDING = os.getenv("MODELO_EMBEDDING", "gemini-embedding-001")
gemini_api_key = os.getenv("GEMINI_API_KEY")


def obtener_vector_store():
    """Lee los archivos de la carpeta docs (PDF y Excel) y los corta en fragmentos/chunks
    ."""
    docs = []
    BASE_DIR = Path(__file__).resolve().parent
    carpeta_docs = Path(BASE_DIR, "docs")

    print("Ruta docs:", carpeta_docs)
    print("Existe:", carpeta_docs.exists())

    for archivo in carpeta_docs.glob("*.*"):
        extension = archivo.suffix.lower()
        try:
            if extension == ".pdf":
                loader = PyMuPDFLoader(str(archivo))
                docs.extend(loader.load())
                print(f"PDF procesado: {archivo.name}")
                
            elif extension in [".xlsx", ".xls"]:
                df = pd.read_excel(archivo)
                
                filas_por_chunk = 15
                for i in range(0, len(df), filas_por_chunk):
                    bloque = df.iloc[i : i + filas_por_chunk]
                    texto_tabla = bloque.to_string(index=False)
                    
                    doc_excel = Document(
                        page_content=f"Inventario de Productos BimBam Buy:\n\n{texto_tabla}",
                        metadata={"source": archivo.name}
                    )
                    docs.append(doc_excel)
                    
                print(f"Excel procesado limpiamente: {archivo.name}")

        except Exception as e:
            print(f"Error procesando {archivo.name}: {e}")

    if not docs:
        print("No se encontraron documentos válidos en la carpeta 'docs'.")
        return None

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2500, chunk_overlap=250)
    chunks = text_splitter.split_documents(docs)
    print(f"Total de chunks creados: {len(chunks)}")
    return chunks


def procesar_vector_store():
    """
    Instancia el modelo de embedding. 
    Carga el índice FAISS si ya existe localmente; de lo contrario, lo construye desde cero.
    """

    try:

        embeddings = GoogleGenerativeAIEmbeddings(model=MODELO_EMBEDDING, google_api_key=gemini_api_key)
        
        if os.path.exists(RUTA_FAISS):
            print("Base de datos FAISS encontrada. Cargando vectores de forma instantánea...")
        
            vector_store = FAISS.load_local(RUTA_FAISS, embeddings, allow_dangerous_deserialization=True)
            return vector_store
        
        print("No se encontró una base de datos previa. Construyendo nuevo vector store...")
        chunks = obtener_vector_store()
        
        if not chunks:
            print("No se pudieron generar chunks. Revisa que la carpeta 'docs' tenga archivos válidos.")
            return None

        vector_store = FAISS.from_documents(chunks, embeddings)
        vector_store.save_local(RUTA_FAISS)
        print(f"¡Nueva base de datos FAISS guardada con éxito en '{RUTA_FAISS}'!")
        
        return vector_store
    
    except Exception as e:
        print(f"Error al procesar el vector store: {e}")
        return None