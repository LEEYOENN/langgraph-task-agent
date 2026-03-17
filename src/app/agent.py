from typing import Annotated, TypedDict, Literal, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, BaseMessage, SystemMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from pathlib import Path 
from src.app.prompts import INVESTMENT_ANALYSIS_PROMPT
from src.app.tools import retrieve_docs, search_news
# 환경변수 불러오기
load_dotenv()
current_path = Path(__file__).resolve()
PROJECT_ROOT = current_path.parent.parent.parent

# === 그래프 상태 정의 ===
class GraphState(TypedDict):
    # 대화 기록 (Langraph가 자동으로 append 처리)
    messages: Annotated[List[BaseMessage], add_messages] # 대화 기록
    # 에이전트 현재 작업 상태 조건 분기 용
    status: Literal["search_doc", "search_web", "generate_report", "error", "done"]
    
    target_company: str # 투자 분석할 기업 명
    rag_context: str # 
    web_search_results: str 
    


# === Agent Class ===
class InvestmentAnalysisAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
        self.graph = self._build_graph()
    
    # --- node 함수 ---
    def _retrieve_node(self, state: GraphState) -> dict:
        """내부 문서(PDF) RAG 검색 노드"""
        
        print(f"▶ [Node] 문서 검색 중... 대상: {state['target_company']}")

        # rag tool 연동
        context = retrieve_docs(f"{state['target_company']}의 최근 실적을 알려줘")

        # graph state 업데이트
        return {
            "rag_context": context,
            "status": "search_web",
            "messages": [SystemMessage(content="내부 문서 검색(RAG)를 완료했습니다.")]
        }
    
    def _search_web_node(self, state: GraphState) -> dict:
        """최신 뉴스 웹 검색 노드"""

        print(f"▶ [Node] 웹 검색 중... 대상: {state['target_company']}")

        # 검색 툴 연동 (DuckDuckGo)
        news = search_news(f"{state['target_company']} 투자 리스크")

        return {
            "web_search_results": news,
            "status": "generate_report",
            "messages": [SystemMessage(content="웹 검색을 완료했습니다.")]
        }
    
    def _generate_node(self, state: GraphState):
        """최종 리포트 생성 노드"""
        print("▶ [Node] 최종 리포트 생성 중...")

        prompt = ChatPromptTemplate.from_messages([
            ("system", INVESTMENT_ANALYSIS_PROMPT),
            ("placeholder", "{messages}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "target_company": state["target_company"],
            "rag_context": state["rag_context"],
            "web_search_results": state["web_search_results"],
            "messages": state["messages"]
        })

        return {
            "status": "done",
            "messages": [response]
        }
    
    # --- 조건부 라우팅 함수 ---
    def _router(self, state: GraphState) -> str:
        """현재의 status에 따라 다음 노드를 결정합니다."""
        status = state["status"]
        if status == "search_web":
            return "search_web_node"
        elif status == "generate_report":
            return "generate_node"
        elif status == "done":
            return END
        else:
            return END 
        
    def _build_graph(self):
        graph_builder = StateGraph(GraphState)

        # 노드 등록
        graph_builder.add_node("retrieve_node", self._retrieve_node)
        graph_builder.add_node("search_web_node", self._search_web_node)
        graph_builder.add_node("generate_node", self._generate_node)

        # 흐름 연결 (조건부 라우팅 적용)
        graph_builder.add_edge(START, "retrieve_node")
        graph_builder.add_conditional_edges("retrieve_node", self._router)
        graph_builder.add_conditional_edges("search_web_node", self._router)
        graph_builder.add_conditional_edges("generate_node", self._router)

        return graph_builder.compile()
    
    # 외부 실행 인터페이스
    def run(self, company_name: str, query: str):
        """FastAPI 등 외부에서 에이전트를 실행할 때 호출하는 메서드"""
        initial_state = {
            "target_company": company_name,
            "messages": [HumanMessage(content=query)],
            "status": "search_doc",
            "rag_context": "",
            "web_search_results": ""
        }

        # 그래프 실행
        result = self.graph.invoke(initial_state)
        
        # 최종 메시지(리포트 내용) 반환
        return result["messages"][-1].content