from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.app.database import init_db, get_db
from src.app.tools import init_vector_db
from src.app.schemas import AnalysisRequest, AnalysisResponse
from src.app.service import InvestmentAnalysisService
from pathlib import Path
import os

current_path = Path(__file__).resolve()
PROJECT_ROOT = current_path.parent.parent.parent

# 서버 시작 시 무조건 실행될 수 있도록 lifespan 설정
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=== 서버 부팅: DB 및 Vector DB 초기화 시작 ===")
    # 서버 켜질 때 실행
    init_db()
    init_vector_db()
    print("초기화 완료")
    yield
    print("서버 종료")

app = FastAPI(title="AI IR Analysis Agent API", lifespan=lifespan)

# 정적 파일(웹 UI) 서빙 설정
static_dir = os.path.join(PROJECT_ROOT, "src", "static")
os.makedirs(static_dir, exist_ok=True) 
app.mount("/static", StaticFiles(directory=static_dir), name="static")

service = InvestmentAnalysisService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.post("/api/analyze", response_model=AnalysisResponse)
def analyze_company(request: AnalysisRequest, db: Session = Depends(get_db)):
    """
    기업 투자 분석 에이전트를 실행합니다.
    (MVP 제출을 위해 동기 블로킹 방식으로 구현됨)
    """
    result = service.run_analysis(
        db=db,
        target_company=request.target_company,
        user_query=request.user_query
    )
    return result

