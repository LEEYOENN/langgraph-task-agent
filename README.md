# 📊 Clush AI Agent 과제: 상장사 투자 정보 분석 에이전트

본 프로젝트는 Clush의 기업 고객(금융권 등)이 필요로 하는 상장사 투자 위험 요소 및 비즈니스 동향을 자동으로 분석하는 LangGraph 기반의 AI 에이전트입니다. 내부 문서(RAG)와 최신 웹 검색을 교차 검증하여 신뢰도 높은 리포트를 생성합니다.

## 1. 자신이 개발한 Agent에 대한 설명
단순한 Chain 구조가 아닌, **LangGraph의 상태(State) 기반 라우팅**을 적용한 Stateful 에이전트입니다.
* **Workflow**: `[사용자 질문]` ➡️ `[PDF RAG 검색]` ➡️ `[DuckDuckGo 실시간 웹 검색]` ➡️ `[최종 마크다운 리포트 생성]`
* 내부 문서에 없는 최신 트렌드를 웹 검색 툴을 통해 보완하여 Hallucination(환각)을 최소화했습니다.
* **가산점 항목 충족**: FastAPI와 순수 HTML/JS를 활용하여 웹 개발 과제와 세트로 구성 (UI 제공).

## 2. 소스 빌드 및 실행 방법 메뉴얼
본 프로젝트는 Python 3.11+ 환경 및 패키지 매니저 `uv`를 기준으로 작성되었습니다.

### 기초 데이터 (필수)
* `src/data/sample_report.pdf` 파일이 위치해야 합니다. (실행 시 이 PDF를 읽어 ChromaDB를 초기화합니다.)

### 실행 순서
1. 레포지토리 클론 및 폴더 이동
2. 패키지 설치: `uv add fastapi uvicorn sqlalchemy pydantic langchain-openai langchain-chroma langchain-text-splitters pypdf duckduckgo-search langgraph`
3. 서버 실행: `uv run uvicorn src.app.main:app --reload`
4. 웹 UI 접속: 브라우저에서 `http://127.0.0.1:8000` 접속 후 에이전트 테스트

### DB 스키마 안내 (SQLite)
서버 실행 시 자동으로 `ir_agent.db` 및 `analysis_tasks` 테이블이 생성됩니다.
* `id` (PK), `task_id` (UUID, 고유 작업 ID)
* `target_name` (분석 대상 기업명), `status` (PENDING, IN_PROGRESS, COMPLETED, ERROR)
* `result_text` (최종 생성 리포트), `created_at` (요청 시간)

## 3. API Key 입력 등에 대한 가이드
루트 디렉토리에 `.env` 파일을 생성하고 아래와 같이 OpenAI API Key를 기입해야 정상 동작합니다.

```env
OPENAI_API_KEY="sk-proj-본인의_오픈AI_키를_여기에_입력하세요"