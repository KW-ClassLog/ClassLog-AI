from app.service.vector_store_service import load_vectorstore
from app.prompt.quiz_generation_prompt import make_quiz_prompt
from app.core.memory import QuizMemory

from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

try:
    from langchain.retrievers.multi_query import MultiQueryRetriever
except Exception:
    from langchain_experimental.retrievers import MultiQueryRetriever

# 멀티 쿼리 한국어 커스터마이징
MULTI_QUERY_PROMPT = PromptTemplate.from_template(
    """당신은 정보 검색 전문가입니다. 아래 입력을 다양한 관점으로 재작성하여
    검색 커버리지를 넓히세요. 핵심 키워드는 보존하되 표현을 달리한 4~6개의
    한국어 검색 질의를 만드세요. 각 질의는 한 줄로 출력하세요.

    입력: {question}
    출력(각 줄에 한 질의):"""
)

def generate_quiz_with_rag(
    lecture_id: str,
    memory: QuizMemory,
    api_key: str,
    model: str = "gpt-4o",
    audio_present: bool = False,
) -> str:
    
    llm = ChatOpenAI(model_name=model, openai_api_key=api_key, temperature=0)
    vectorstore = load_vectorstore(lecture_id, api_key)

    base_retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 8,
            "fetch_k": 40,
            "lambda_mult": 0.7,
        },
    )

    try:
        retriever = MultiQueryRetriever.from_llm(
            retriever=base_retriever,
            llm=llm,
            prompt=MULTI_QUERY_PROMPT,
        )
    except Exception:
        retriever = base_retriever

    prompt = make_quiz_prompt(memory=memory, audio_present=audio_present)

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        return_source_documents=False,
        chain_type_kwargs={"prompt": prompt},
    )

    query_for_retrieval = (    
        "강의의 핵심 개념·정의·공식·절차·예시를 바탕으로 퀴즈 제작에 필요한 "
        "핵심 정보를 회수하세요."
    )

    result = qa.run(query_for_retrieval)

    print("====퀴즈 응답====")
    print(result)

    return result