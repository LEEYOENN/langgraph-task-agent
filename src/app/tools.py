import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

# 1. 웹 검색 툴 (DuckDuckGo - API Key 불필요)
def search_news(query: str) -> str:
    """최신 뉴스 및 정보를 웹에서 검색하여 문자열로 반환합니다."""
    try:
        # 한국 지역 설정, 최근 한달 정보, 상위 5개의 결과만 가져옵니다.
        wrapper = DuckDuckGoSearchAPIWrapper(region="kr-kr", time="m", max_results=5)
        search = DuckDuckGoSearchResults(api_wrapper=wrapper)
        results = search.run(query)
        return results
    except Exception as e:
        return f"검색 중 오류 발생: {e}"
    

# 2. RAG 기반 내부 문서 검색 툴 (PDF -> ChromaDB)
VECTOR_STORE_DIR = "./chroma.db"

def init_vector_db():
    """
    PDF를 읽어 Vector DB를 초기화하는 함수. 
    (FastAPI 서버 시작 시 한 번만 실행되도록 main.py에서 호출합니다.)
    """
    if os.path.exists(VECTOR_STORE_DIR):
        print("이미 Vector DB가 존재합니다. 초기화를 건너뜁니다.")
        return
    
    print("VectorDB 초기화 중(PDF embedding)")

    pdf_path = "src/data/[미래에셋증권]_2025_4Q_실적보고서.pdf"

    if not os.path.exists(pdf_path):
        print(f"경고: pdf 파일이 존재하지 않아 VectorDB를 생성하지 못했습니다.")
        return
    
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    # chunking
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    split_docs = text_splitter.split_documents(docs)

    # OpenAI 임베딩 사용해 로컬 디렉토리에 영구 저장
    Chroma.from_documents(
        documents=split_docs,
        embedding=OpenAIEmbeddings(),
        persist_directory=VECTOR_STORE_DIR
    )

    print("Vector DB 세팅 완료")

def retrieve_docs(query: str) -> str:
    """Vector DB에서 쿼리와 가장 유사한 문서를 찾아 반환합니다."""
    if not os.path.exists(VECTOR_STORE_DIR):
        return "관련 내부 문서를 찾을 수 없습니다. (DB 미초기화)"
    
    vectorstore = Chroma(
        persist_directory=VECTOR_STORE_DIR,
        embedding_function=OpenAIEmbeddings()
    )

    # 상위 3개의 관련 청크만 가져오도록 설정
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(query)

    if not docs:
        return "관련된 내부 문서를 찾을 수 없습니다."
    
    # 검색된 내부 문서들을 하나로 합쳐서 반환
    return "\n\n".join([doc.page_content for doc in docs])