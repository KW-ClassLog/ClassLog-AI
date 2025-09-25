from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.service.vector_meta_service import VECTOR_DIR
import os

EMB_MODEL = os.getenv("OPENAI_EMBED_MODEL") or "text-embedding-3-large"

def _embeddings(api_key: str) -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model=EMB_MODEL, openai_api_key=api_key)

def _split_text(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=160, separators=["\n\n", "\n", " ", ""]
    )
    return splitter.split_text(text)

# lecture_id, 강의 내용 텍스트 저장 함수
def save_vectorstore(lecture_id: str, text: str, api_key: str):
    base = os.path.join(VECTOR_DIR, lecture_id)
    os.makedirs(base, exist_ok=True)
    chunks = [c for c in _split_text(text) if c.strip()]
    docs = [Document(page_content=c) for c in chunks]
    emb = _embeddings(api_key)
    vs = FAISS.from_documents(docs, emb, normalize_L2=True)
    vs.save_local(base)

def load_vectorstore(lecture_id: str, api_key: str) -> FAISS:
    base = os.path.join(VECTOR_DIR, lecture_id)
    emb = _embeddings(api_key)
    vs = FAISS.load_local(base, emb, allow_dangerous_deserialization=True)

    try:
        embed_dim = len(emb.embed_query("probe"))
        index_dim = getattr(vs.index, "d", None)
        if os.getenv("REINDEX_ON_LOAD") == "1" or (index_dim and index_dim != embed_dim):
            texts, metas = [], []
            for _id, doc in getattr(vs.docstore, "_dict", {}).items():
                texts.append(doc.page_content)
                metas.append(doc.metadata)
            new_vs = FAISS.from_texts(texts, emb, metadatas=metas, normalize_L2=True)
            new_vs.save_local(base)
            vs = new_vs
    except Exception:
        pass
    return vs

def vectorstore_exists(lecture_id: str) -> bool:
    base = os.path.join(VECTOR_DIR, lecture_id)
    faiss_idx = os.path.join(base, "index.faiss")
    pkl       = os.path.join(base, "index.pkl")
    doc_json  = os.path.join(base, "docstore.json")
    idx_json  = os.path.join(base, "index.json")
    return (
        os.path.isdir(base) and
        os.path.isfile(faiss_idx) and
        (os.path.isfile(pkl) or os.path.isfile(doc_json) or os.path.isfile(idx_json))
    )