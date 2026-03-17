# 📊 Clush AI Agent 과제: 상장사 투자 정보 분석 에이전트
![843DFB2F-FFB9-4C94-9011-F2724214BD7D_1_201_a](https://github.com/user-attachments/assets/d65d9f29-1231-48e1-8839-dc47eabc4a69)

본 프로젝트는 Clush의 기업 고객(금융권 등)이 필요로 할 만한 상장사 투자 위험 요소 및 비즈니스 동향을 자동으로 분석하는 LangGraph 기반의 AI 에이전트입니다. 내부 문서(RAG)와 최신 웹 검색을 교차 검증하여 신뢰도 높은 리포트를 생성합니다.

## 1. 자신이 개발한 Agent에 대한 설명
단순한 Chain 구조가 아닌, **LangGraph의 상태(State) 기반 라우팅**을 적용한 Stateful 투자 정보 분석 에이전트입니다.
* **Workflow**: `[사용자 질문]` ➡️ `[PDF RAG 검색]` ➡️ `[DuckDuckGo 실시간 웹 검색]` ➡️ `[최종 마크다운 리포트 생성]`
* 내부 문서에 없는 최신 트렌드를 웹 검색 툴을 통해 보완하여 Hallucination(환각)을 최소화했습니다.
* **백엔드 서버와 UI 제공**: FastAPI와 순수 HTML/JS를 활용하여 구현했습니다.
* **DB 스키마 안내 (SQLite)**: 서버 실행 시 자동으로 `task_agent.db` 및 `analysis_tasks` 테이블이 생성됩니다.
  * `id` (PK), `task_id` (UUID, 고유 작업 ID)
  * `target_name` (분석 대상 기업명), `status` (PENDING, IN_PROGRESS, COMPLETED, ERROR)
  * `result_text` (최종 생성 마크다운 리포트), `created_at` (요청 시간)


## 2. API Key 입력 등에 대한 가이드
루트 디렉토리에 `.env` 파일을 생성하고 아래와 같이 OpenAI API Key를 기입해야 정상 동작합니다.

```env
OPENAI_API_KEY="sk-proj-본인의_오픈AI_키를_여기에_입력하세요"
```

## 3. 소스 빌드 및 실행 방법 매뉴얼

본 프로젝트는 Python 3.11+ 환경에서 개발되었습니다. 
평가자의 환경에 맞게 **표준 패키지 매니저(pip)**를 사용하는 방법과, **고속 패키지 매니저(uv)**를 사용하는 방법 두 가지를 모두 제공합니다. 편하신 방법으로 실행해 주세요.

### 📂 기초 데이터 세팅 (필수)
* 프로젝트 루트 기준 `src/data/` 폴더 내에 `[미래에셋증권]_2025_4Q_실적보고서.pdf`파일이 존재하는지 확인해 주세요. 
* 서버 최초 실행 시 이 PDF를 읽어 Vector DB(ChromaDB)를 자동 초기화합니다.

### 🚀 방법 A: 일반적인 표준 실행 방법 (pip 권장)
가장 보편적인 파이썬 환경 실행 방법입니다.

**1. 레포지토리 클론 및 폴더 이동**
```bash
git clone https://github.com/LEEYOENN/langgraph-task-agent
cd [clone된 프로젝트 루트 위치]
```

**2. 가상환경 생성 및 활성화**
```bash
# Mac/Linux
python -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

**3. 패키지 설치**
```bash
pip install -r requirements.txt
```

**4. 서버 실행**
```bash
# 루트 디렉토리에서 아래 명령어 실행
uvicorn src.app.main:app --reload
```

----

### ⚡ 방법 B: 고속 실행 방법 (uv 사용 시)
Rust 기반의 초고속 패키지 매니저인 `uv`가 설치되어 있다면 훨씬 빠르게 세팅할 수 있습니다.

**1. uv 설치 (미설치된 경우)**
```bash
# Mac/Linux
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"
```

**2. 패키지 동기화 및 실행**
```bash
# 가상환경 생성 및 의존성 설치를 동시에 수행
uv sync

# 서버 실행
uv run uvicorn src.app.main:app --reload
```

---

### 🌐 웹 UI 테스트 방법
* 서버가 정상적으로 실행되면(기본 포트 8000), 브라우저를 열고 `http://127.0.0.1:8000/` 로 접속합니다.
* 화면에 나타난 입력 폼을 통해 에이전트의 문서 분석 및 RAG 연계 동작을 직접 테스트하실 수 있습니다.
* 현재는 RAG를 위한 더미용 실적보고서 PDF가 '미래에셋증권'의 파일만 들어가 있어 분석 대상 기업명
은 바꾸지 않으시는 걸 권장드립니다.

## 4. 주력으로 사용한 라이브러리 및 사용 이유
* **FastAPI**: 비동기 처리에 강하고 Pydantic을 통한 DTO 검증이 뛰어나 백엔드 API 및 정적 UI 서빙을 위해 채택했습니다.
* **LangGraph**: 단순 프롬프트 체이닝을 넘어, 향후 에러 처리나 사람의 개입(Human-in-the-loop) 등 복잡한 워크플로우로 확장하기 위해 명시적인 상태 관리 도구로 사용했습니다.
* **ChromaDB & PyPDF**: 가볍고 빠르게 로컬 벡터 저장소를 구축하여 RAG 파이프라인을 구현하기 위해 사용했습니다.
* **DuckDuckGo Search**: 별도의 API Key 발급 없이 즉각적으로 최신 뉴스와 트렌드를 검색하여 에이전트의 도구(Tool)로 활용하기 위해 채택했습니다.

## 5. 향후 최적화와 서비스 확장 방향
제한된 과제 시간 내에 MVP 형태로 구현하였으나, 실제 프로덕션 환경 도입을 위해 다음과 같은 아키텍처 고도화를 계획하고 있습니다.

* **RAG 파이프라인 및 문서 전처리 고도화 (멀티모달 적용)**
  * 현재의 단순 텍스트 Chunking 방식을 넘어, 재무 제표나 IR 리포트에 자주 등장하는 **표(Table), 그래프, 이미지**를 정확히 해석하기 위해 `Unstructured.io` 등의 파서를 도입하고 Multi-Vector 검색 전략을 적용할 예정입니다.
* **Supervisor 기반 Multi-Agent 시스템 도입**
  * 현재의 단일 파이프라인 흐름을 발전시켜, '검색 담당', '재무 데이터 분석 담당', '보고서 작성 담당' 에이전트를 분리하고 이를 **Supervisor 에이전트**가 총괄하도록 LangGraph 아키텍처를 재설계하여 복잡한 추론 능력을 극대화하겠습니다.
* **비동기(Async) 백엔드 처리 및 MLOps 인프라**
  * 에이전트의 구동 시간이 길어질 경우를 대비해, FastAPI의 백그라운드 태스크나 Redis/Celery 기반의 비동기 메세지 큐 시스템으로 전환하여 서버 블로킹 현상을 방지하고 시스템 안정성을 확보하겠습니다.
* **클러쉬(Clush) 자사 솔루션과의 연계 (MCP 활용)**
  * 향후 Model Context Protocol(MCP) 서버를 구축하여, 본 에이전트가 클러쉬의 'WorkPlace(메신저)'나 'Readit Chat' 환경에서 사내 데이터베이스와 안전하게 통신하며 즉각적인 인사이트를 제공하는 비즈니스 자동화 모듈로 기능하도록 확장할 수 있습니다.
