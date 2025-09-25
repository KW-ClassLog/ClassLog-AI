import os
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

from app.prompt.multi_query_prompt import MULTI_QUERY_PROMPT


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
            "k": 12,
            "fetch_k": 120,
            "lambda_mult": 0.5,
        },
    )

    try:
        mq_llm = ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=api_key, temperature=0)
        retriever = MultiQueryRetriever.from_llm(
            retriever=base_retriever,
            llm=mq_llm,
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
        "강의자료에서 개념 정의, 핵심 용어, 배경/맥락, 비교/대조, 절차/방법, 예시/사례, "
        "자주 틀리는 포인트를 폭넓게 찾아 퀴즈 재료로 사용할 부분을 수집해 주세요."
    )

    if os.getenv("DEBUG_RETRIEVE") == "1":
        try:
            docs = retriever.invoke(query_for_retrieval)
        except Exception:
            docs = vectorstore.similarity_search(query_for_retrieval, k=12)

        print(f"[DEBUG] retrieved {len(docs)} docs")
        seen = set()
        for i, d in enumerate(docs[:12]):
            src = d.metadata.get("source", "?")
            body = (d.page_content or "")
            preview = body[:160].replace("\n", " ")
            is_dup = " DUP" if preview in seen else ""
            seen.add(preview)
            print(f"[RET{i:02d}] src={src} len={len(body)}{is_dup} | {preview}")


    result = qa.run(query_for_retrieval)
    print("====퀴즈 응답====")
    print(result)
    return result