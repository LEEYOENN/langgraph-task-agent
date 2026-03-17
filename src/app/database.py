import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

# sqlite 데이터 베이스 파일 경로 설정 (루트 밑에 생성됨)
SQLALCHEMY_DATABASE_URL = "sqlite:///./task_agent.db"

engine  = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autoflush=False, bind=engine)

Base = declarative_base()

# 금융 리포트 분석 B 스키마 정의
class AnalysisTask(Base):
    __tablename__ = "analysis_task"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    target_name = Column(String, index=True) # 분석 대상
    status = Column(String, default="PENDING") # PENDING, IN_PROGRESS, COMPLETED, ERROR
    result_text = Column(Text, nullable=True) # 에이전트가 작성한 최종 분석 결과
    error_message = Column(Text, nullable=True) # 실패시 에러 로깅용
    created_at = Column(DateTime, default=datetime.now)

# 테이블 초기화 함수
def init_db():
    """
    정의된 스키마를 바탕으로 데이터베이스와 테이블 생성
    이미 존재하면 유지
    """
    Base.metadata.create_all(bind=engine)

# DB 세션 제너레이터
def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()


