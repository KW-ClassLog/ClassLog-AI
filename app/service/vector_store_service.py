from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from app.service.vector_meta_service import VECTOR_DIR
import os

# lecture_id, 강의 내용 텍스트 저장 함수
def save_vectorstore(lecture_id: str, text: str, api_key: str):
    os.makedirs(os.path.join(VECTOR_DIR, lecture_id), exist_ok=True)

    documents = [Document(page_content=chunk) for chunk in text.split("\n\n") if chunk.strip()]
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)

    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local(os.path.join(VECTOR_DIR, lecture_id))


def load_vectorstore(lecture_id: str, api_key: str) -> FAISS:
    path = os.path.join(VECTOR_DIR, lecture_id)
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    return FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)

def vectorstore_exists(lecture_id: str) -> bool:
    base = os.path.join(VECTOR_DIR, lecture_id)
    faiss_idx      = os.path.join(base, "index.faiss")
    pkl            = os.path.join(base, "index.pkl")
    docstore_json  = os.path.join(base, "docstore.json")
    index_json     = os.path.join(base, "index.json")

    ok = (
        os.path.isdir(base) and
        os.path.isfile(faiss_idx) and
        (os.path.isfile(pkl) or os.path.isfile(docstore_json) or os.path.isfile(index_json))
    )
    
    return ok