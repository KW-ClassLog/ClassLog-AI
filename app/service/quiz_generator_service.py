from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI  
from app.service.vector_store_service import load_vectorstore
from app.prompt.quiz_generation_prompt import make_quiz_prompt
from app.core.memory import QuizMemory

def generate_quiz_with_rag(
    lecture_id: str,
    memory: QuizMemory,
    api_key: str,
    model: str = "gpt-4o",
    audio_present: bool = False,
) -> str:
    
    vectorstore = load_vectorstore(lecture_id, api_key)
    retriever = vectorstore.as_retriever(k=4)

    prompt = make_quiz_prompt(memory=memory, audio_present=audio_present)

    llm = ChatOpenAI(model_name=model, openai_api_key=api_key)
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        return_source_documents=False,
        chain_type_kwargs={"prompt": prompt},
    )

    question = "위 지침에 따라 새로운 퀴즈(객관식 2, 단답형 1, OX 1)를 생성해 주세요."
    result = qa.run(question)

    print("==== 퀴즈 응답 ====")
    print(result)

    return result